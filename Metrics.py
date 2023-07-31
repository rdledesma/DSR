#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 15:35:45 2023
info@inglescientifico.com.ar
+54 911  008 1287
@author: dario
"""
import numpy as np

class Metrics:
    ##X debe ser dato medido
    ##Y debe ser dato estimado - predecido
    
    def __init__(self, X, Y):
        self.X = np.array(X)
        self.Y = np.array(Y)
    
        #rrmse
    def relative_root_mean_squared_error(self):

        num = np.sum(np.square(self.X - self.Y))
        den = np.sum(np.square(self.Y))
        squared_error = num/den
        rrmse_loss = np.sqrt(squared_error)
        return rrmse_loss * 100
    
    def relative_root_mean_square_deviation(self):
        deviation = np.sqrt(sum((self.Y - self.X)**2)/len(self.X))
        return deviation/ np.mean(self.X) * 100

    def mean_absolute_deviation(self):
        return sum(abs(self.Y - self.X))

    def MBE(self):
        '''
        Parameters:
            y_true (array): Array of observed values
            y_pred (array): Array of prediction values
    
        Returns:
            mbe (float): Biais score
        '''
        y_true = np.array(self.X)
        y_pred = np.array(self.Y)
        y_true = y_true.reshape(len(y_true),1)
        y_pred = y_pred.reshape(len(y_pred),1)   
        diff = (y_true-y_pred)
        mbe = diff.mean()
        return mbe

    def showMetrics(self):
        print(f'rRMSE ==> {self.relative_root_mean_squared_error():.4f} %')
        print(f'rRMSD ==> {self.relative_root_mean_square_deviation():.4} %')
        print(f'MAD ==> {self.mean_absolute_deviation():.4f}')

