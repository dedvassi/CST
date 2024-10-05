import numpy as np
import os
import matplotlib.pyplot as plt
from math_obj.q_vector import Q_v_state
from math_obj.matrix import Matrix
from math_obj.f_prch import F_prch_maker
from math_obj.integraters import integrators
from working_with_files.config import Files_con
from math_logic.cacher import Cacher
from math_logic.geodesy_line import geodesy_line
import time
import asyncio

def main():
    print(np.array([]))
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Инициализируем векторм состояний
    file_start_param = os.path.join(BASE_DIR, '../data/changeable', 'system_init_coord.yaml') ##### СДЕЛАТЬ ЧТОБЫ ОН В БУДУЩЕМ СЮДА ПЕРЕДВАЛАСЯ ИЗ ПОЛЬЗОВАТЕЛЬСКОГО ИНТЕРФЕЙСА
    file_iner_sys = os.path.join(BASE_DIR, '../con_files', 'start_iner_sys_data.yaml')
    file_geodesia_const = os.path.join(BASE_DIR, '../con_files', 'geodez_const.yaml')
    
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
    cacher = Cacher()
    cacher_st = Cacher()
    cacher_natmo = Cacher()

    q = Q_v_state(matrix, [-4.27502926e+06, -1.41255307e+06, -4.65376552e+06,  1.64150833e+03, -2.61619015e+03, -3.84657312e+03,  6.20206184e+02], 3)()
    # print(q.in_gr)
    # print(q.geodesy_grad)
    # time.sleep(1000)
    f_prch = F_prch_maker(0, 2, cacher)()
    # f_prch_st = F_prch_maker(0, 1, cacher_st)()
    # f_prch_natmo = F_prch_maker(0, 0, cacher_natmo)()
    #
    integr = integrators(cacher)
    # integr_st = integrators(cacher_st)
    # integr_natmo = integrators(cacher_natmo)
    #
    runge_4 = integr.runge_4
    # runge_4_st = integr_st.runge_4
    # runge_4_natmo = integr_natmo.runge_4
    #
    runge_4(f_prch, q)
    # runge_4_st(f_prch_st, q)
    # runge_4_natmo(f_prch_natmo, q)
    # q_values = cacher.q_values
    # q_values_st = cacher_st.q_values
    # q_values_natmo = cacher_natmo.q_values
    #
    # print(f"Длина напрямую: {np.linalg.norm((q_values_natmo[-1]).r_vector - (q_values[-1]).r_vector)}")
    # print(f"геодезия по глобальной атмосфере : {(q_values[-1]).geodesy_grad}")
    # print(f"геодезия без атмосферы : {(q_values_natmo[-1]).geodesy_grad}")
    # # geodesy_line(q_values[-1], q_values_natmo[-1])
    #
    # print(f"конечный веткорв {q_values[-1]}, его геодезия {(q_values[-1]).geodesy_grad}")

    # speed_values = cacher.speed_values
    # p_values = cacher.p_values
    # ro_values = cacher.ro_values
    # T_values = cacher.T_values
    # clash_values = cacher.clash_values
    # accel_values = cacher.accel_values
    # height_values = cacher.height_values
    # t_values = cacher.t_values
    #
    # speed_x = cacher.speed_x_values
    # speed_y = cacher.speed_y_values
    # speed_z = cacher.speed_z_values
    #
    #
#    height = np.array([q.height for q in q_values])
#    speed = np.array([np.linalg.norm(q.speed) for q in q_values])
#    t = np.array([q[-1] for q in q_values])


    # fig = plt.figure()
    # ax1 = fig.add_subplot(321)
    # ax1.plot(t_values, height_values)
    # ax1.set_title("h(t)")
    # ax1.set_xlabel("t, с")
    # ax1.set_ylabel("h, м")
    #
    # ax2 = fig.add_subplot(322)
    # ax2.plot(speed_values, height_values)
    # ax2.set_title("V(t)")
    # ax2.set_xlabel("t, с")
    # ax2.set_ylabel("V, м/с")
    #
    # ax3 = fig.add_subplot(323)
    # ax3.plot(accel_values/9.81, height_values)
    # ax3.set_title("accel(t)")
    # ax3.set_xlabel("t, с")
    # ax3.set_ylabel("a, м/с^2")
    #
    # ax4 = fig.add_subplot(324)
    # ax4.plot(np.abs(clash_values), height_values/1000)
    # ax4.set_title("clash(t)")
    # ax4.set_xlabel("h, КМ")
    # ax4.set_ylabel("угол, град")
    #
    # ax5 = fig.add_subplot(325)
    # ax5.plot(height_values, ro_values)
    # ax5.set_title("ro(t)")
    # ax5.set_xlabel("t, с")
    # ax5.set_ylabel("ro, кг/м^3")
    #
    # ax6 = fig.add_subplot(326)
    # ax6.plot(T_values, height_values)
    # ax6.set_title("T(t)")
    # ax6.set_xlabel("t, с")
    # ax6.set_ylabel("T, К")
    #
    # fig1 = plt.figure()
    # ax11 = fig1.add_subplot(311)
    # ax11.plot(t_values, speed_x)
    # ax11.set_title("Vx(t)")
    # ax11.set_xlabel("t, с")
    # ax11.set_ylabel("Vx, м/с")
    #
    # ax12 = fig1.add_subplot(312)
    # ax12.plot(t_values, speed_y)
    # ax12.set_title("Vy(t)")
    # ax12.set_xlabel("t, с")
    # ax12.set_ylabel("Vy, м/с")
    #
    # ax13 = fig1.add_subplot(313)
    # ax13.plot(t_values, speed_z)
    # ax13.set_title("Vz(t)")
    # ax13.set_xlabel("t, с")
    # ax13.set_ylabel("Vz, м/с")
    #
    # fig2 = plt.figure()
    # ax111 = fig2.add_subplot(111)
    # ax111.plot(p_values, height_values)
    # ax111.set_title("P(h)")
    # ax111.set_xlabel("P, Па")
    # ax111.set_ylabel("h, м")
    
    
    
#    plt.plot(t, speed)
    plt.show()


if __name__ == '__main__':
    t1 = time.time()
    main()
    t2 = time.time()
    print(t2 - t1)