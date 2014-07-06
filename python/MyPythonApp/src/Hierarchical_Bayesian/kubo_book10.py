# coding: utf-8

import pymc
from pymc.distributions.timeseries import *
import numpy
import pandas
import scipy
from scipy import optimize

import pandas
import matplotlib.pyplot as plt
import pylab
from pylab import hist, show, linspace, plot, figure
import theano.tensor as t


src = "http://hosho.ees.hokudai.ac.jp/~kubo/stat/iwanamibook/fig/hbm/data7a.csv"

def fetch_data(src):
    return pandas.read_csv(src)

def tinvlogit(x):
    return t.exp(x) / (1 + t.exp(x))

# fig 10.1(B)
def draw_figure_10_1():
    df = fetch_data(src)
    hist(df['y'], bins=9, color='w')
    xx = linspace(0, 8, 9)
    yy = scipy.stats.binom.pmf(xx, 8, 0.504) * 100
    plot(xx, yy, 'ko-')
"""    
figure(figsize(8,7))
draw_figure_10_1()
plt.show()
"""

df = fetch_data(src)

with pymc.Model() as model:
    ### pp.228のBUGSコード相当
    Y = df['y'].values
    N = len(Y)
    
    ### hyperpriors
    s = pymc.Uniform(name="s", lower=1.0e-2, upper=1.0e+2, testval=0.01)
    b = pymc.Normal(name='b', mu=0.01, tau=1.0e+2)
    
    ### priors
    r = [pymc.Normal(name="r_{0}".format(i), mu=0., tau=s**-2) for i in range(N)]
    p = tinvlogit(b + r)

    obs = pymc.Binomial(name="obs", n=8, p=p, observed=Y)

#H = model.fastd2logp()
    
with model:
    start = pymc.find_MAP(vars=[s], fmin=optimize.fmin_l_bfgs_b)

# with model:
#     step = pymc.NUTS(model.vars, scaling=start)

# かなり時間がかかるので実行時には注意すること！
def run(n=3000):
    if n == "short":
        n = 50
    with model: 
        step = pymc.HamiltonianMC(model)
        trace = pymc.sample(n, step, start)
    # サンプリング過程の可視化
    #fig = pymc.traceplot(trace, lines={'alpha': 1, 'beta': 2, 'sigma': .5});
    
if __name__=='__main__':
    run()