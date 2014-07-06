# coding: utf-8

import numpy as np
import scipy
from numpy import *
import newsfeatures
import multiprocessing
#from multiprocessing.sharedctypes import Value, Array
#from multiprocessing import Manager

FEATURE_NUM = 5
ITERATOR_NUM = 10


#################################################
# Euclidean distance
def difcost_ed(a,b):
    dif=np.sum(np.power(a-b,2))
    return dif

def factorize_ed(v,pc=10,iter_num=50):
    ic=shape(v)[0]
    fc=shape(v)[1]
    
    # Initialize the weight and feature matrices with random values   
    w=matrix([[random.random() for j in range(pc)] for i in range(ic)])
    h=matrix([[random.random() for j in range(fc)] for i in range(pc)])
    
    # Perform operation a maximum of iter times
    for i in range(iter_num):
        wh=w*h
        
        # Calculate the current difference
        cost=difcost_ed(v,wh)
        
        if i%5==0: print cost
        
        # Terminate if the matrix has been fully factorized
        if cost<1*10**(-3): break
        
        # Update feature matrix
        hn=(transpose(w)*v)
        hd=(transpose(w)*w*h)
        
        # Avoid zero division
        hd[hd==0.0]=1*10**(-9)
        
        h=matrix(array(h)*array(hn)/array(hd))
        
        # Update weights matrix
        wn=(v*transpose(h))
        wd=(w*h*transpose(h))
        
        # Avoid zero division
        wd[wd==0.0]=1*10**(-9)
        
        w=matrix(array(w)*array(wn)/array(wd))  
    
    return w,h

#################################################
# Kullback-Leibler divergence
def difcost_kld(a,b):
    a=np.array(a)
    b=np.array(b)
    a[a==0.0] = 1*10**(-9)
    b[b==0.0] = 1*10**(-9)
    
    dif=np.sum(a*(np.log(a)-np.log(b)) - a+b)
    
    return dif

def factorize_kld(v,pc=10,iter_num=50):
    ic=shape(v)[0]
    fc=shape(v)[1]

    # Initialize the weight and feature matrices with random values
    w=matrix([[random.random() for j in range(pc)] for i in range(ic)])
    h=matrix([[random.random() for j in range(fc)] for i in range(pc)])

    # Perform operation a maximum of iter times
    for i in range(iter_num):
        w=matrix(w)
        ho=matrix(h)
        wh=w*ho
    
        w=np.array(w)
        ho=np.array(ho)
        wh=np.array(wh)
        v=np.array(v)
         
        w[w==0.0]=1*10**(-9)
        ho[ho==0.0]=1*10**(-9)
    
        # Calculate the current difference
        cost=difcost_kld(v,wh)
    
        if i%10==0: print cost

        # Terminate if the matrix has been fully factorized
        if cost<1*10**(-3) and cost> (-1)*10**(-3): break

        '''
        calculate common variable
        array(v)/array(wh) → calculate each elements
        matrix of articles number * words
        '''
        # avoid zero division
        wh[wh==0]=1*10**(-9)    # matrix of articles number * word number       
        div_v_wh=matrix(v/wh)   # matrix of articles number * word number


        '''
        Update feature matrix
        '''
        wt=matrix(np.transpose(w)) # matrix of articles number * features → features * article number
        # matrix of (features * article number) *  (articles number * word number)
        # → features * word number
        hc_mat=wt*div_v_wh
        # → word number * features
        hc_matt=np.transpose(hc_mat)
        
        hm=[]
        # calculate hm vector
        hm=np.array( [np.sum(w[:,a]) for a in range(len(w[0,:]))] ) # calculate summation each column → 1*features vector
        hm[hm==0]=1*10**(-9)        
                        
        hconst=[]
        # calculate constant number matrix
        for m in range(len(hc_matt[:,0])):   # loop column number.
            # division row values each column
            # matrix of word number * features
            tmp=np.array(hc_matt[m,:])/hm
            hconst.append( list(tmp[0,:]) )
        
        hconstt=np.transpose(np.array(hconst))  #matrix of features * word number
        h=ho*hconstt

        '''
        Update weights matrix
        '''        
        div_v_wht=matrix(np.transpose(div_v_wh)) # matrix of articles number * words → words * article number
        # matrix of (feature * words) * (words * article number)
        # → features * article number
        wc_mat=matrix(ho)*div_v_wht
        # → article number * features
        wc_matt=np.transpose(wc_mat)
        
        wm=[]
        # calculate wm vector
        wm=np.array( [np.sum(ho[a,:]) for a in range(len(ho[:,0]))] )   # calculate summation each row → 1*features vector
        wm[wm==0]=1*10**(-9)
        
        wconst=[]
        # calculate constant number matrix
        for c in range(len(wc_matt[:,0])):   #loop column number
            # division row values each column
            # matrix of article number * features
            tmp=np.array(wc_matt[c,:])/wm
            wconst.append( list(tmp[0,:]) )
            
        w=w*np.array(wconst)
                
    return w,h

'''
##################################################
# multiprocessing_cpu.py
"""
def _cpu_bound_work():
    i = 0
    while i < 100000000:
        i += 1
"""

class TestProcess(multiprocessing.Process):
    def __init__(self, v, pc=10, iter_num=50):
        self.v = v
        self.pc = pc
        self.iter_num = iter_num
        multiprocessing.Process.__init__(self)
        
    def run(self):
        factorize_kld(self.v, self.pc, self.iter_num)


# run
input_filename = 'C:/HadoopPig/workspace/HadoopPig/works/output/EVA/EvaVerbCount1212/Part-r-00000'

# get data
allv, action_data, verbmatrix, verbs, usr_names = newsfeatures.get_input_data(input_filename)

v = matrix(verbmatrix)
#v = verbmatrix

pc=multiprocessing.Value("i",FEATURE_NUM)
iter_num=multiprocessing.Value("i",ITERATOR_NUM)
V = multiprocessing.Array("d",v)

for _ in xrange(8):
#    process = TestProcess(v, pc = 5, iter_num = 10)
    p = multiprocessing.Process(target=factorize_kld ,args=(v, pc, iter_num,))
#    p = multiprocessing.Process(target=factorize_kld ,args=(v, 5, 10,))
    print "done %d" % _
    p.start()
for process in multiprocessing.active_children():
    print "start"
    process.join()
'''