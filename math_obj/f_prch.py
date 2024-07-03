import numpy as np
from working_with_files.config import Files_con


class F_prch_maker:
    """Собирает функцию правой части в зависимости от установленных моделей"""

    def __init__(self, fM, get_stand_atmo_data, get_TCxM, start_param):
        # self.fM = fM
        # self.get_stand_atmo_data = get_stand_atmo_data
        # self.get_TCxM = get_TCxM

        self.__start_param = start_param

        # Модели поля и атмосферы
        self.__grav_model = self.__models('grav')
        self.__atmo_model = self.__models('atmo')


        self.__f_prch = None
        self.__speed_comp = None
        self.__grav_accel = self.__gravitational_acceleration()
        self.__atmo_resist = self.__atmospheric_resistance()


    def __models(self, component):
        if component is 'grav':
            return self.__start_param[8]
        if component is 'atmo':
            return self.__start_param[9]

    def speed_component(self):
        """Скорость всегда берется из предыдущего шага интегрирования"""
        self.__speed_comp = lambda q: q[3:6]

    def __gravitational_acceleration(self):
        """Добавление гравитационного ускорения"""

        if self.__grav_model == 1:
            # Применяется модель центрального потенциального поля земли (простейшая)
            def grav_accel(q):
                r = np.array(q[:3])
                r_norm = np.linalg.norm(r)          # Это не нормировка, а получение нормы - модуля
                g = -self.fM * r / r_norm ** 3      # Поменять тут в будущем момент с self.fM
                return g
            return grav_accel
        else:
            pass



    def __atmospheric_resistance(self):
        """Добавление атмосферного сопротивления"""
        if self.__atmo_model == 0:
            # Применяется модель без атмосферы
            def atmo_resist(q_gr, V, h):
                Wa_ksi = np.zeros(3)
                return Wa_ksi
            return atmo_resist

        if self.__atmo_model == 1:
            # Применяется модель стандартной атмосферы
            def atmo_resist(q_gr, V, h):
                alpha = 20.046796
                if 0 < h < 10 ** 5:
                    h_l, ro_l, T_l = self.get_stand_atmo_data(h, up_or_down='down')
                    h_r, ro_r, T_r = self.get_stand_atmo_data(h, up_or_down='up')
                    ro = ro_l + ((ro_r - ro_l) / (h_r - h_l)) * (h - h_l)
                    T = T_l + ((T_r - T_l) / (h_r - h_l)) * (h - h_l)
                elif h <= 0:
                    h = 0
                    h, ro, T = self.get_stand_atmo_data(h, up_or_down=False)
                elif h >= 10 ** 5:
                    h = 10 ** 5
                    h, ro, T = self.get_stand_atmo_data(h, up_or_down=False)

                dP = ro * (V ** 2) / 2
                Cs = alpha * np.sqrt(T)
                M = V / Cs

                if 0.2 < M < 5.0:
                    M_l, Cxmin_l, Cxmax_l = self.get_TCxM(M, up_or_down='down')
                    M_r, Cxmin_r, Cxmax_r = self.get_TCxM(M, up_or_down='up')
                    Cxmin = Cxmin_l + ((Cxmin_r - Cxmin_l) / (M_r - M_l)) * (M - M_l)
                elif M <= 0.2:
                    M = 0.2
                    M, Cxmin, Cxmax = self.get_TCxM(M, up_or_down=False)
                elif M >= 5.0:
                    M = 5.0
                    M, Cxmin, Cxmax = self.get_TCxM(M, up_or_down=False)

                Wa = - ((Cxmin * 13.2) / 4000) * dP
                v_ksi_gr = np.array(q_gr[3:6])
                Wa_ksi_gr = Wa * v_ksi_gr / V
                return Wa_ksi_gr

            return atmo_resist

    def coriolis_centrifugal_forces(self):
        """Добавление кориолисовой и центробежной сил"""

        def coriolis_centrifugal(q_gr, Ω_vector):
            ksi_gr = np.array(q_gr[:3])
            v_ksi_gr = np.array(q_gr[3:6])
            W_c_gr = (Ω_vector[2] ** 2) * ksi_gr
            W_k = -2 * np.cross(Ω_vector, v_ksi_gr)
            return W_c_gr, W_k

        self.coriolis_centrifugal = coriolis_centrifugal

    @property
    def f_prch(self):
        """Возвращает значение настроенной функции правой части в виде np.ndarray"""
        if self.__f_prch is None:
            def f_prch(q, Ω, h):
                Ω_vector = np.array([0, 0, Ω])
                v_ksi_gr = np.array(q_gr[3:6])
                V = np.linalg.norm(v_ksi_gr)

                f_accel = np.zeros(3)
                if self.grav_accel is not None:
                    f_accel += self.__grav_accel(q)

                if hasattr(self, 'coriolis_centrifugal'):
                    W_c_gr, W_k = self.coriolis_centrifugal(q_gr, Ω_vector)
                    f_accel += W_c_gr + W_k

                if self.atmo_resist is not None:
                    f_accel += self.atmo_resist(q_gr, V, h)

                return np.concatenate((v_ksi_gr, f_accel, [1]))

            self.__f_prch = f_prch

        return self.__f_prch


# Пример использования
def get_stand_atmo_data(h, up_or_down):
    # Примерная реализация функции
    if up_or_down == 'down':
        return h, 1.225, 288.15
    elif up_or_down == 'up':
        return h, 0.9, 255.65
    else:
        return h, 0.0, 0.0


def get_TCxM(M, up_or_down):
    # Примерная реализация функции
    if up_or_down == 'down':
        return M, 0.1, 0.5
    elif up_or_down == 'up':
        return M, 0.3, 0.8
    else:
        return M, 0.2, 0.6


# Создание объекта класса с необходимыми параметрами
fM = 3.986e14  # Примерное значение гравитационного параметра Земли
f_maker = F_prch_maker(fM, get_stand_atmo_data, get_TCxM)

# Настройка компонентов
f_maker.speed_component()
f_maker.gravitational_acceleration()
f_maker.atmospheric_resistance()
f_maker.coriolis_centrifugal_forces()

# Вызов функции через созданный объект
q_gr = [7000, 0, 0, 0, 7.8, 0]  # Примерные начальные условия
Ω = 7.2921159e-5  # Угловая скорость вращения Земли
h = 300  # Высота над поверхностью Земли

result = f_maker.f_prch(q_gr, Ω, h)
print(result)
