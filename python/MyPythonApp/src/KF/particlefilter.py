# coding: utf-8
'''
Created on 2014/02/07

@author: RN-017
'''
from math import log, pow, sqrt
import numpy as np
from scipy.stats import norm
from numpy.random import uniform
from multiprocessing import Pool
import matplotlib.pyplot as plt


class ParticleFilter:
    alpha2 = 0.15 # システムノイズと観測ノイズの分散比
    sigma2 = pow(2,5) # システムノイズの分散
    log_likelihood = 0.0 # 対数尤度
    LSM = 0.0 # ２乗誤差
    TIME = 1
    PR=8 
    
    def __init__(self, PARTICLES_NUM):
        self.PARTICLES_NUM = PARTICLES_NUM # 粒子の数
        self.TEETH_OF_COMB = np.arange(0, 1, float(1.0)/self.PARTICLES_NUM)
        self.weights = np.zeros(self.PARTICLES_NUM)
        self.particles = np.zeros(self.PARTICLES_NUM)
        self.predicted_particles = np.zeros(self.PARTICLES_NUM)
        np.random.seed(555)
        self.predicted_value = []
        self.filtered_value = []
    
    def init_praticles_distribution(self):
        """initialize particles
        x_0|0
        """
        self.particles = norm.rvs(0,1,size=self.PARTICLES_NUM)
        
    def get_system_noise(self):
        """v_t"""
        return norm.rvs(0, self.alpha2*self.sigma2, size=self.PARTICLES_NUM)
        
    def calc_pred_particles(self):
        """calculate system function
        x_t|t-1
        """
        return self.particles + self.get_system_noise()  
        
    def calc_particles_weight(self,y):
        """calculate fitness probabilities between observation value and predicted value
        w_t
        """
        locs = self.calc_pred_particles()
        self.predicted_particles = locs
                  
        self.weights = norm.pdf([y]*self.PARTICLES_NUM, loc=locs,
                                scale=[sqrt(self.sigma2)]*self.PARTICLES_NUM)
                  
    def calc_likelihood(self):
        """alculate likelihood at that point
        p(y_t|y_1:t-1)
        """
        res = sum(self.weights)/self.PARTICLES_NUM
        self.log_likelihood += log(res)
#        return res
      
    def normalize_weights(self):
        """wtilda_t"""
        self.weights = self.weights/sum(self.weights)
      
    def resample(self,y):
        """x_t|t"""
        self.normalize_weights()

        self.memorize_predicted_value()

        # accumulate weight
        cum = np.cumsum(self.weights)
        
        # create roulette pointer 
        base = uniform(0,float(1.0)/self.PARTICLES_NUM)
        pointers = self.TEETH_OF_COMB + base
        
        # select particles
        selected_idx = [np.where(cum>=p)[0][0] for p in pointers]
        """
        pool = Pool(processes=self.PR)
        selected_idx = pool.map(get_slected_particles_idx, ((cum,p) for p in pointers))
        pool.close()
        pool.join()     
        """

#         print "select",selected_idx
        self.particles = self.predicted_particles[selected_idx]                
        self.memorize_filtered_value(selected_idx, y)
        
    
    def memorize_predicted_value(self):
        predicted_value = sum(self.predicted_particles*self.weights)
        self.predicted_value.append(predicted_value)

    def memorize_filtered_value(self, selected_idx, y):
        filtered_value = sum(self.particles*self.weights[selected_idx])/sum(self.weights[selected_idx])
        self.filtered_value.append(filtered_value)
        self.calculate_LSM(y,filtered_value)

    def calculate_LSM(self,y,filterd_value):
        self.LSM += pow(y-filterd_value,2)

    def ahead(self,y):
        """compute system model and observation model"""
        print 'calculating time at %d' % self.TIME
        self.calc_pred_particles()
        self.calc_particles_weight(y)
        self.calc_likelihood()
        self.resample(y)
        self.TIME += 1

def get_slected_particles_idx((cum,p)):
    """multiprocessing function"""
    try:
        return np.where(cum>=p)[0][0]
    
    except Exception, e:
        import sys
        import traceback
        sys.stderr.write(traceback.format_exc())    

if __name__=='__main__':
    pf = ParticleFilter(3000)
    pf.init_praticles_distribution()
    
    data = np.hstack((norm.rvs(0,1,size=20),norm.rvs(2,1,size=60),norm.rvs(-1,0.5,size=20)))
    
    for d in data:
        pf.ahead(d)
    print 'log likelihood:', pf.log_likelihood
    print 'LSM:', pf.LSM
    
    rng = range(100)
    plt.plot(rng,data,label=u"training data")
    plt.plot(rng,pf.predicted_value,label=u"predicted data")
    plt.plot(rng,pf.filtered_value,label=u"filtered data")
    plt.xlabel('TIME',fontsize=18)
    plt.ylabel('Value',fontsize=18)    
    plt.legend() 
    plt.show()