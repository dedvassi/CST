import pandas as pd
import threading
def check_csv_file_atmo(model):

    if model == 0:
        pass

    if model == 1:
        # Путь к файлу CSV
        csv_file_path = '../data/immutable/stand_atmo_data.csv'
        # Загрузка CSV файла в DataFrame
        df = pd.read_csv(csv_file_path)

        h_values = df['h'].values
        ro_values = df['ro'].values
        T_values = df['T'].values

        cache = {h: (ro, T) for h, ro, T in zip(h_values, ro_values, T_values)}

        return cache

    if model == 2:
        # Пути к файлам CSV
        csv_file_path_st_atm = '../data/immutable/stand_atmo_data.csv'
        csv_file_path_tplot = '../data/immutable/TPLOT.csv'
        csv_file_path_tdavl = '../data/immutable/TDAVL.csv'
        csv_file_path_ttemp = '../data/immutable/TTEMP.csv'
        csv_file_path_tvetz = '../data/immutable/TVETZ.csv'
        csv_file_path_tvetm = '../data/immutable/TVETM.csv'

        # Загрузка CSV файлов в DataFrame
        df_st_atm = pd.read_csv(csv_file_path_st_atm)
        df_tplot = pd.read_csv(csv_file_path_tplot)
        df_tdavl = pd.read_csv(csv_file_path_tdavl)
        df_ttemp = pd.read_csv(csv_file_path_ttemp)
        df_tvetz = pd.read_csv(csv_file_path_tvetz)
        df_tvetm = pd.read_csv(csv_file_path_tvetm)

        h_values = df_st_atm['h'].values
        ro_values = df_st_atm['ro'].values
        T_values = df_st_atm['T'].values

        cache_st_atm = {h: (ro, T) for h, ro, T in zip(h_values, ro_values, T_values)}

        cr_values = df_tplot['Cr'].values
        k_values = df_tplot['k'].values
        l_values = df_tplot['l'].values
        m_values = df_tplot['m'].values
        n_values = df_tplot['n'].values

        cache_tplot = {cr: (k, l, m, n) for cr, k, l, m, n in zip(cr_values, k_values, l_values, m_values, n_values)}

        cp_values = df_tdavl['Cp'].values
        k_values = df_tdavl['k'].values
        l_values = df_tdavl['l'].values
        m_values = df_tdavl['m'].values
        n_values = df_tdavl['n'].values

        cache_tdavl = {cp: (k, l, m, n) for cp, k, l, m, n in zip(cp_values, k_values, l_values, m_values, n_values)}

        ct_values = df_ttemp['Ct'].values
        k_values = df_ttemp['k'].values
        l_values = df_ttemp['l'].values
        m_values = df_ttemp['m'].values
        n_values = df_ttemp['n'].values

        cache_ttemp = {ct: (k, l, m, n) for ct, k, l, m, n in zip(ct_values, k_values, l_values, m_values, n_values)}

        cwz_values = df_tvetz['Cwz'].values
        k_values = df_tvetz['k'].values
        l_values = df_tvetz['l'].values
        m_values = df_tvetz['m'].values
        n_values = df_tvetz['n'].values

        cache_vetz = {cwz: (k, l, m, n) for cwz, k, l, m, n in zip(cwz_values, k_values, l_values, m_values, n_values)}


        cwm_values = df_tvetm['Cwm'].values
        k_values = df_tvetm['k'].values
        l_values = df_tvetm['l'].values
        m_values = df_tvetm['m'].values
        n_values = df_tvetm['n'].values

        cache_vetm = {cwm: (k, l, m, n) for cwm, k, l, m, n in zip(cwm_values, k_values, l_values, m_values, n_values)}

        cache = {
            'stand_atmo': cache_st_atm,
            'tplot': cache_tplot,
            'tdavl': cache_tdavl,
            'ttemp': cache_ttemp,
            'tvetz': cache_vetz,
            'tvetm': cache_vetm,
        }

        print(cache)
        return cache

def check_csv_file_TCxM(priority):
    if priority == 0:
        # Пуь к файлу CSV
        csv_file_path = '../data/immutable/TCxM.csv'
        # Загрузка CSV файла в DataFrame
        df = pd.read_csv(csv_file_path)

        M_values = df['M'].values
        Cx_values = df['Cxmin'].values

        cache = {M: Cx for M, Cx in zip(M_values, Cx_values)}

        return cache

    if priority == 1:
        # Пуь к файлу CSV
        csv_file_path = '../data/immutable/TCxM.csv'
        # Загрузка CSV файла в DataFrame
        df = pd.read_csv(csv_file_path)

        M_values = df['M'].values
        Cx_values = df['Cxmax'].values

        cache = {M: Cx for M, Cx in zip(M_values, Cx_values)}

        return cache

