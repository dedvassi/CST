import numpy as np
from scipy.optimize import minimize


class Q_v_state:
    """
    Этот класс позволяет создавать и модифицировать вектор состояния q (7-вектор)
    """

    class VectorState:
        def __init__(self,
                     outer_instance,
                     init_value,
                     sys,
                     a_oze,
                     b_oze,
                     r_oze_sr,
                     e2_oze,
                     height_m):
            self.__outer_instance = outer_instance
            self.__value = init_value
            self.__sys = sys
            self.__a_oze = a_oze
            self.__b_oze = b_oze
            self.__r_oze_sr = r_oze_sr
            self.__e2_oze = e2_oze
            self.__height_m = height_m

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
                if other.system == self.__sys:
                    return self.__class__(self.__outer_instance, self.__value + other.value, self.__sys, self.__a_oze,
                                          self.__b_oze, self.__r_oze_sr, self.__e2_oze, self.__height_m)
                else:
                    if self.__sys == 1:
                        other = other.in_st
                    elif self.__sys == 2:
                        other = other.in_ekv
                    elif self.__sys == 3:
                        other = other.in_gr
                    return self.__class__(self.__outer_instance, self.__value + other.value, self.__sys, self.__a_oze,
                                          self.__b_oze, self.__r_oze_sr, self.__e2_oze, self.__height_m)

            elif isinstance(other, np.ndarray) and len(other) == 7:
                return self.__class__(self.__outer_instance, self.__value + other, self.__sys, self.__a_oze,
                                      self.__b_oze, self.__r_oze_sr, self.__e2_oze, self.__height_m)
            else:
                raise TypeError("Unsupported type for additional")

        def __iadd__(self, other):
            if isinstance(other, self.__class__):
                if other.system == self.__sys:
                    self.value = self.__value + other.value
                    return self.__class__(self.__outer_instance, self.__value, self.__sys, self.__a_oze,
                                          self.__b_oze, self.__r_oze_sr, self.__e2_oze, self.__height_m)
                else:
                    if self.__sys == 1:
                        other = other.in_st
                    elif self.__sys == 2:
                        other = other.in_ekv
                    elif self.__sys == 3:
                        other = other.in_gr
                    self.value = self.__value + other.value
                    return self.__class__(self.__outer_instance, self.__value, self.__sys, self.__a_oze,
                                          self.__b_oze, self.__r_oze_sr, self.__e2_oze, self.__height_m)

            elif isinstance(other, np.ndarray) and len(other) == 7:
                self.value = self.__value + other
                return self.__class__(self.__outer_instance, self.__value, self.__sys, self.__a_oze, self.__b_oze,
                                      self.__r_oze_sr, self.__e2_oze, self.__height_m)
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
        def r(self):
            """
            Возвращает текущий вектор скорости.
            """
            return np.array(self.__value[:3])

        @property
        def speed(self):
            return np.array(self.__value[3:6])

        @property
        def value(self):
            return self.__value

        @value.setter
        def value(self, new_value):
            self.__value = new_value
            self.__outer_instance.set_value(self.__value, self.__sys)
            self.__height_above_ellipsoid = None
            self.__proj_point = None

        @property
        def system(self):
            return self.__sys

        def __proj_and_height(self):
            """Вычисляет точку проекции на ОЗЭ и расстояние до нее."""

            if self.__height_m == 0:
                def geodesy_height(q):
                    r = np.array(q[:3])
                    r_norm = np.linalg.norm(r)
                    return None, r_norm - self.__a_oze / np.sqrt(1 + self.__e2_oze*((q[2] / r_norm) ** 2))

                if self.__sys != 3:
                    self.__grin_for_calculation_h = self.__outer_instance.q_gr
                    self.__proj_point, self.__height_above_ellipsoid = geodesy_height(self.__grin_for_calculation_h)
                else:
                    self.__proj_point, self.__height_above_ellipsoid = geodesy_height(self)

            if self.__height_m == 1:
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
                        return (x_ ** 2 / self.__a_oze ** 2) + (y_ ** 2 / self.__a_oze ** 2) + (
                                    z_ ** 2 / self.__b_oze ** 2) - 1

                    def is_inside_ellipsoid(x, y, z):
                        return (x ** 2 / self.__a_oze ** 2) + (y ** 2 / self.__a_oze ** 2) + (
                                    z ** 2 / self.__b_oze ** 2) - 1 < 0

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
                    self.__proj_point, self.__height_above_ellipsoid = project_point_to_ellipsoid(
                        self.__grin_for_calculation_h)
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

    def __init__(self,
                 matrix,
                 q_non_sys,
                 system_coord,
                 a_oze=6378136.0,
                 b_oze=6356751.361795686,
                 r_oze_sr=6371110.0,
                 e2_oze=0.0066943662,
                 height_m=0):
        """
        Инициализирует вектор состояния q в заданной системе координат.
        Args:
            matrix (Matrix): Экземпляр класса Matrix.
            q_non_sys (np.array): Вектор состояния q.
            system_coord (int): Номер системы координат (1 - стартовая, 2 - экваториальная, 3 - Гринвичская).
            a_oze (float, optional): Параметр a эллипсоида. Defaults to 6378136.0.
            b_oze (float, optional): Параметр b эллипсоида. Defaults to 6356751.361795686.
            r_oze_sr (float, optional): Средний радиус Земли. Defaults to 6371110.0.
            e2_oze (float, optional): Квадрат эксцентриситета ОЗЭ. Defaults to 0.0066943662.
            height_m (int, optional): Тип метода расчета высоты. Defaults to 0 (по геодезии).
        """
        self.__matrix = matrix
        self.__value = q_non_sys
        self.__sys = system_coord
        self.__a_oze = a_oze
        self.__b_oze = b_oze
        self.__r_oze_sr = r_oze_sr
        self.__e2_oze = e2_oze
        self.__height_m = height_m

        self.__q_st_in = None
        self.__q_ekv_in = None
        self.__q_gr = None

        self.__r_st_in = None
        self.__r_ekv_in = None
        self.__r_gr = None

        self.__v_st_in = None
        self.__v_ekv_in = None
        self.__v_gr = None

        if self.__sys == 1:
            self.__q_st_in = self.VectorState(self, self.__value, self.__sys, self.__a_oze, self.__b_oze,
                                              self.__r_oze_sr, self.__e2_oze, self.__height_m)
            x, y, z = self.__q_st_in[:3]
            vx, vy, vz = self.__q_st_in[3:6]
            self.__r_st_in = np.array([x, y, z])
            self.__v_st_in = np.array([vx, vy, vz])

        elif self.__sys == 2:
            self.__q_ekv_in = self.VectorState(self, self.__value, self.__sys, self.__a_oze, self.__b_oze,
                                               self.__r_oze_sr, self.__e2_oze, self.__height_m)
            ksi_1, ksi_2, ksi_3, v_ksi_1, v_ksi_2, v_ksi_3 = self.__q_ekv_in[:6]
            self.__r_ekv_in = np.array([ksi_1, ksi_2, ksi_3])
            self.__v_ekv_in = np.array([v_ksi_1, v_ksi_2, v_ksi_3])

        elif self.__sys == 3:
            self.__q_gr = self.VectorState(self, self.__value, self.__sys, self.__a_oze, self.__b_oze, self.__r_oze_sr,
                                           self.__e2_oze, self.__height_m)
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

        self.__q_st_in = None
        self.__q_ekv_in = None
        self.__q_gr = None

        self.__r_st_in = None
        self.__r_ekv_in = None
        self.__r_gr = None

        self.__v_st_in = None
        self.__v_ekv_in = None
        self.__v_gr = None

        if self.__sys == 1:
            self.__q_st_in = self.VectorState(self, self.__value, self.__sys, self.__a_oze, self.__b_oze,
                                              self.__r_oze_sr, self.__e2_oze, self.__height_m)
            x, y, z = self.__q_st_in[:3]
            vx, vy, vz = self.__q_st_in[3:6]
            self.__r_st_in = np.array([x, y, z])
            self.__v_st_in = np.array([vx, vy, vz])

        elif self.__sys == 2:
            self.__q_ekv_in = self.VectorState(self, self.__value, self.__sys, self.__a_oze, self.__b_oze,
                                               self.__r_oze_sr, self.__e2_oze, self.__height_m)
            ksi_1, ksi_2, ksi_3, v_ksi_1, v_ksi_2, v_ksi_3 = self.__q_ekv_in[:6]
            self.__r_ekv_in = np.array([ksi_1, ksi_2, ksi_3])
            self.__v_ekv_in = np.array([v_ksi_1, v_ksi_2, v_ksi_3])

        elif self.__sys == 3:
            self.__q_gr = self.VectorState(self, self.__value, self.__sys, self.__a_oze, self.__b_oze, self.__r_oze_sr,
                                           self.__e2_oze, self.__height_m)
            ksi_gr_1, ksi_gr_2, ksi_gr_3, v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3 = self.__q_gr[:6]
            self.__r_gr = np.array([ksi_gr_1, ksi_gr_2, ksi_gr_3])
            self.__v_gr = np.array([v_ksi_gr_1, v_ksi_gr_2, v_ksi_gr_3])
        else:
            raise ValueError("Несуществующая СК")

    def set_value(self, new_value, sys):
        """
        Устанавливает новое значение вектора состояния q и пересчитывает его в указанной системе координат.
        Последняя по задумке передается из экземпляров класса VectorState, или при желании извне!
        Метод по сути заново инициализирует вектор состояния!

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
        if self.__sys == 1:
            self.__q_st_in = self.VectorState(self, self.__value, self.__sys, self.__a_oze, self.__b_oze,
                                              self.__r_oze_sr, self.__e2_oze, self.__height_m)
            x, y, z = self.__q_st_in[:3]
            vx, vy, vz = self.__q_st_in[3:6]
            self.__r_st_in = np.array([x, y, z])
            self.__v_st_in = np.array([vx, vy, vz])

        elif self.__sys == 2:
            self.__q_ekv_in = self.VectorState(self, self.__value, self.__sys, self.__a_oze, self.__b_oze,
                                               self.__r_oze_sr, self.__e2_oze, self.__height_m)
            ksi_1, ksi_2, ksi_3, v_ksi_1, v_ksi_2, v_ksi_3 = self.__q_ekv_in[:6]
            self.__r_ekv_in = np.array([ksi_1, ksi_2, ksi_3])
            self.__v_ekv_in = np.array([v_ksi_1, v_ksi_2, v_ksi_3])

        elif self.__sys == 3:
            self.__q_gr = self.VectorState(self, self.__value, self.__sys, self.__a_oze, self.__b_oze, self.__r_oze_sr,
                                           self.__e2_oze, self.__height_m)
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
            self.__q_st_in = self.VectorState(self, q, np.float64(1), self.__a_oze, self.__b_oze, self.__r_oze_sr,
                                              self.__e2_oze, self.__height_m)
        return self.__q_st_in

    @property
    def q_ekv_in(self):
        """
        Возвращает вектор состояния q в экваториальной инерциальной геоцентрической СК.
        """
        if self.__q_ekv_in is None:
            if self.__q_st_in is not None:
                self.__r_ekv_in = np.dot(self.__matrix.d.T, self.__r_st_in)
                self.__v_ekv_in = np.dot(self.__matrix.d.T, self.__v_st_in)
                q = np.concatenate((self.__r_ekv_in, self.__v_ekv_in, np.array([self.__q_st_in[6]])))
                self.__q_ekv_in = self.VectorState(self, q, np.float64(2), self.__a_oze, self.__b_oze, self.__r_oze_sr,
                                                   self.__e2_oze, self.__height_m)

            elif self.__q_gr is not None:
                self.__matrix.data_T_G = np.array([self.__matrix.Ω, self.__q_gr[6]])
                self.__r_ekv_in = np.dot(self.__matrix.T_G.T, self.__r_gr)
                self.__v_ekv_in = np.dot(self.__matrix.T_G.T, self.__v_gr) + np.cross(self.__matrix.Ω_vector,
                                                                                      self.__r_ekv_in)
                q = np.concatenate((self.__r_ekv_in, self.__v_ekv_in, np.array([self.__q_gr[6]])))
                self.__q_ekv_in = self.VectorState(self, q, np.float64(2), self.__a_oze, self.__b_oze, self.__r_oze_sr,
                                                   self.__e2_oze, self.__height_m)
            else:
                raise ValueError(
                    "Неудалось преобразовать вектор в Экваториальную геоцентрическую инерциальную систему.\n"
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
            self.__matrix.data_T_G = np.array([self.__matrix.Ω, self.__q_ekv_in[6]])
            self.__r_gr = np.dot(self.__matrix.T_G, self.__r_ekv_in)
            self.__v_gr = np.dot(self.__matrix.T_G, self.__v_ekv_in) - np.cross(self.__matrix.Ω_vector, self.__r_gr)
            q = np.concatenate((self.__r_gr, self.__v_gr, np.array([self.__q_ekv_in[6]])))
            self.__q_gr = self.VectorState(self, q, np.float64(3), self.__a_oze, self.__b_oze, self.__r_oze_sr,
                                           self.__e2_oze, self.__height_m)
        return self.__q_gr

    @property
    def r(self):
        """
        Возвращает текущий радиус-вектор.
        """
        if self.__sys == 1:
            return self.__r_st_in
        if self.__sys == 2:
            return self.__r_ekv_in
        if self.__sys == 3:
            return self.__r_gr

    @property
    def speed(self):
        """
        Возвращает текущий вектор скорости.
        """
        if self.__sys == 1:
            return self.__v_st_in
        if self.__sys == 2:
            return self.__v_ekv_in
        if self.__sys == 3:
            return self.__v_gr

    @property
    def system(self):
        """
        Возвращает текущую СК.
        """
        return self.__sys
