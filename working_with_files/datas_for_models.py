import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def check_csv_file_atmo(model):

    if model == 0:
        pass

    if model == 1:
        # Путь к файлу CSV
        csv_file_path = os.path.join(BASE_DIR, '../data', 'immutable', 'stand_atmo_data.csv')
        # Загрузка CSV файла в DataFrame
        df = pd.read_csv(csv_file_path)

        numbers_st_atm = df['number'].values
        h_values = df['h'].values
        ro_values = df['ro'].values
        T_values = df['T'].values
        zero_d_1 = df['zero1'].values
        zero_d_2 = df['zero2'].values
        cache = {h: (ro, T, num, z1, z2) for h, ro, T, num,   z1, z2 in zip(h_values, ro_values, T_values,
                                                                            numbers_st_atm, zero_d_1, zero_d_2)}
                                                                            

        # print(cache)
        return cache

    if model == 2:
        # Пути к файлам CSV
        csv_file_path_st_atm = os.path.join(BASE_DIR, '../data', 'immutable', 'stand_atmo_data.csv')
        csv_file_path_tplot = os.path.join(BASE_DIR, '../data', 'immutable', 'TPLOT.csv')
        csv_file_path_tdavl = os.path.join(BASE_DIR, '../data', 'immutable', 'TDAVL.csv')
        csv_file_path_ttemp = os.path.join(BASE_DIR, '../data', 'immutable', 'TTEMP.csv')
        csv_file_path_tvetz = os.path.join(BASE_DIR, '../data', 'immutable', 'TVETZ.csv')
        csv_file_path_tvetm = os.path.join(BASE_DIR, '../data', 'immutable', 'TVETM.csv')

        # Загрузка CSV файлов в DataFrame
        df_st_atm = pd.read_csv(csv_file_path_st_atm)
        df_tplot = pd.read_csv(csv_file_path_tplot)
        df_tdavl = pd.read_csv(csv_file_path_tdavl)
        df_ttemp = pd.read_csv(csv_file_path_ttemp)
        df_tvetz = pd.read_csv(csv_file_path_tvetz)
        df_tvetm = pd.read_csv(csv_file_path_tvetm)

        numbers_st_atm = df_st_atm['number'].values
        h_values = df_st_atm['h'].values
        ro_values = df_st_atm['ro'].values
        T_values = df_st_atm['T'].values
        zero_d_1 = df_st_atm['zero1'].values
        zero_d_2 = df_st_atm['zero2'].values

        cache_st_atm = {h: (ro, T, num, z1, z2) for h, ro, T, num,   z1, z2 in zip(h_values, ro_values, T_values,
                                                                            numbers_st_atm, zero_d_1, zero_d_2)}

        numbers_tplot = df_tplot['number'].values
        cr_values = df_tplot['Cr'].values
        k_values_tplot = df_tplot['k'].values
        l_values_tplot = df_tplot['l'].values
        m_values_tplot = df_tplot['m'].values
        n_values_tplot = df_tplot['n'].values

        cache_tplot = {num: (cr, k, l, m, n) for num, cr, k, l, m, n in
                       zip(numbers_tplot, cr_values, k_values_tplot, l_values_tplot, m_values_tplot, n_values_tplot)}

        numbers_tdavl = df_tdavl['number'].values
        cp_values = df_tdavl['Cp'].values
        k_values_tdavl = df_tdavl['k'].values
        l_values_tdavl = df_tdavl['l'].values
        m_values_tdavl = df_tdavl['m'].values
        n_values_tdavl = df_tdavl['n'].values

        cache_tdavl = {num: (cp, k, l, m, n) for num, cp, k, l, m, n in
                       zip(numbers_tdavl, cp_values, k_values_tdavl, l_values_tdavl, m_values_tdavl, n_values_tdavl)}

        numbers_ttemp = df_ttemp['number'].values
        ct_values = df_ttemp['Ct'].values
        k_values_ttemp = df_ttemp['k'].values
        l_values_ttemp = df_ttemp['l'].values
        m_values_ttemp = df_ttemp['m'].values
        n_values_ttemp = df_ttemp['n'].values

        cache_ttemp = {num: (ct, k, l, m, n) for num, ct, k, l, m, n in
                       zip(numbers_ttemp, ct_values, k_values_ttemp, l_values_ttemp, m_values_ttemp, n_values_ttemp)}

        numbers_tvetz = df_tvetz['number'].values
        cwz_values = df_tvetz['Cwz'].values
        k_values_tvetz = df_tvetz['k'].values
        l_values_tvetz = df_tvetz['l'].values
        m_values_tvetz = df_tvetz['m'].values
        n_values_tvetz = df_tvetz['n'].values

        cache_vetz = {num: (cwz, k, l, m, n) for num, cwz, k, l, m, n in
                      zip(numbers_tvetz, cwz_values, k_values_tvetz, l_values_tvetz, m_values_tvetz, n_values_tvetz)}

        numbers_tvetm = df_tvetm['number'].values
        cwm_values = df_tvetm['Cwm'].values
        k_values_tvetm = df_tvetm['k'].values
        l_values_tvetm = df_tvetm['l'].values
        m_values_tvetm = df_tvetm['m'].values
        n_values_tvetm = df_tvetm['n'].values

        cache_vetm = {num: (cwm, k, l, m, n) for num, cwm, k, l, m, n in
                      zip(numbers_tvetm, cwm_values, k_values_tvetm, l_values_tvetm, m_values_tvetm, n_values_tvetm)}

        cache = {
            'stand_atmo': cache_st_atm,
            'tplot': cache_tplot,
            'tdavl': cache_tdavl,
            'ttemp': cache_ttemp,
            'tvetz': cache_vetz,
            'tvetm': cache_vetm,
        }

        # print(cache['tdavl'])

        return cache

def check_csv_file_TCxM(priority):
    if priority == 0:
        # Пуь к файлу CSV
        csv_file_path = os.path.join(BASE_DIR, '../data', 'immutable', 'TCxM.csv')
        # Загрузка CSV файла в DataFrame
        df = pd.read_csv(csv_file_path)

        M_values = df['M'].values
        Cx_values = df['Cxmin'].values

        cache = {M: Cx for M, Cx in zip(M_values, Cx_values)}

        return cache

    if priority == 1:
        # Пуь к файлу CSV
        csv_file_path = os.path.join(BASE_DIR, '../data', 'immutable', 'TCxM.csv')
        # Загрузка CSV файла в DataFrame
        df = pd.read_csv(csv_file_path)

        M_values = df['M'].values
        Cx_values = df['Cxmax'].values

        cache = {M: Cx for M, Cx in zip(M_values, Cx_values)}

        return cache

if __name__ == '__main__':
    import time
    t1 = time.perf_counter()
    check_csv_file_atmo(2)
    t2 = time.perf_counter()
    print(t2-t1)