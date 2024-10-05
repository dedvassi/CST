# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 09:35:15 2024

@author: BurdukovID
"""
import numpy as np
import os
import openpyxl as opxl


class Cacher:
    
    
    def __init__(self):
        self.__q_values = []
        self.__accel_values = []
        self.__ro_values = []
        self.__p_values = []
        self.__T_values = []
        self.__clash_of_atmo = []
        
        self.__speed_values = None
        self.__speed_x_values = None
        self.__speed_y_values = None
        self.__speed_z_values = None
        self.__t_values = None
        self.__height_values = None
        
    def __repr__(self):
        return(f"Cacher("
               f"q_values = {self.__q_values}"
               f"accel_values = {self.__accel_values}"
               f"ro_values = {self.__ro_values}"
               f"p_values = {self.__p_values}"
               f"T_values = {self.__T_values}"
               )
    
    def __getitem__(self, index):
        if (len(self.__q_values) == len(self.__accel_values) and 
        len(self.__q_values) == len(self.__ro_values) and
        len(self.__q_values) == len(self.__p_values) and
        len(self.__q_values) == len(self.__T_values)):
            return {
                    'q_values': self.__q_values[index],
                    'accel_values': self.__accel_values[index],
                    'ro_values': self.__ro_values[index],
                    'p_values': self.__p_values[index],
                    'T_values': self.__T_values[index]
                    }
    def __delitem__(self, index):
        
        del self.__accel_values[index]
        del self.__ro_values[index]
        del self.__p_values[index]
        del self.__T_values[index]
        del self.__clash_of_atmo[index]
        
        self.__invalidata_cached_properties()
        
    def __invalidata_cached_properties(self):
        
        self.__speed_values = None
        self.__t_values = None
        self.__height_values = None
        
    def append(self, q = None, accel = None, ro = None, p = None, T = None,
               clash = None):
        
        if q is not None:
            self.__q_values.append(q)
        if accel is not None:
            self.__accel_values.append(accel)
        if ro is not None:
            self.__ro_values.append(ro)
        if p is not None:
            self.__p_values.append(p)
        if T is not None:
            self.__T_values.append(T)
        if clash is not None:
            self.__clash_of_atmo.append(clash)
    
        self.__invalidata_cached_properties()

    @property
    def q_values(self):
        return self.__q_values

    @property
    def accel_values(self):
        return np.array(self.__accel_values)
    
    @property
    def p_values(self):
        return np.array(self.__p_values)
    
    @property
    def ro_values(self):
        return np.array(self.__ro_values)
    
    @property
    def T_values(self):
        return np.array(self.__T_values)
    
    @property
    def clash_values(self):
        return np.array(self.__clash_of_atmo)
    
    @property
    def len_accel_values(self):
        return len(self.__accel_values)
    
    @property
    def speed_values(self):
        if self.__speed_values is None:
            self.__speed_values = np.array([q.speed_norm for q in self.__q_values])
        return self.__speed_values
    
    @property
    def speed_x_values(self):
        if self.__speed_x_values is None:
            self.__speed_x_values = np.array([q.speed_vector[0] for q in self.__q_values])
        return self.__speed_x_values
    
    @property
    def speed_y_values(self):
        if self.__speed_y_values is None:
            self.__speed_y_values = np.array([q.speed_vector[1] for q in self.__q_values])
        return self.__speed_y_values
    
    @property
    def speed_z_values(self):
        if self.__speed_z_values is None:
            self.__speed_z_values = np.array([q.speed_vector[2] for q in self.__q_values])
        return self.__speed_z_values
    
    @property    
    def t_values(self):
        
        if self.__t_values is None:
            self.__t_values = np.array([q.time for q in self.__q_values])
        return self.__t_values
        
    @property
    def height_values(self):
        if self.__height_values is None:
            self.__height_values = np.array([q.height for q in self.__q_values])
        return self.__height_values


    def __write_row_to_excel(self, file_path, row_data):
        # Проверяем, существует ли файл
        if os.path.exists(file_path):
            # Открываем существующий файл
            workbook = opxl.load_workbook(file_path)
            sheet = workbook.active
        else:
            # Создаем новый файл
            workbook = opxl.Workbook()
            sheet = workbook.active

            # Задаем шапку столбцов, если файл новый
            headers = ['x', 'y', 'z', 'vx', 'vy', 'vz', 't', 'r', 'v', 'h', 'B',  'L', 'a', 'ro', 'T', 'gamma']
            sheet.append(headers)

        # Добавляем новую строку данных
        sheet.append(row_data)

        # Сохраняем файл
        workbook.save(file_path)

    def create_exel(self, file_path):

        for i in range(len(self.q_values)):
            x, y, z, vx, vy, vz, t = self.q_values[i][:7]
            r = self.q_values[i].r_norm
            v = self.q_values[i].speed_norm
            h = self.q_values[i].height
            B, L = self.q_values[i].geodesy_grad
            a = self.accel_values[i]
            ro = self.ro_values[i]
            T = self.T_values[i]
            gamma = self.clash_values[i]

            row_data = [x, y, z, vx, vy, vz, t, r, v, h, B. L, a, ro, T, gamma]

            self.__write_row_to_excel(file_path, row_data)


    