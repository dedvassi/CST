import numpy as np

class Q_v_state():
    """
    Этот класс позволяет создавать и модифицировать вектор состояния q
    """
    def __init__(self, matrix,  start_param, *args, **kwargs):
        """
        Инициализация вектора состояния q.
        """
        self.matrix = matrix
        self.init_data = start_param

        self.__q_st_in = None
        self.__q_ekv_in = None
        self.__q_gr = None

        self.__r_st_in = None
        self.__r_ekv_in = None
        self.__r_gr = None

        self.__v_st_in = None
        self.__v_ekv_in = None
        self.__v_gr = None

        if self.init_data[7] == 1:
            print('Стартовая инерциальная геоцентрическая СК')
            self.__q_st_in = self.load_q()
            x, y, z = self.__q_st_in[:3]
            vx, vy, vz = self.__q_st_in[3:6]
            self.__r_st_in = np.array([x, y, z])
            self.__v_st_in = np.array([vx, vy, vz])

        elif self.init_data[7] == 2:
            print('Экваториальная инерциальная геоцентрическая СК')
            self.__q_ekv_in = self.load_q()
            ksi_1, ksi_2, ksi_3, v_ksi_1, v_ksi_2, v_ksi_3 = self.__q_ekv_in[:6]
            self.__r_ekv_in = np.array([ksi_1, ksi_2, ksi_3])
            self.__v_ekv_in = np.array([v_ksi_1, v_ksi_2, v_ksi_3])

        elif self.init_data[7] == 3:
            print('Гринвичская СК')
            self.__q_gr = self.load_q()
            ksi_gr_1, ksi_gr_2, ksi_gr_3, v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3 = self.__q_gr[:6]
            self.__r_gr = np.array([ksi_gr_1, ksi_gr_2, ksi_gr_3])
            self.__v_gr = np.array([v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3])

    def load_q(self):
        """
        Подгружает параметры начального состояния
        """
        data = self.init_data
        return np.array([data[0], data[1], data[2], data[3], data[4], data[5], data[6]])

    @property
    def q_st_in(self):
        if self.__q_st_in is None:
            if self.__q_ekv_in is None:
                self.__q_ekv_in = self.q_ekv_in

            self.__r_st_in = np.dot(self.matrix.d, self.__r_ekv_in)
            self.__v_st_in = np.dot(self.matrix.d, self.__v_ekv_in)
            self.__q_st_in = np.concatenate((self.__r_st_in, self.__v_st_in, np.array([self.__q_ekv_in[6]])))

        return self.__q_st_in

    @property
    def q_ekv_in(self):
        if self.__q_ekv_in is None:
            print('q_ekv_in посчиталось впервые')
            if self.__q_st_in is not None:
                print('расчет прошел через q_st_in')
                self.__r_ekv_in = np.dot(self.matrix.d.T, self.__r_st_in)
                self.__v_ekv_in = np.dot(self.matrix.d.T, self.__v_st_in)
                self.__q_ekv_in = np.concatenate((self.__r_ekv_in, self.__v_ekv_in, np.array([self.__q_st_in[6]])))

            elif self.__q_gr is not None:
                print('расчет прошел через q_gr')
                self.__r_ekv_in = np.dot(self.matrix.T_G.T, self.__r_gr)
                self.__v_ekv_in = np.dot(self.matrix.T_G.T, self.__v_gr) + np.cross(self.matrix.Ω_vector, self.__r_ekv_in)
                self.__q_ekv_in = np.concatenate((self.__r_ekv_in, self.__v_ekv_in, np.array([self.__q_gr[6]])))
            else:
                raise ValueError("Произошла ошибка в свойстве 'q_ekv_in'\n"
                                 "Не найдено иных представлений вектора")

        return self.__q_ekv_in

    @property
    def q_gr(self):
        if self.__q_gr is None:
            if self.__q_ekv_in is None:
                self.__q_ekv_in = self.q_ekv_in

            self.__r_gr = np.dot(self.matrix.T_G, self.__r_ekv_in)
            self.__v_gr = np.dot(self.matrix.T_G, self.__v_ekv_in) - np.cross(self.matrix.Ω_vector, self.__r_gr)
            self.__q_gr = np.concatenate((self.__r_gr, self.__v_gr, np.array([self.__q_ekv_in[6]])))
        return self.__q_gr


