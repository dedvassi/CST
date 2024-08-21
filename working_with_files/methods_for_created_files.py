
from working_with_files.config import *
import os

# # Пути к файлам
# geodesia_const_path = '../data/immutable/geodesia_const.yaml'
# oze_param_path = '../data/immutable/oze_param.yaml'
#
# start_parametrs_path = '../data/default_changeable/system_init_coord.yaml'
# start_iner_sys_path = '../data/default_changeable/start_param.yaml'
# rocket_param_path = '../data/default_changeable/rocket_param.yaml'
# models_param_path = '../data/default_changeable/models_param.yaml'
# method_param_path = '../data/default_changeable/method_param.yaml'
# runge_4_path = '../data/default_changeable/integration/runge_4.yaml'
physical_const_path = '../data/immutable/physical_const.yaml'
#
# geodesia_const_data  = {
#     '0_OmegaZ': 7.292115e-05,
#     '1_fM': 398600.4418e9,
# }
#
# oze_param_data = {
#     '0_a_oze': 6378136.0,
#     '1_polar_compression': 0.0033528037351842955,
#     '2_R_sr': 6371110.0,
#     '3_e2_oze': 0.0066943662,
# }
#
# start_parametrs_data = {
#         '0_x': 2.1489035e5,
#         '1_y': 6.4652197e6,
#         '2_z': 4.9219371e4,
#         '3_vx': 3.5701399e3,
#         '4_vy': 8.0158688e2,
#         '5_vz': 1.5086193e2,
#         '6_t': 196.6801,
#         '7_system': 0,
#         # '8_mod_gravity_pole': 0,
#         # '9_mod_atm': 0
#     }
#
# start_iner_sys_data = {
#      '0_phi_st': 45.943267,
#      '1_lambda_st': 63.652920,
#      '2_h_st': 121.8360,
#      '3_azimut_0': 60.553177
#  }
#
# rocket_param_data = {
#     '0_s_mid_otd': 13.2,
#     '1_m_otd': 4000
# }
#
# models_param_data = {
#         '0_mod_gravity_pole': 0,
#         '1_mod_atm': 0
# }
#
# method_param_data = {
#         '0_runge_4': 1
# }
#
# runge_4_data = {
#     '0_h_ex': 0,
#     '1_dt_0': 1,
#     '2_eps_h': 1
# }
physical_const_data = {
      '0_R_g_specific': 287.05287
}
#
# geodesia_const = Files_con(geodesia_const_path)
# oze_param = Files_con(oze_param_path)
# start_iner_sys = Files_con(start_iner_sys_path)
# start_parametrs = Files_con(start_parametrs_path)
# rocket_param = Files_con(rocket_param_path)
# models_param = Files_con(models_param_path)
# method_param = Files_con(method_param_path)
#
# runge_4 = Files_con(runge_4_path)
physical_const = Files_con(physical_const_path)


# geodesia_const.write_to_scd(geodesia_const_data)
# oze_param.write_to_scd(oze_param_data)
# start_parametrs.write_to_scd(start_parametrs_data)
# start_iner_sys.write_to_scd(start_iner_sys_data)
# rocket_param.write_to_scd(rocket_param_data)
# models_param.write_to_scd(models_param_data)
# method_param.write_to_scd(method_param_data)
# runge_4.write_to_scd(runge_4_data)
physical_const.write_to_scd(physical_const_data)

