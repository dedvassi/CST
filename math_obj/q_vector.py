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

        if self.init_data[7] == 1:
            print('Стартовая инерциальная геоцентрическая СК')
            self.__q_st_in = self.load_Q()
            x, y, z = self.__q_st_in[:3]
            vx, vy, vz = self.__q_st_in[3:6]
            self.__r_st_in = np.array([x, y, z])
            self.__v_st_in = np.array([vx, vy, vz])


            self.__q_ekv_in = None
            self.__r_ekv_in = None
            self.__v_ekv_in = None

            self.__q_gr = None
            self.__r_gr = None
            self.__v_gr = None



        if self.init_data[7] == 2:
            print('Экваториальная инерциальная геоцентрическая СК')
            self.q_st = self.load_data_q_st()

        if self.init_data[7] == 3:
            print('Гринвичская СК')
            self.q_st = self.load_data_q_st()
        

    def load_Q(self):
        """
        Подгружает параметры начального состояния
        """
        data = self.init_data
        self.x = data[0]
        self.y = data[1]
        self.z = data[2] 
        self.vx = data[3] 
        self.vy = data[4] 
        self.vz = data[5] 
        self.t = data[6] 
        return np.array([self.x,
                              self.y,
                              self.z,
                              self.vx,
                              self.vy,
                              self.vz,
                              self.t,
                              ])

    @property
    def q_st_in(self):
        if self.__q_st_in is None:
            pass
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
                self.__r_gr = np.dot(self.matrix.d.T, self.__r_st_in)
                self.__v_gr = np.dot(self.matrix.d.T, self.__v_st_in)
                self.__q_ekv_in = np.concatenate((self.__r_ekv_in, self.__v_ekv_in, np.array([self.__q_st_in[6]])))


        return self.__q_ekv_in

    def q_gr_vector(self):
        pass

#a = Q_v_state()
#print(a.__dict__)

#a=np.array([1,2,3,4])
#print(type(a)

#print(isinstance(a, array))

