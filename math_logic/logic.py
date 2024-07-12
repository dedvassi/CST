import numpy as np
from math_obj.q_vector import Q_v_state
from math_obj.matrix import Matrix
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
    print(q.in_st.height)
    print(q.in_ekv.height)
    print(q.in_gr.height)
    # q_st_in = Q.q_st_in
    # q_ekv_in = Q.q_ekv_in
    # q_gr = Q.q_gr
    #
    # print(f'vector in st_in {q_st_in}')
    # print(q_st_in.in_gr)



    # print(f'h {q_st_in.height}')
    # print(f'proj {q_st_in.proj_point}')
    #
    # print(f'vector in ekv_in {q_ekv_in}')
    # print(f'h {q_ekv_in.height}')
    # print(f'proj {q_ekv_in.proj_point}')
    #
    # print(f'vector in gr {q_gr}')
    # print(f'h {q_gr.height}')
    # print(f'proj {q_gr.proj_point}')

    # print()
    # print(f'vector in gr sys {Q.q_gr}')
    # print()
    # print(f'vector in ekv iner sys {Q.q_ekv_in}')
    # print()
    #
    # ksi_gr = np.array(Q.q_gr[:3])
    # print(ksi_gr)

    # f = F_prch_maker(1,2,3,4)
    # f.__s





if __name__ == '__main__':
    main()
    