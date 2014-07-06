# coding: utf-8

import pymc as pm
import numpy as np

ndims = 2
nobs = 20

xtrue = np.random.normal(scale=2., size=1)
ytrue = np.random.normal(loc=np.exp(xtrue), scale=1, size=(ndims, 1))
zdata = np.random.normal(loc=xtrue + ytrue, scale=.75, size=(ndims, nobs))

with pm.Model() as model:
    x = pm.Normal('x', mu=0., sd=1)
    y = pm.Normal('y', mu=pm.exp(x), sd=2., shape=(ndims, 1)) # here, shape is telling us it's a vector rather than a scalar.
    z = pm.Normal('z', mu=x + y, sd=.75, observed=zdata) # shape is inferred from zdata
    
with model:
    start = pm.find_MAP()
    
print("MAP found:")
print("x:", start['x'])
print("y:", start['y'])

print("Compare with true values:")
print("ytrue", ytrue)
print("xtrue", xtrue)

with model:
    step = pm.NUTS()
    
with model: 
    trace = pm.sample(3000, step, start)
    pm.traceplot(trace);