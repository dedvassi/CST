import numpy as np
import multiprocessing
import concurrent.futures
from working_with_files.datas_for_models import *


def delta_param_worker(input_queue, output_queue, atmo_cache, month):
    while True:
        key, B, L, H = input_queue.get()
        if key is None:
            break
        delta = delta_param(atmo_cache, month, key, B, L, H)
        output_queue.put((key, delta))
        input_queue.task_done()

# Глобальная функция
def delta_param(atmo_cache: dict, month: int, key: str, B: float, L: float, H: float):
    delta = 0
    for i in (atmo_cache[key]).keys():
        c, k, l, m, n = (atmo_cache[key])[i]

        Fk = np.cos(np.pi * H * (k - 1) / 102)

        if l == 1:
            Sl = 1
        elif l % 2 == 0:
            Sl = np.cos(np.pi * l * (month - 1) / 12)
        elif l % 2 == 1:
            Sl = np.sin(np.pi * (l - 1) * (month - 1) / 12)

        Gm = np.cos((B + np.pi / 2) * (m - 1))

        if n == 1:
            Rn = 1
        elif n % 2 == 0:
            Rn = np.cos(L * n / 2)
        elif n % 2 == 1:
            Rn = np.sin(L * (n - 1) / 2)

        delta += c * Fk * Sl * Gm * Rn

    return delta


