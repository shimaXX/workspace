# coding: utf-8

import numpy as np
from numpy.random import normal
from math import log
import pylab 
import scipy.stats as stats


x = normal(0.002,2, 1000)
y = x + normal(0, 0.0001, 1000)

stats.probplot(x, dist="norm", plot=pylab) # check similarity measure of normal distribution
pylab.show()

res = y-x-np.mean(y-x)
res_var = np.var(res)

x_var = np.var(x)
print x_var

print 0.5*log(1+x_var/res_var, 2)