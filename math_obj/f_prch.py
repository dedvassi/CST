import numpy as np
from working_with_files.datas_for_models import *
class F_prch_maker:
    """Собирает функцию правой части в зависимости от установленных моделей"""

    def __init__(self, grav_m: int, atmo_m: int, Cx_priority:int):
        self.__start_param = np.concatenate((np.array([grav_m]), np.array([atmo_m])))

        # Модели поля и атмосферы
        self.__grav_model = self.__models('grav')
        self.__atmo_model = self.__models('atmo')

        # Кэшируем данные из таблиц по атмосфере
        self.__atmo_cache = check_csv_file_atmo(self.__atmo_model, 1)
        self.__analysis_atmo = self.__analysis_atmo_cache()

        self.__Cx_cache = check_csv_file_TCxM(Cx_priority)
        self.__analysis_Cx = self.__analysis_Cx_cache()

        self.__f_prch = None
        self.__speed_comp = self.__speed_component()
        self.__grav_accel = self.__gravitational_acceleration()
        self.__aero_d_resist = self.__aerodynamics_resist()

    def __models(self, component):
        if component is 'grav':
            return self.__start_param[0]
        if component is 'atmo':
            return self.__start_param[1]

    def __speed_component(self):
        """Компоненты скорости с предыдущего шага"""
        def speed_comp(q):
            v = np.array(q[3:6])
            v_norm = np.linalg.norm(v)
            v_ort = v/v_norm
            return v, v_norm, v_ort
        return speed_comp

    def __gravitational_acceleration(self):
        """Добавление гравитационного ускорения"""
        if self.__grav_model == 0:
            def grav_accel(q):
                r = np.array(q[:3])
                r_norm = np.linalg.norm(r)
                g = -fM * r / r_norm ** 3
                return g
            return grav_accel
        else:
            self.__errors('initial_model_grav')

    def __aerodynamics_resist(self):
        """Добавление аэродинамики"""
        if self.__atmo_model == 0:
            # Применяется модель без атмосферы
            return None
        else:
            def aero_d_resist(ro, v_norm, v_ort, Cx, S_midotd, m_otd):
                dP = ro * (v_norm ** 2) / 2
                Wa = -((Cx * S_midotd) / m_otd) * dP # Коэф
                Wa_vector = Wa * v_ort  # вектор
                return Wa_vector
            return aero_d_resist

    def __analysis_atmo_cache(self):
        if self.__atmo_model == 0:
            # Модель без атмосферы
            def analysis_atmo(h):
                ro, T = (0, 0)
                return ro, T
            return analysis_atmo

        if self.__atmo_model == 1:
            # Стандартная модель атмосферы
            def analysis_atmo(h):
                h_values = sorted(self.__atmo_cache.keys())
                h_min = h_values[0]
                h_max = h_values[-1]

                if h <= h_min:
                    # Высота меньше минимальной из таблицы или совпадает с ней
                    h = h_min
                    ro, T = self.__atmo_cache[h]
                    return ro, T
                if h >= h_max:
                    # Высота превышает максимальную из таблицы или совпадает с ней
                    h = h_max
                    ro, T = self.__atmo_cache[h]
                    return ro, T
                else:
                    # Высота находится в пределах таблицы
                    if h in h_values:
                        # Высота находится в узле таблицы
                        ro, T = self.__atmo_cache[h]
                        return ro, T
                    else:
                        # Высота не находится в узле таблицы
                        h_l = None
                        h_r = None
                        for h_s in h_values:
                            if h_s < h:
                                h_l = h_s
                            if h_s > h and h_r is None:
                                h_r = h_s
                                break

                        ro_l, T_l = self.__atmo_cache[h_l]
                        ro_r, T_r = self.__atmo_cache[h_r]

                        ro = self.__line_interpolation(h, h_l, h_r, ro_l, ro_r)
                        T = self.__line_interpolation(h, h_l, h_r, T_l, T_r)

                        return ro, T

    def __analysis_Cx_cache(self):
        def analysis_Cx(v, T):
            # Скорость звук
            Cs = alpha * np.sqrt(T)
            # Махи
            M = v/Cs

            M_values = sorted(self.__Cx_cache.keys())
            M_min = M_values[0]
            M_max = M_values[-1]

            if M <= M_min:
                M = M_min
                Cx = self.__Cx_cache[M]
                return Cx

            if M >= M_max:
                M = M_max
                Cx = self.__Cx_cache[M]
                return Cx

            else:
                if M in M_values:
                    Cx = self.__Cx_cache[M]
                    return Cx
                else:
                    M_l = None
                    M_r = None

                    for M_s in M_values:
                        if M_s < M:
                            M_l = M_s
                        if M_s > M and M_r is None:
                            M_r = M_s
                    Cx_l = self.__Cx_cache[M_l]
                    Cx_r = self.__Cx_cache[M_r]

                    Cx = self.__line_interpolation(M, M_l, M_r, Cx_l, Cx_r)

                    return Cx

        return analysis_Cx




    @property
    def f_prch(self):
        if self.__f_prch is None:
            def f_prch(q, h):
                v, v_norm, v_ort = self.__speed_comp(q)
                f_accel = np.zeros(3)
                if self.__grav_accel is not None:
                    f_accel += self.__grav_accel(q)

                if self.__aero_d_resist is not None:
                    ro, T = self.__analysis_atmo(h)
                    Cx = self.__analysis_Cx(v, T)
                    f_accel += self.__aero_d_resist(ro, v_norm, v_ort, Cx, S_midotd, m_otd)
                return np.concatenate((v, f_accel, [1]))
            self.__f_prch = f_prch
        return self.__f_prch

    def __line_interpolation(self, x, x_l, x_r, y_l, y_r):
        y = y_l + (y_r - y_l) / (x_r - x_l) * (x - x_l)
        return y

    def __errors(self, type_err):
        if type_err is 'initial_model_grav':
            raise ValueError("Ошибка инициализации модели гравитационного поля\n"
                             "Функция не может быть сформирована.\n"
                             "Проверьте входные данные")
        if type_err is 'initial_model_atmo':
            raise ValueError("Ошибка инициализации модели атмосферы.\n"
                             "Функция не может быть сформирована.\n"
                             "Проверьте входные данные")
