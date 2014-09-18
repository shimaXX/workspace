# coding: utf-8

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import tanh, copysign

class RRLAgentForFX:
    TRADING_COST = 0.003
    EPS = 1e-6
        
    def __init__(self,M,rho=0.01,eta=0.1,bias=1.0):
        np.random.seed(555)
        self.M = M # number of lags
        self.weights = np.zeros(self.M+3,dtype=np.float64)
        self.bias = bias # bias term
        self.rho = rho
        self.eta = eta
        self.price_diff = np.zeros(self.M+1) # r_t
        
        self.pre_price = None
        self.pre_signal = 0
        
        self.pre_A = 0.0
        self.pre_B = 0.0
        self.pre_gradient_F = 0.0
        
        # result store
        self.signal_store = []
        self.profit_store = []
        self.dsr_store = []
        self.sr_store = []
        self.cumulative_profit = 0.0
        
    def train_online(self, price):
        self.calculate_price_diff(price)
        signal, self.F_t_value = self.select_signal()
        print signal
        self.calculate_return(signal)
        self.update_parameters()
        self.pre_price = price
        self.pre_signal = signal
        
        # store result
        self.signal_store.append(signal)
                    
    def calculate_price_diff(self,price):
        r = price - self.pre_price if self.pre_price is not None else 0
        self.price_diff[:self.M] = self.price_diff[1:]
        self.price_diff[self.M] = r
        
    def calculate_return(self,signal):
        R_t = self.pre_signal*self.price_diff[-1]
        R_t -= self.TRADING_COST*abs(signal - self.pre_signal)
        self.return_t = R_t
        
        self.cumulative_profit += R_t
        self.profit_store.append(self.cumulative_profit)
            
    def select_signal(self):
        values_sum = (self.weights[:self.M+1]*self.price_diff).sum()
        values_sum += self.weights[-2]*self.pre_signal
        values_sum += self.bias*self.weights[-1]
        
        F_t_value = tanh(values_sum)
        return copysign(1, F_t_value ), F_t_value
                                            
    def update_parameters(self):
        # update weight
        self.weights += self.rho*self.calculate_gradient_weights()
        print "weight",self.weights

        # update moment R_t
        self.update_R_moment()

    def calculate_gradient_weights(self):
        """ differentiate between D_t and w_t """
        denominator = self.pre_B-self.pre_A**2
        if denominator!=0:
            diff_D_R = self.pre_B-self.pre_A*self.return_t
            diff_D_R /= (denominator)**1.5
        else:
            diff_D_R = 0
        
        gradient_F = self.calculate_gradient_F()
        print gradient_F

        #diff_R_F = -self.TRADING_COST
        #diff_R_F_{t-1} = self.price_diff[-1] - self.TRADING_COST
        delta_weights = -self.TRADING_COST*gradient_F
        delta_weights += ( self.price_diff[-1] - self.TRADING_COST) \
                                                    *self.pre_gradient_F
        delta_weights *= diff_D_R
        self.pre_gradient_F = gradient_F
        return delta_weights
        
    def calculate_gradient_F(self):
        """ differentiate between F_t and w_t """
        diff_tnah = 1-self.F_t_value**2

        diff_F_w = diff_tnah*( np.r_[ self.price_diff, self.pre_signal, self.bias ] )
        diff_F_F = diff_tnah*self.weights[-2]

        return diff_F_w + diff_F_F*self.pre_gradient_F

    def update_R_moment(self):
        delta_A = self.return_t - self.pre_A
        delta_B = self.return_t**2 - self.pre_B
        A_t = self.pre_A + self.eta*delta_A # A_t. first moment of R_t.
        B_t = self.pre_B + self.eta*delta_B # B_t. second moment of R_t.
        self.sr_store.append(A_t/B_t)
        self.calculate_dsr(delta_A, delta_B)
        
        self.pre_A = A_t
        self.pre_B = B_t

    def calculate_dsr(self,delta_A,delta_B):
        dsr = self.pre_B*delta_A - 0.5*self.pre_A*delta_B
        dsr /= (self.pre_B-self.pre_A**2)**1.5
        self.dsr_store.append(dsr)

if __name__=='__main__':
    M = 8
    fx_agent = RRLAgentForFX(M,rho=0.01,eta=0.01,bias=0.25)
    
    ifname = os.getcwd()+'/input/quote.csv'
    data = pd.read_csv(ifname)
    train_data = data.ix[:3000,'USD']
    
    for price in train_data.values:
        fx_agent.train_online(price)
    
    plt.plot(range(len(train_data.values)), train_data.values)
    plt.show()    
    
    plt.plot(range(len(fx_agent.signal_store)), fx_agent.signal_store)
    plt.show()
    
    plt.plot(range(len(fx_agent.profit_store)), fx_agent.profit_store)
    plt.show()    
    
    plt.plot(range(len(fx_agent.dsr_store)), fx_agent.dsr_store)
    plt.ylim([-5,5])
    plt.show()
    
    plt.plot(range(len(fx_agent.sr_store)), fx_agent.sr_store)
    plt.ylim([-0.2,0.2])
    plt.show()    