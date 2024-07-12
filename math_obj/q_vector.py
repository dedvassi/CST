import numpy as np
from scipy.optimize import minimize

class Q_v_state:
    """
    Этот класс позволяет создавать и модифицировать вектор состояния q (7-вектор)
    """

    class VectorState:
        def __init__(self, outer_instance, init_value, sys, a_oze, b_oze, r_oze_sr):
            self.__outer_instance = outer_instance
            self.__value = init_value
            self.__sys = sys
            self.__a_oze = a_oze
            self.__b__oze = b_oze
            self.__r_oze_sr = r_oze_sr

            self.__value_change = False
            self.__grin_for_calculation_h = None
            self.__height_above_ellipsoid = None
            self.__proj_point = None

            self.__depth = 0

        def __str__(self):
            return str(self.__value)

        def __repr__(self):
            if self.__depth > 2:  # Ограничиваем глубину до 2
                return "..."
            self.__depth += 1
            result = f"VectorState(value={self.__value}, height={self.height}, proj_point={self.proj_point})"
            self.__depth -= 1
            return result

        def __call__(self):
            return self.__value

        def __array__(self):
            return self.__value

        def __getitem__(self, item):
            return self.__value[item]

        def __add__(self, other):
            if isinstance(other, self.__class__):
                return self.__class__(self.__value + other.value, self.__a_oze, self.__b__oze, self.__r_oze_sr)
            elif isinstance(other, np.ndarray):
                return self.__class__(self.__value + other, self.__a_oze, self.__b__oze, self.__r_oze_sr)
            else:
                raise TypeError("Unsupported type for additional")

        def __iadd__(self, other):
            if isinstance(other, self.__class__):
                return self.__class__(self.__value + other.value, self.__a_oze, self.__b__oze, self.__r_oze_sr)
            elif isinstance(other, np.ndarray):
                return self.__class__(self.__value + other, self.__a_oze, self.__b__oze, self.__r_oze_sr)
            else:
                raise TypeError("Unsupported type for additional")


        @property
        def in_st(self):
            return self.__outer_instance.q_st_in

        @property
        def in_ekv(self):
            return self.__outer_instance.q_ekv_in

        @property
        def in_gr(self):
            return self.__outer_instance.q_gr

        @property
        def value(self):
            return self.__value

        @value.setter
        def value(self, new_value):
            self.__value = new_value
            self.__outer_instance.set_value(self.__value, self.__sys)
            self.__height_above_ellipsoid = None
            self.__proj_point = None

        def __proj_and_height(self):
            """Вычисляет точку проекции на ОЗЭ и расстояние до нее."""
            def project_point_to_sphere(q):

                r = np.array(q[:3])
                r_norm = np.linalg.norm(r)
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
            if self.__sys != 3:
                self.__grin_for_calculation_h = self.__outer_instance.q_gr
                self.__proj_point, self.__height_above_ellipsoid = project_point_to_ellipsoid(self.__grin_for_calculation_h)
            else:
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

    def __init__(self, matrix, q_non_sys, system_coord, a_oze=6378136.0, b_oze=6356751.361795686, r_oze_sr=6371110.0,  *args, **kwargs):
        """
        Инициализирует вектор состояния q в заданной системе координат.

        Args:
            matrix (Matrix): Экземпляр класса Matrix.
            q_non_sys (np.array): Вектор состояния q.
            system_coord (int): Номер системы координат (1 - стартовая, 2 - экваториальная, 3 - Гринвичская).
            a_oze (float, optional): Параметр a эллипсоида. Defaults to 6378136.0.
            b_oze (float, optional): Параметр b эллипсоида. Defaults to 6356751.361795686.
            r_oze_sr (float, optional): Средний радиус Земли. Defaults to 6371110.0.
        """
        self.__matrix = matrix
        self.__value = q_non_sys
        self.__sys = system_coord
        self.__a_oze = a_oze
        self.__b_oze = b_oze
        self.__r_oze_sr = r_oze_sr

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
            self.__q_st_in = self.VectorState(self, self.__load_q(), self.init_data[7], 6378136.0, 6356751.361795686, 6371110.0)
            x, y, z = self.__q_st_in[:3]
            vx, vy, vz = self.__q_st_in[3:6]
            self.__r_st_in = np.array([x, y, z])
            self.__v_st_in = np.array([vx, vy, vz])

        elif self.init_data[7] == 2:
            print('Экваториальная инерциальная геоцентрическая СК')
            self.__q_ekv_in = self.VectorState(self, self.__load_q(), self.init_data[7], 6378136.0, 6356751.361795686, 6371110.0)
            ksi_1, ksi_2, ksi_3, v_ksi_1, v_ksi_2, v_ksi_3 = self.__q_ekv_in[:6]
            self.__r_ekv_in = np.array([ksi_1, ksi_2, ksi_3])
            self.__v_ekv_in = np.array([v_ksi_1, v_ksi_2, v_ksi_3])

        elif self.init_data[7] == 3:
            print('Гринвичская СК')
            self.__q_gr = self.VectorState(self, self.__load_q(), self.init_data[7], 6378136.0, 6356751.361795686, 6371110.0)
            ksi_gr_1, ksi_gr_2, ksi_gr_3, v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3 = self.__q_gr[:6]
            self.__r_gr = np.array([ksi_gr_1, ksi_gr_2, ksi_gr_3])
            self.__v_gr = np.array([v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3])
        else:
            raise ValueError("Несуществующая СК")

    def __call__(self):
        """
        Возвращает вектор состояния q в его начальной системе координат.
        """
        if self.__sys == 1:
            return self.__q_st_in
        elif self.__sys == 2:
            return self.__q_ekv_in
        elif self.__sys == 3:
            return self.__q_gr
        else:
            raise ValueError("Неверно инициализировано начальный вектор")

    @property
    def value(self):
        """
        Возвращает текущее значение вектора состояния q.
        """
        return self.__value

    @value.setter
    def value(self, new_value):
        """
        Устанавливает новое значение вектора состояния q и пересчитывает его в текущей системе координат.
        Предполагает применение к экземпляру класса Q_v_state
        """
        self.__value = new_value

        if self.init_data[7] == 1:
            print('Стартовая инерциальная геоцентрическая СК')
            self.__q_st_in = self.VectorState(self, self.__value, self.init_data[7], 6378136.0, 6356751.361795686, 6371110.0)
            x, y, z = self.__q_st_in[:3]
            vx, vy, vz = self.__q_st_in[3:6]
            self.__r_st_in = np.array([x, y, z])
            self.__v_st_in = np.array([vx, vy, vz])

        elif self.init_data[7] == 2:
            print('Экваториальная инерциальная геоцентрическая СК')
            self.__q_ekv_in = self.VectorState(self, self.__value, self.init_data[7], 6378136.0, 6356751.361795686, 6371110.0)
            ksi_1, ksi_2, ksi_3, v_ksi_1, v_ksi_2, v_ksi_3 = self.__q_ekv_in[:6]
            self.__r_ekv_in = np.array([ksi_1, ksi_2, ksi_3])
            self.__v_ekv_in = np.array([v_ksi_1, v_ksi_2, v_ksi_3])

        elif self.init_data[7] == 3:
            print('Гринвичская СК')
            self.__q_gr = self.VectorState(self, self.__value, self.init_data[7], 6378136.0, 6356751.361795686, 6371110.0)
            ksi_gr_1, ksi_gr_2, ksi_gr_3, v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3 = self.__q_gr[:6]
            self.__r_gr = np.array([ksi_gr_1, ksi_gr_2, ksi_gr_3])
            self.__v_gr = np.array([v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3])
        else:
            raise ValueError("Несуществующая СК")

    def set_value(self, new_value, sys):
        """
        Устанавливает новое значение вектора состояния q и пересчитывает его в указанной системе координат.
        Последняя по задумке передается из экземпляров класса VectorState, или при желании извне!

        Args:
            new_value (np.array): Новое значение вектора состояния q.
            sys (int): Система координат (1 - стартовая, 2 - экваториальная, 3 - Гринвичская).
        """
        self.__value = new_value
        self.__sys = sys
        self.__q_st_in = None
        self.__q_ekv_in = None
        self.__q_gr = None

        self.__r_st_in = None
        self.__r_ekv_in = None
        self.__r_gr = None

        self.__v_st_in = None
        self.__v_ekv_in = None
        self.__v_gr = None
        if sys == 1:
            print('Стартовая инерциальная геоцентрическая СК')
            self.__q_st_in = self.VectorState(self, self.__value, sys, 6378136.0, 6356751.361795686, 6371110.0)
            x, y, z = self.__q_st_in[:3]
            vx, vy, vz = self.__q_st_in[3:6]
            self.__r_st_in = np.array([x, y, z])
            self.__v_st_in = np.array([vx, vy, vz])

        elif sys == 2:
            print('Экваториальная инерциальная геоцентрическая СК')
            self.__q_ekv_in = self.VectorState(self, self.__value, sys, 6378136.0, 6356751.361795686, 6371110.0)
            ksi_1, ksi_2, ksi_3, v_ksi_1, v_ksi_2, v_ksi_3 = self.__q_ekv_in[:6]
            self.__r_ekv_in = np.array([ksi_1, ksi_2, ksi_3])
            self.__v_ekv_in = np.array([v_ksi_1, v_ksi_2, v_ksi_3])

        elif sys == 3:
            print('Гринвичская СК')
            self.__q_gr = self.VectorState(self, self.__value, sys, 6378136.0, 6356751.361795686, 6371110.0)
            ksi_gr_1, ksi_gr_2, ksi_gr_3, v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3 = self.__q_gr[:6]
            self.__r_gr = np.array([ksi_gr_1, ksi_gr_2, ksi_gr_3])
            self.__v_gr = np.array([v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3])
        else:
            raise ValueError("Несуществующая СК")


    @property
    def q_st_in(self):
        """
        Возвращает вектор состояния q в стартовой инерциальной геоцентрической СК.
        """
        if self.__q_st_in is None:
            if self.__q_ekv_in is None:
                self.__q_ekv_in = self.q_ekv_in

            self.__r_st_in = np.dot(self.__matrix.d, self.__r_ekv_in)
            self.__v_st_in = np.dot(self.__matrix.d, self.__v_ekv_in)
            q = np.concatenate((self.__r_st_in, self.__v_st_in, np.array([self.__q_ekv_in[6]])))
            self.__q_st_in = self.VectorState(self, q, 1, self.__a_oze, self.__b_oze, self.__r_oze_sr)
        return self.__q_st_in

    @property
    def q_ekv_in(self):
        """
        Возвращает вектор состояния q в экваториальной инерциальной геоцентрической СК.
        """
        if self.__q_ekv_in is None:
            if self.__q_st_in is not None:
                print('расчет прошел через q_st_in')
                self.__r_ekv_in = np.dot(self.matrix.d.T, self.__r_st_in)
                self.__v_ekv_in = np.dot(self.matrix.d.T, self.__v_st_in)
                q = np.concatenate((self.__r_ekv_in, self.__v_ekv_in, np.array([self.__q_st_in[6]])))
                self.__q_ekv_in = self.VectorState(self, q, 2, self.__a_oze, self.__b_oze, self.__r_oze_sr)

            elif self.__q_gr is not None:
                print('расчет прошел через q_gr')
                self.__r_ekv_in = np.dot(self.matrix.T_G.T, self.__r_gr)
                self.__v_ekv_in = np.dot(self.matrix.T_G.T, self.__v_gr) + np.cross(self.matrix.Ω_vector, self.__r_ekv_in)
                q = np.concatenate((self.__r_ekv_in, self.__v_ekv_in, np.array([self.__q_gr[6]])))
                self.__q_ekv_in = self.VectorState(self, q, 2, self.__a_oze, self.__b_oze, self.__r_oze_sr)
            else:
                raise ValueError("Неудалось преобразовать вектор в Экваториальную геоцентрическую инерциальную систему.\n"
                                 "Исключение в свойстве 'q_ekv_in' - не найдены иные формы вектора")

        return self.__q_ekv_in

    @property
    def q_gr(self):
        """
        Возвращает вектор состояния q в Гринвичской СК.
        """
        if self.__q_gr is None:
            if self.__q_ekv_in is None:
                self.__q_ekv_in = self.q_ekv_in

            self.__r_gr = np.dot(self.__matrix.T_G, self.__r_ekv_in)
            self.__v_gr = np.dot(self.__matrix.T_G, self.__v_ekv_in) - np.cross(self.__matrix.Ω_vector, self.__r_gr)
            q = np.concatenate((self.__r_gr, self.__v_gr, np.array([self.__q_ekv_in[6]])))
            self.__q_gr = self.VectorState(self, q, 3, self.__a_oze, self.__b_oze, self.__r_oze_sr)
        return self.__q_gr

    @property
    def system(self):
        """
        Возвращает текущую СК.
        """
        return self.__sys

