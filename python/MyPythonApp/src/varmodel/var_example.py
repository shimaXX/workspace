# coding: utf-8

import pandas as pd
import numpy as np
import statsmodels.api as sm
import pylab
from statsmodels.tsa.base.datetools import dates_from_str
from statsmodels.tsa.vector_ar.var_model import VAR

mdata = sm.datasets.macrodata.load_pandas().data
dates = mdata[['year', 'quarter']].astype(int).astype(str)
quarterly = dates["year"] + "Q" + dates["quarter"]
quarterly = dates_from_str(quarterly)

mdata = mdata[['realgdp','realcons','realinv']]
mdata.index = pd.DatetimeIndex(quarterly)
data = np.log(mdata).diff().dropna() # log difference

# make a VAR model
model = VAR(data)
results = model.fit(2)
print results.summary()
results.plot()
results.plot_acorr() #autocorrelation 

model.select_order(15)
results = model.fit(maxlags=15, ic='aic')

irf = results.irf(10)
irf.plot(orth=True) #Orthogonalization

pylab.show()