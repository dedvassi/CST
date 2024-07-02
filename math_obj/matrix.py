import numpy as np
class Matrix:
    """Инициализирует матрицы перехода между системами
        
        - Матрица d инициализируется единоразово и не изменяется в рамках сессии. Для ее получения использовать:

            >>d = self.d (пример с присвоением значения переменной d)
       
        - Матрица T_G динамична. Для обновления и полученяи ее нового значения следует использовать :

            >>self.data_T_G = new_value*
            >>T_G = self.T_G (пример с присвоением значения переменной T_G)

        *new_value - массив numpy (np.ndarray), содержит угловую скорость вращения Земли и время в соответствующем порядке

    """
    def __init__(self, dt_1, dt_2):
        self.__data_d = dt_1
        self.__d = None

        self.__data_T_G = dt_2
        self.__T_G = None

        self.Ω = dt_2[0]
    
    @property
    def d(self):
        if self.__d is None:
            Φ, λ, _, P = self.__data_d[:4]  * np.pi / 180
            d11 = (-1) * np.cos(P) * np.sin(Φ) * np.cos(λ) - np.sin(P) * np.sin(λ)
            d12 = (-1) * np.cos(P) * np.sin(Φ) * np.sin(λ) + np.sin(P) * np.cos(λ)
            d13 = np.cos(P) * np.cos(Φ)

            d21 = np.cos(Φ) * np.cos(λ)
            d22 = np.cos(Φ) * np.sin(λ)
            d23 = np.sin(Φ)

            d31 = np.sin(P) * np.sin(Φ) * np.cos(λ) - np.cos(P) * np.sin(λ)
            d32 = np.sin(P) * np.sin(Φ) * np.sin(λ) + np.cos(P) * np.cos(λ)
            d33 = (-1) * np.sin(P) * np.cos(Φ)

            self.__d = np.array([[d11, d12, d13],
                             [d21, d22, d23],
                             [d31, d32, d33]])

        return self.__d
    
    @property
    def data_T_G(self):
        return self.__data_T_G
    @data_T_G.setter
    def data_T_G(self, value):
        self.__data_T_G = value
        self.__T_G = None
        a = m.T_
    @property
    def T_G(self):
        if self.__T_G is None:
            Ω = self.data_T_G[0]
            t = self.data_T_G[1] # извлекает время
            self.__T_G = np.array([
                [np.cos(Ω * t), np.sin(Ω * t), 0],
                [-np.sin(Ω * t), np.cos(Ω * t), 0],
                [0, 0, 1]
            ])
        return self.__T_G

#a = Matrix(np.array([45.943267, 63.65292, 121.836, 60.553177]), np.array([2, 12]))
#print(a.data_2)
#print(a.T_G)
#print(a.d)
#print(a.T_G)
#a.data_2 = [0, 10]
#print(a.data_2)
#print(a.T_G)
#print(a.d.T)