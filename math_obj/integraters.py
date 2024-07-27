import numpy as np
from math_obj.q_vector import Q_v_state

class integrators:

    def __init__(self):

        self.__runge_4 = None

    def __runge_methods(self, method):
        
        if method == 4:

            def runge_4_method(f_prch, q, H_k=0, epsilon=0.001, dt=1):
                if isinstance(q, Q_v_state.VectorState):
                    if q.system != 3:
                        # Переводим вектор на всякий случай в гринвичскую СК
                        q = q.in_gr

                    print(q)
                    q_values = [q]
                    f_accel = np.array(f_prch(q)[3:6])
                    f_accel_values = [f_accel.copy()]
                    while True:
                        k1 = f_prch(q)
                        k2 = f_prch(q + 0.5 * dt * k1)
                        k3 = f_prch(q + 0.5 * dt * k2)
                        k4 = f_prch(q + dt * k3)
                        q_prom = q + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6

                        print(f"height справа: {q_prom.height}")

                        if np.abs(q_prom.height - H_k) <= epsilon:
                            q = q_prom
                            f_accel = np.array(f_prch(q)[3:6])
                            q_values.append(q)
                            f_accel_values.append(f_accel.copy())
                            print(f"Time: {q[-1]}\n"
                                  f"gr_coord: {q.r}\n"
                                  f"gr_speed: {q.speed}\n"
                                  f"Height: {q.height}\n")
                            break

                        else:
                            if q_prom.height - H_k < 0:
                                dt = ((q.height - H_k) / (q.height - q_prom.height)) * dt
                                print("--------------------------------------------")
                                print(f"New dt: {dt}")
                                print(f"Time: {q[-1]}\n"
                                      f"gr_coord: {q.r}\n"
                                      f"gr_speed: {q.speed}\n"
                                      f"Height: {q.height}")
                                print("--------------------------------------------\n")
                            else:
                                q = q_prom
                                f_accel = np.array(f_prch(q)[3:6])
                                q_values.append(q)
                                f_accel_values.append(f_accel.copy())
                                print(f"Time: {q[-1]}\n"
                                      f"gr_coord: {q.r}\n"
                                      f"gr_speed: {q.speed}\n"
                                      f"Height: {q.height}\n")

                    return q_values, f_accel_values

            return runge_4_method

    @property
    def runge_4(self):

        if self.__runge_4 is None:

            self.__runge_4 = self.__runge_methods(4)

        return self.__runge_4


