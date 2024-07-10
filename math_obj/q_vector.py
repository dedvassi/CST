import numpy as np
from scipy.optimize import minimize

class Q_v_state:
    """
    Этот класс позволяет создавать и модифицировать вектор состояния q (7-вектор)
    """

    class VectorState:
        def __init__(self, init_value, a_oze, b_oze, r_oze_sr):
            self.__value = init_value
            self.__a_oze = a_oze
            self.__b__oze = b_oze
            self.__r_oze_sr = r_oze_sr

            self.__height_above_ellipsoid = None
            self.__proj_point = None

        def __str__(self):
            return str(self.__value)

        def __getitem__(self, item):
            return self.__value[item]
        @property
        def value(self):
            return self.__value
        @value.setter
        def value(self, new_value):
            self.__value = new_value
            self.__height_above_ellipsoid = None
            self.__proj_point = None

        def __proj_and_height(self):
            """Вычисляет точку проекции на ОЗЭ и расстояние до нее."""
            def project_point_to_sphere(q):

                r = np.array(q[:3])

                print(f"rrrr {r}")
                r_norm = np.linalg.norm(r)
                print(f"rrrr {r_norm}")
                a = (6371110.0 / r_norm) * r
                print(f"aaaaa {a}")
                return (self.__r_oze_sr / r_norm) * r

            # Функция для проекции точки на эллипсоид
            def project_point_to_ellipsoid(q):
                x, y, z = q[:3]

                def distance_to_point(p):
                    x_, y_, z_ = p
                    return np.sqrt((x - x_) ** 2 + (y - y_) ** 2 + (z - z_) ** 2)

                def ellipsoid_constraint(p):
                    x_, y_, z_ = p
                    return (x_ ** 2 / self.__a_oze ** 2) + (y_ ** 2 / self.__a_oze ** 2) + (z_ ** 2 / self.__b__oze ** 2) - 1

                def is_inside_ellipsoid(x, y, z):
                    return (x ** 2 / self.__a_oze ** 2) + (y ** 2 / self.__a_oze ** 2) + (z ** 2 / self.__b__oze ** 2) - 1 < 0

                x_initial = project_point_to_sphere(q)  # Начальное приближение по проекции на сферу
                constraint = {'type': 'eq', 'fun': ellipsoid_constraint}
                result = minimize(distance_to_point, x_initial, constraints=[constraint], method='SLSQP')

                if result.success:
                    optimal_point = result.x
                    distance = result.fun  # Вычисляем расстояние между q и найденной точкой на эллипсоиде
                    if is_inside_ellipsoid(x, y, z):
                        distance = -distance  # Отрицательное расстояние, если точка внутри эллипсоида
                    return np.array(optimal_point), np.array(distance)
                else:
                    raise ValueError("Оптимизация не удалась: " + result.message)

            self.__proj_point, self.__height_above_ellipsoid = project_point_to_ellipsoid(self)

        @property
        def proj_point(self):
            if self.__proj_point is None:
                self.__proj_and_height()
            return self.__proj_point
        @property
        def height(self):
            if self.__height_above_ellipsoid is None:
                self.__proj_and_height()
            return self.__height_above_ellipsoid

    def __init__(self, matrix, q_non_sys, system_coord,  *args, **kwargs):
        """
        Инициализация вектора состояния q.
        """
        self.matrix = matrix
        self.init_data = np.concatenate((q_non_sys, np.array([system_coord])))

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
            self.__q_st_in = self.VectorState(self.__load_q(), 6378136.0, 6356751.361795686, 6371110.0)
            x, y, z = self.__q_st_in[:3]
            vx, vy, vz = self.__q_st_in[3:6]
            self.__r_st_in = np.array([x, y, z])
            self.__v_st_in = np.array([vx, vy, vz])

        elif self.init_data[7] == 2:
            print('Экваториальная инерциальная геоцентрическая СК')
            self.__q_ekv_in = self.VectorState(self.__load_q(), 6378136.0, 6356751.361795686, 6371110.0)
            ksi_1, ksi_2, ksi_3, v_ksi_1, v_ksi_2, v_ksi_3 = self.__q_ekv_in[:6]
            self.__r_ekv_in = np.array([ksi_1, ksi_2, ksi_3])
            self.__v_ekv_in = np.array([v_ksi_1, v_ksi_2, v_ksi_3])

        elif self.init_data[7] == 3:
            print('Гринвичская СК')
            self.__q_gr = self.VectorState(self.__load_q(), 6378136.0, 6356751.361795686, 6371110.0)
            ksi_gr_1, ksi_gr_2, ksi_gr_3, v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3 = self.__q_gr[:6]
            self.__r_gr = np.array([ksi_gr_1, ksi_gr_2, ksi_gr_3])
            self.__v_gr = np.array([v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3])
        else:
            raise ValueError("Несуществующая СК")

    def __load_q(self):
        """
        Подгружает параметры начального состояния
        """
        data = self.init_data
        return np.array([data[0], data[1], data[2], data[3], data[4], data[5], data[6]])

    def sum_coord(self):
        return np.sum(self.init_data[:6])  # Пример метода, который можно вызывать

    @property
    def q_st_in(self):
        if self.__q_st_in is None:
            if self.__q_ekv_in is None:
                self.__q_ekv_in = self.q_ekv_in

            self.__r_st_in = np.dot(self.matrix.d, self.__r_ekv_in)
            self.__v_st_in = np.dot(self.matrix.d, self.__v_ekv_in)
            q = np.concatenate((self.__r_st_in, self.__v_st_in, np.array([self.__q_ekv_in[6]])))
            self.__q_st_in = self.VectorState(q, 6378136.0, 6356751.361795686, 6371110.0)
        return self.__q_st_in

    @property
    def q_ekv_in(self):
        if self.__q_ekv_in is None:
            print('q_ekv_in посчиталось впервые')
            if self.__q_st_in is not None:
                print('расчет прошел через q_st_in')
                self.__r_ekv_in = np.dot(self.matrix.d.T, self.__r_st_in)
                self.__v_ekv_in = np.dot(self.matrix.d.T, self.__v_st_in)
                q = np.concatenate((self.__r_ekv_in, self.__v_ekv_in, np.array([self.__q_st_in[6]])))
                print(q)
                self.__q_ekv_in = self.VectorState(q, 6378136.0, 6356751.361795686, 6371110.0)

            elif self.__q_gr is not None:
                print('расчет прошел через q_gr')
                self.__r_ekv_in = np.dot(self.matrix.T_G.T, self.__r_gr)
                self.__v_ekv_in = np.dot(self.matrix.T_G.T, self.__v_gr) + np.cross(self.matrix.Ω_vector, self.__r_ekv_in)
                q = np.concatenate((self.__r_ekv_in, self.__v_ekv_in, np.array([self.__q_gr[6]])))
                self.__q_ekv_in = self.VectorState(q, 6378136.0, 6356751.361795686, 6371110.0)
            else:
                raise ValueError("Неудалось преобразовать вектор в Экваториальную геоцентрическую инерциальную систему.\n"
                                 "Исключение в свойстве 'q_ekv_in' - не найдены иные формы вектора")

        return self.__q_ekv_in

    @property
    def q_gr(self):
        if self.__q_gr is None:
            print('пока в гринвиче нет ничего')
            if self.__q_ekv_in is None:
                print("Сперва нашел в экваториальной")
                self.__q_ekv_in = self.q_ekv_in

            self.__r_gr = np.dot(self.matrix.T_G, self.__r_ekv_in)
            self.__v_gr = np.dot(self.matrix.T_G, self.__v_ekv_in) - np.cross(self.matrix.Ω_vector, self.__r_gr)
            q = np.concatenate((self.__r_gr, self.__v_gr, np.array([self.__q_ekv_in[6]])))
            self.__q_gr = self.VectorState(q, 6378136.0, 6356751.361795686, 6371110.0)
        return self.__q_gr


