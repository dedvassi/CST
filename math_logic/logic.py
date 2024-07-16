import numpy as np
from math_obj.q_vector import Q_v_state
from math_obj.matrix import Matrix
from math_obj.f_prch import F_prch_maker
from math_obj.integraters import integrators
from working_with_files.config import Files_con
# from math_obj.f_prch import F_prch_maker


def main():
    # Инициализируем векторм состояний
    file_start_param = '../con_files/last_init_data.yaml' ##### СДЕЛАТЬ ЧТОБЫ ОН В БУДУЩЕМ СЮДА ПЕРЕДВАЛАСЯ ИЗ ПОЛЬЗОВАТЕЛЬСКОГО ИНТЕРФЕЙСА
    file_iner_sys = '../con_files/start_iner_sys_data.yaml'
    file_geodesia_const = '../con_files/geodez_const.yaml'
    
    # Экземпляры класса Files_con из пакета working_with_files для открытия yaml файлов
    sis = Files_con(file_iner_sys)                      # Работает с файлом содержащим информацию о старте
    start_param = Files_con(file_start_param)           # Работает с файлом содержащим информацию о начальном состоянии
    geodez_const = Files_con(file_geodesia_const)      # Работает с файлом содержащим геодезические постоянные 0_OmegaZ 1_R_sr 2_a_oze 3_alpha 4_e2_oze

    print(f'Параметры старта {sis.init_data}')
    print()
    print(f'Параметры начального состояния {start_param.init_data}')
    print()
    print(f'Геодезия {geodez_const.init_data}')
    print()

    # Экземпляр класса матриц перехода
    matrix = Matrix(sis.init_data, np.concatenate((np.array([geodez_const.init_data[0]]),np.array([start_param.init_data[6]]))))
    print(f'Матрица d {matrix.d}')
    print()
    print(f'Матрица T_G {matrix.T_G}')
    print()

    # Экземпляр класса вектора состояния
    q = Q_v_state(matrix, np.array(start_param.init_data[:7]), start_param.init_data[7])()
    f_prch = F_prch_maker(0, 0, 0)()
    
    integr = integrators()
    runge_4 = integr.runge_4

    q_values, f_accel_values = runge_4(f_prch, q)
    #print(f"{q}\n")
    #print(f"{q.system}\n")
    #print(f"{q.height}\n")
    #print(f"{q.speed}\n")
    #print(f"{q.proj_point}\n")

    #print(f"{q.in_st.in_gr.__hash__}\n")
    #print(f"{q.in_gr.__hash__}\n")
    #print(f"{q.in_st.system}\n")
    #print(f"{q.in_st.height}\n")
    #print(f"{q.in_st.speed}\n")
    #print(f"{q.in_st.proj_point}\n")

    #print(f"{q.in_ekv}\n")
    #print(f"{q.in_ekv.system}\n")
    #print(f"{q.in_ekv.height}\n")
    #print(f"{q.in_ekv.speed}\n")
    #print(f"{q.in_ekv.proj_point}\n")

    #print(f"{q.in_gr}\n")
    #print(f"{q.in_gr.system}\n")
    #print(f"{q.in_gr.height}\n")
    #print(f"{q.in_gr.speed}\n")
    #print(f"{q.in_gr.proj_point}\n")

    #sum = q.in_st + q.in_gr
    #print(sum)
    #print(q.in_st)
    #print(q.in_gr)
    #print(q.in_gr.r)

    #a = []
    #for i in range(5):
    #    q += i*q.value
    #    a.append(q)
    #for i in a:
    #    print(f'{a.index(i)} ', i.__repr__)

    #print(q.speed)
    #print((a[4]).__repr__)



if __name__ == '__main__':
    main()
    