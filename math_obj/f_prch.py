import numpy as np
from working_with_files.datas_for_models import *
class F_prch_maker:
    """Собирает функцию правой части в зависимости от установленных моделей"""

    def __init__(self, fM, get_stand_atmo_datar, get_TCxM, grav_m: int, atmo_m: int):
        self.__start_param = np.concatenate((np.array([grav_m]), np.array([atmo_m])))

        # Модели поля и атмосферы
        self.__grav_model = self.__models('grav')
        self.__atmo_model = self.__models('atmo')

        # Кэшируем данные из таблиц по атмосфере
        self.__atmo_cache = check_csv_file_atmo(self.__atmo_model)
        self.__analysis_atmo = self.__analysis_atmo_cache()

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
                r = np.array(q[1:3])
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
            def aero_d_resist(ro, T, v_norm, v_ort):
                Wa_vector = np.array([0, 0, 0])  # Для ясности того, что оно возвращает (на самом деле можно просто вернуть массив нулей)
                return Wa_vector
            return aero_d_resist
        else:
            def aero_d_resist(ro, v_norm, v_ort, Cx, S_midotd, m_otd):
                dP = ro * ((v_norm ** 2) / 2)
                Wa = -((Cx * S_midotd) / m_otd) * dP # Коэф
                Wa_vector = Wa * v_ort  # вектор
                return Wa_vector
            return aero_d_resist

    def __analysis_atmo_cache(self):
        if self.__atmo_model == 0:
            def analysis_atmo():
                ro, T = (0, 0)
                return ro, T
            return analysis_atmo
        if self.__atmo_model == 1:
            # Стандартная модель атмосферы
            pass

    @property
    def f_prch(self):
        if self.__f_prch is None:
            def f_prch(q):
                v, v_norm, v_ort = self.__speed_comp(q)
                f_accel = np.zeros(3)
                if self.__grav_accel is not None:
                    f_accel += self.__grav_accel(q)
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

a = F_prch_maker(1, 2, 3, 0, 5)
