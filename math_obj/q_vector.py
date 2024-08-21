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
            self.__geodesy_coordinate = None
            self.__proj_point = None

            self.__depth = 0

        def __str__(self):
            return str(self.__value)

        def __repr__(self):
            if self.__depth > 2:  # Ограничиваем глубину до 2
                return "..."
            self.__depth += 1
            result = f"VectorState(value={self.__value}, height={self.height})"
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
        def r_vector(self):
            """
            Возвращает текущий вектор скорости.
            """
            return np.array(self.__value[:3])
        @property
        def r_norm(self):
            """
            Возвращает текущий вектор скорости.
            """
            return np.linalg.norm(np.array(self.__value[:3]))
        
        @property
        def time(self):
            """
            Возвращает текущее время.
            """
            return self.__value[-1]

        @property
        def speed_vector(self):
            return np.array(self.__value[3:6])
        
        @property
        def speed_norm(self):
            return np.linalg.norm(np.array(self.__value[3:6]))

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

        def __height(self):
            """Вычисляет точку проекции на ОЗЭ и расстояние до нее."""

            if self.__height_m == 0:

                def geodesy_height(q):
                    ON = 0
                    i = 0
                    while i < 5:
                        r = np.sqrt(q[0] ** 2 + q[1] ** 2 + (q[2] + ON) ** 2)
                        snb = (q[2] + ON)/r
                        N = self.__a_oze/np.sqrt(1 - self.__e2_oze * (snb ** 2))
                        ON = self.__e2_oze * N * snb
                        i += 1
                    else:
                        return r - N

                if self.__sys != 3:
                    self.__grin_for_calculation_h = self.__outer_instance.q_gr
                    self.__height_above_ellipsoid = geodesy_height(self.__grin_for_calculation_h)
                else:
                    self.__height_above_ellipsoid = geodesy_height(self)

        def __geodesy_coord(self):

            def geodesy_coord(q, tol=1e-6):
                X, Y, Z = q[:3]
                r = np.sqrt(X ** 2 + Y ** 2)

                if r == 0:
                    B = (np.pi / 2) * np.sign(Z)
                    L = 0
                else:
                    La = np.arcsin(Y / r)

                    if Y >= 0 and X >= 0:
                        L = La
                    elif Y >= 0 and X < 0:
                        L = np.pi - La
                    elif Y < 0 and X < 0:
                        L = np.pi + La
                    elif Y < 0 and X >= 0:
                        L = 2 * np.pi - La

                    if Z == 0:
                        B = 0
                    else:
                        ro = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)
                        c = np.arcsin(Z / ro)
                        p = (self.__e2_oze * self.__a_oze) / (2 * ro)

                        s1 = 0
                        while True:
                            b = c + s1
                            s2 = np.arcsin(p * np.sin(2 * b)) / np.sqrt(1 - self.__e2_oze * (np.sin(b) ** 2))
                            if np.abs(s2 - s1) < tol:
                                B = b
                                break

                            s1 = s2

                        if np.abs(r / Z) < 1e-8:
                            B -= r / Z
                return np.array([B, L])

            if self.__sys != 3:
                self.__grin_for_calculation_h = self.__outer_instance.q_gr
                self.__geodesy_coordinate = geodesy_coord(self.__grin_for_calculation_h)
            else:
                self.__geodesy_coordinate = geodesy_coord(self)

        # @property
        # def proj_point(self):
        #     if self.__proj_point is None:
        #         self.__proj_and_height()
        #     return self.__proj_point

        @property
        def height(self):
            if self.__height_above_ellipsoid is None:
                self.__height()
            return self.__height_above_ellipsoid

        @property
        def geodesy_rad(self):
            if self.__geodesy_coordinate is None:
                self.__geodesy_coord()
            return self.__geodesy_coordinate

        @property
        def geodesy_grad(self):
            if self.__geodesy_coordinate is None:
                self.__geodesy_coord()
            return np.degrees(self.__geodesy_coordinate)

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