class F_prch_maker:
    """Собирает функцию правой части в зависимости от установленных моделей"""

    def __init__(self,
                 grav_m: int,
                 atmo_m: int,
                 cacher,
                 Cx_priority=0,
                 omega_z=7.292115e-05,
                 month=1,
                 fM=398600441800000.0,
                 alpha_cs=20.046796,
                 R_g=287.05287,
                 s_mid_otd=13.2,
                 m_otd=4000):
        self.__start_param = np.concatenate((np.array([grav_m]), np.array([atmo_m])))
        self.__cacher = cacher
        self.__Cx_priority = Cx_priority
        self.__omega_z = omega_z
        self.__month = month
        self.__fM = fM
        self.__alpha_cs = alpha_cs
        self.__R_g = R_g
        self.__s_mid_otd = s_mid_otd
        self.__m_otd = m_otd

        # Модели поля и атмосферы
        self.__grav_model = self.__models('grav')
        self.__atmo_model = self.__models('atmo')

        # Кэшируем данные из таблиц по атмосфере
        self.__atmo_cache = check_csv_file_atmo(self.__atmo_model)
        self.__analysis_atmo = self.__analysis_atmo_cache()

        self.__Cx_cache = check_csv_file_TCxM(self.__Cx_priority)
        self.__analysis_Cx = self.__analysis_Cx_cache()

        self.__f_prch = None
        self.__speed_comp = self.__speed_component()
        self.__r_comp = self.__r_component()
        self.__grav_accel = self.__gravitational_acceleration()
        self.__aero_d_resist = self.__aerodynamics_resist()

        if self.__atmo_model == 2:
            keys = ['tplot', 'tdavl', 'ttemp', 'tvetz', 'tvetm']
            self.__process = {}

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {}
                for key in keys:
                    futures[key] = executor.submit(self.__start_process, key)

                for key, future in futures.items():
                    process, input_queue, output_queue = future.result()
                    self.__process[key] = (process, input_queue, output_queue)
            print("Запущены дополнительные процессы для обработки данных")

    def __start_process(self, key):
        input_queue = multiprocessing.JoinableQueue()
        output_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=delta_param_worker,
                                          args=(input_queue, output_queue, self.__atmo_cache, self.__month),
                                          name=f'proc-{key}')
        process.start()
        return process, input_queue, output_queue

    def __call__(self):
        return self.f_prch

    def __models(self, component):
        if component is 'grav':
            return self.__start_param[0]
        if component is 'atmo':
            return self.__start_param[1]

    def __r_component(self):
        """Компоненты радиусвектора с предыдущего шага"""
        def r_comp(q):
            r = q.r_vector
            r_norm = q.r_norm
            r_ort = r/r_norm
            return r, r_norm, r_ort
        return r_comp

    def __speed_component(self):
        """Компоненты скорости с предыдущего шага"""
        def speed_comp(q):
            v = q.speed_vector
            v_norm = q.speed_norm
            v_ort = v/v_norm
            return v, v_norm, v_ort
        return speed_comp

    def __gravitational_acceleration(self):
        """Добавление гравитационного ускорения"""
        if self.__grav_model == 0:
            def grav_accel(r):
                r_norm = np.linalg.norm(r)
                g = -self.__fM * r / r_norm ** 3
                return g
            return grav_accel
        else:
            self.__errors('initial_model_grav')

    def __aerodynamics_resist(self):
        """Добавление аэродинамики"""
        if self.__atmo_model == 0:
            # Применяется модель без атмосферы
            def aero_d_resist(ro, v_norm, v_ort, Cx, S_midotd, m_otd):
                return 0
            return aero_d_resist
        else:
            def aero_d_resist(ro, v_norm, v_ort, Cx, S_midotd, m_otd):
                dP = ro * (v_norm ** 2) / 2
                Wa = -((Cx * S_midotd) / m_otd) * dP # Коэф
                Wa_vector = Wa * v_ort  # вектор
                return Wa_vector
            return aero_d_resist

    def __analysis_atmo_cache(self):
        if self.__atmo_model == 0:
            # Модель без атмосферы
            def analysis_atmo(q):
                p, ro, T = (0, 0, 0)
                return p, ro, T
            
            return analysis_atmo

        if self.__atmo_model == 1:
            # Стандартная модель атмосферы
            def analysis_atmo(q):
                h = q.height
                h_values = sorted(self.__atmo_cache.keys())
                h_min = h_values[0]
                h_max = h_values[-1]

                if h <= h_min:
                    # Высота меньше минимальной из таблицы или совпадает с ней
                    h = h_min
                    ro, T, _, _, _ = self.__atmo_cache[h]
                    p = ro * self.__R_g * T
                    return p, ro, T
                if h >= h_max:
                    # Высота превышает максимальную из таблицы или совпадает с ней
                    h = h_max
                    ro, T, _, _, _ = self.__atmo_cache[h]
                    p = ro * self.__R_g * T
                    return p, ro, T
                else:
                    # Высота находится в пределах таблицы
                    if h in h_values:
                        # Высота находится в узле таблицы
                        ro, T, _, _, _ = self.__atmo_cache[h]
                        p = ro * self.__R_g * T
                        return p, ro, T
                    else:
                        # Высота не находится в узле таблицы
                        h_l = None
                        h_r = None
                        for h_s in h_values:
                            if h_s < h:
                                h_l = h_s
                            if h_s > h and h_r is None:
                                h_r = h_s
                                break

                        ro_l, T_l, _, _, _ = self.__atmo_cache[h_l]
                        ro_r, T_r, _, _, _ = self.__atmo_cache[h_r]

                        ro = self.__line_interpolation(h, h_l, h_r, ro_l, ro_r)
                        T = self.__line_interpolation(h, h_l, h_r, T_l, T_r)
                        p = ro * self.__R_g * T

                        return p, ro, T

            return analysis_atmo

        if self.__atmo_model == 2:
            # Стандартная модель атмосферы
            def stand_atmo(h):
                h_values = sorted((self.__atmo_cache['stand_atmo']).keys())
                h_min = h_values[0]
                h_max = h_values[-1]

                if h <= h_min:
                    # Высота меньше минимальной из таблицы или совпадает с ней
                    h = h_min
                    ro, T, _, _, _ = (self.__atmo_cache['stand_atmo'])[h]
                    return ro, T
                if h >= h_max:
                    # Высота превышает максимальную из таблицы или совпадает с ней
                    h = h_max
                    ro, T, _, _, _ = (self.__atmo_cache['stand_atmo'])[h]
                    return ro, T
                else:
                    # Высота находится в пределах таблицы
                    if h in h_values:
                        # Высота находится в узле таблицы
                        ro, T, _, _, _ = (self.__atmo_cache['stand_atmo'])[h]
                        return ro, T
                    else:
                        # Высота не находится в узле таблицы
                        h_l = None
                        h_r = None
                        for h_s in h_values:
                            if h_s < h:
                                h_l = h_s
                            if h_s > h and h_r is None:
                                h_r = h_s
                                break

                        ro_l, T_l, _, _, _ = (self.__atmo_cache['stand_atmo'])[h_l]
                        ro_r, T_r, _, _, _ = (self.__atmo_cache['stand_atmo'])[h_r]

                        ro = self.__line_interpolation(h, h_l, h_r, ro_l, ro_r)
                        T = self.__line_interpolation(h, h_l, h_r, T_l, T_r)

                        return ro, T

            def analysis_atmo(q):
                h = q.height
                ro_st, T_st = stand_atmo(h)
                p_st = ro_st * self.__R_g * T_st

                H = h / 1000
                keys = ['tplot', 'tdavl', 'ttemp', 'tvetz', 'tvetm']

                input_queues = []
                output_queues = []
                for key in keys:
                    _, input_queue, output_queue = self.__process[key]
                    input_queues.append(input_queue)
                    output_queues.append(output_queue)
                    input_queue.put((key, q.geodesy_rad[0], q.geodesy_rad[1], H))

                for queues in input_queues:
                    queues.join()

                results = {}
                for outs in output_queues:
                    key, delta = outs.get()
                    results[key] = delta

                dro = results['tplot']
                dp = results['tdavl']
                Tc = results['ttemp']
                Wz = results['tvetz']
                Wm = results['tvetm']
                
                p = p_st * (1 + dp / 100)
                ro = ro_st * (1 + dro / 100)
                T = Tc + 273.15
                
                print(f"{dro}, {dp}, {Tc}, {Wz}, {Wm}")

                return p, ro, T

            return analysis_atmo

    def __analysis_Cx_cache(self):
        def analysis_Cx(v_norm, T):
            # Скорость звук
            Cs = self.__alpha_cs * np.sqrt(T)
            # Махи
            M = v_norm/Cs

            M_values = sorted(self.__Cx_cache.keys())
            M_min = M_values[0]
            M_max = M_values[-1]

            if M <= M_min:
                M = M_min
                Cx = self.__Cx_cache[M]
                return Cx

            if M >= M_max:
                M = M_max
                Cx = self.__Cx_cache[M]
                return Cx

            else:
                if M in M_values:
                    Cx = self.__Cx_cache[M]
                    return Cx
                else:
                    M_l = None
                    M_r = None

                    for M_s in M_values:
                        if M_s < M:
                            M_l = M_s
                        if M_s > M and M_r is None:
                            M_r = M_s
                    Cx_l = self.__Cx_cache[M_l]
                    Cx_r = self.__Cx_cache[M_r]

                    Cx = self.__line_interpolation(M, M_l, M_r, Cx_l, Cx_r)

                    return Cx

        return analysis_Cx




    @property
    def f_prch(self):
        if self.__f_prch is None:
            def f_prch(q, cached):
                if q.system != 3:
                    # Переводим вектор на всякий случай в гринвичскую СК
                    q = q.in_gr


                r, r_norm, r_ort = self.__r_comp(q)
                v, v_norm, v_ort = self.__speed_comp(q)
                print("cosY", np.dot(r_ort, v_ort))
                clash_of_atmo = np.degrees(np.pi/2 - np.arccos(np.dot(r_ort, v_ort)))
                W_c = (self.__omega_z ** 2) * r
                W_k = -2 * np.cross(np.array([0, 0, self.__omega_z]), v)
                f_accel = W_c + W_k
                if self.__grav_accel is not None:
                    f_accel += self.__grav_accel(r)

                if self.__aero_d_resist is not None:
                    p, ro, T = self.__analysis_atmo(q)
                    Cx = self.__analysis_Cx(v_norm, T)
                    f_accel += self.__aero_d_resist(ro, v_norm, v_ort, Cx, self.__s_mid_otd, self.__m_otd)
                if cached is True:
                    print('ro ', ro)
                    self.__cacher.append(accel=np.linalg.norm(f_accel),
                                         ro = ro,
                                         p = p,
                                         T = T - 273.15,
                                         clash = clash_of_atmo)
                    
                print(f'запись ускорений: {np.linalg.norm(f_accel)} длина {self.__cacher.len_accel_values}')
                return np.concatenate((v, f_accel, [1]))
            self.__f_prch = f_prch
        return self.__f_prch

    def __line_interpolation(self, x, x_l, x_r, y_l, y_r):
        y = y_l + (y_r - y_l) / (x_r - x_l) * (x - x_l)
        return y

    def __errors(self, type_err):
        if type_err is 'initial_model_grav':
            raise ValueError("Ошибка инициализации модели гравитационного поля\n"
                             "Функция не может быть сформирована.\n"
                             "Проверьте входные данные")
        if type_err is 'initial_model_atmo':
            raise ValueError("Ошибка инициализации модели атмосферы.\n"
                             "Функция не может быть сформирована.\n"
                             "Проверьте входные данные")

if __name__ == "__main__":
    pass