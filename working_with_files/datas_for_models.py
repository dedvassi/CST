import pandas as pd
def check_csv_file_atmo(model, month):

    if model == 0:
        pass

    if model == 1:
        # Путь к файлу CSV
        csv_file_path = '../data/immutable/stand_atmo_data.csv'
        # Загрузка CSV файла в DataFrame
        df = pd.read_csv(csv_file_path)

        h_values = df['h [м]'].values
        ro_values = df['ro [кг/м3]'].values
        T_values = df['T [градус K]'].values

        cache = {h: (ro, T) for h, ro, T in zip(h_values, ro_values, T_values)}

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

