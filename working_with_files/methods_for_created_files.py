
from working_with_files.config import *
import os

# Пути к файлам
start_parametrs_path = '../con_files/last_init_data.yaml'
start_iner_sys_path = '../con_files/start_iner_sys_data.yaml'


start_parametrs_data = {
        '0_x': 2.1489035e5,
        '1_y': 6.4652197e6,
        '2_z': 4.9219371e4,
        '3_vx': 3.5701399e3,
        '4_vy': 8.0158688e2,
        '5_vz': 1.5086193e2,
        '6_t': 196.6801,
        '7_system': 1,
        '8_mod_gravity_pole': 1,
        '9_mod_atm': 1,
    }

start_iner_sys_data = {
     '0_phi_st': 45.943267,
     '1_lambda_st': 63.652920,
     '2_h_st': 121.8360,
     '3_azimut_0': 60.553177
 }

start_iner_sys = Start_iner_sys(start_iner_sys_path)
start_parametrs = Start_parametrs(start_parametrs_path)

start_parametrs.write_to_last_init(start_parametrs_data)
start_iner_sys.write_to_scd(start_iner_sys_data)