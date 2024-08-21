import numpy as np
from numba import cuda
from math_obj.q_vector import Q_v_state

class integrators:

    def __init__(self, cacher):

        self.__cacher = cacher
        self.__runge_4 = None

    def __runge_methods(self, method):
        
        if method == 4:
            
            def runge_4_method(f_prch, q, H_k=0, epsilon=0.001, dt=1):
                if isinstance(q, Q_v_state.VectorState):
                    if q.system != 3:
                        # Переводим вектор на всякий случай в гринвичскую СК
                        q = q.in_gr

                    print(q)
                    self.__cacher.append(q=q)
                    
                    while True:
                        print("||||||||||||||||||||||||||||||||||||||||||||||")
                        print(f"Runge 1-й: ")
                        k1 = f_prch(q, True)
                        print(f"Runge 2-й: ")
                        k2 = f_prch(q + 0.5 * dt * k1, False)
                        print(f"Runge 3-й: ")
                        k3 = f_prch(q + 0.5 * dt * k2, False)
                        print(f"Runge 4-й: ")
                        k4 = f_prch(q + dt * k3, False)
                        q_prom = q + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
                        print(f"height справа: {q_prom.height}")

                        if np.abs(q_prom.height - H_k) <= epsilon:
                            print(f"Конечный шаг")
                            q = q_prom
                            _ = f_prch(q, True)
                            self.__cacher.append(q=q)
                            print(f"Time: {q[-1]}\n"
                                  f"gr_coord: {q.r_vector}\n"
                                  f"gr_speed: {q.speed_vector}\n"
                                  f"Height: {q.height}\n")
                            break

                        else:
                            if q_prom.height - H_k < 0:
                                del self.__cacher[-1]
                                dt = ((q.height - H_k) / (q.height - q_prom.height)) * dt
                                print("--------------------------------------------")
                                print(f"height_right - H_k = {q_prom.height - H_k} => смена шага")
                                print(f"New dt: {dt}")
                                print(f"Time: {q[-1]}\n"
                                      f"gr_coord: {q.r_vector}\n"
                                      f"gr_speed: {q.speed_vector}\n"
                                      f"Height: {q.height}")
                                print("--------------------------------------------\n")
                            else:
                                q = q_prom
                                self.__cacher.append(q=q)
                                print(f"Time: {q[-1]}\n"
                                      f"gr_coord: {q.r_vector}\n"
                                      f"gr_speed: {q.speed_vector}\n"
                                      f"Height: {q.height}\n")

            return runge_4_method

    @property
    def runge_4(self):

        if self.__runge_4 is None:

            self.__runge_4 = self.__runge_methods(4)

        return self.__runge_4


