import numpy as np

class integrators:

    def __init__(self):

        self.__runge_4 = None

    def __runge_methods(self, method):
        
        if method == 4:

            def runge_4_method(f_prch, q, H_k=0, epsilon=1, dt=1):
                if q.system != 3:
                    # Переводим вектор на всякий случай в гринвичскую СК
                    q = q.in_gr

                print(q)
                q_values = [q]
                f_accel = np.array(f_prch(q)[3:6])
                f_accel_values = [f_accel.copy()]
                while np.abs(q.height - H_k) >= epsilon and (q.height - H_k) > 0 and q[6] <= 543200:
                    if q.height <= 3000:
                        dt = 0.1
                    k1 = f_prch(q)
                    k2 = f_prch(q + 0.5 * dt * k1)
                    k3 = f_prch(q + 0.5 * dt * k2)
                    k4 = f_prch(q + dt * k3)
                    q += dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
                    
                    f_accel = np.array(f_prch(q)[3:6])
                    q_values.append(q)
                    f_accel_values.append(f_accel.copy())
                    print(q)
                return q_values, f_accel_values

            return runge_4_method

    @property
    def runge_4(self):

        if self.__runge_4 is None:

            self.__runge_4 = self.__runge_methods(4)

        return self.__runge_4


