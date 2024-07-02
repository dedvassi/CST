import yaml
import numpy as np

class Files_con:
    """description of class"""
    
    def __init__(self, f_path):
        self.__file_path = f_path
        self.__init_data = None

    @property
    def file_path(self):
        return self.__file_path

    @file_path.setter
    def file_path(self, value):
        self.__file_path = value
        self.__init_data = None
    
    @property
    def init_data(self):
        if self.__init_data is None:
            self.__init_data = self.read_sisd_to_numpy()
        return self.__init_data

    def write_to_scd(self, data):
        """
        Записывает данные в YAML файл.

        Параметры:
        data (dict): Словарь с данными для записи.
        """

        with open(self.file_path, 'w') as file:
            yaml.dump(data, file)
        self.__init__(self.file_path)

    def read_sisd_to_numpy(self):
        """
        Читает YAML файл и преобразует содержащиеся в нем константы в массив NumPy.
        Возвращает:
        np.array: Массив NumPy с константами из файла.

        '0_phi_st'

        '1_lambda_st'

        '2_h_st'

        '3_azimut_0'
        """
        
        with open(self.file_path, 'r') as file:
            data = yaml.safe_load(file)
        return np.array(list(data.values()))


