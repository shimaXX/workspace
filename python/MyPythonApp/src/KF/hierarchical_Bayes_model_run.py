# coding: utf8

import sys
import numpy.random as npr
from numpy.oldnumeric.linear_algebra import inverse
import scipy
from scipy import linalg
import random
import scipy.stats.distributions as dis
from scipy.stats import uniform,chi2,invgamma
import scipy.stats as ss
import numpy as np
import math
from scipy.linalg import inv,cholesky,det
import scipy.optimize as so
import hierarchical_Bayes_model as hbm
from multiprocessing import *
from numpy import genfromtxt
#
#
# データインポートファイルパスの定義
inpt_filename = 'D:/workspace/python/MyPythonApp/works/input/input.txt'

### データinput-------------------
# Dデータの取得（共通性を使って個人毎のパラメータを推定するのに必要なデータ）
y = genfromtxt(inpt_filename, delimiter=',').flatten()
print "done input"
### ------------------------------
#
# ランダムシードの発生
random.seed(555)
#
##--定数の定義-------
SEASONALYTY = 7 #季節変動の周期
limy = 1e20 # 欠測とみなす数値の境界
k = 2 # トレンド成分モデルの次数
N = len(y)
##-------------------
print "done data shape"
###------------------------------------------------------------

## 初期値の設定------------------------------
param = hbm.FGHset(0, k, SEASONALYTY, 0)
L = 1
R = np.identity(L)
m = np.array(param['m'])
F = np.array(param['MatF'])
G = np.array(param['MatG'])
H = np.array(param['MatH'])
Q0 =np.array(param['MatQ'])


def Kalman_filtering(y):
    # TAU2の最尤推定を求める数値計算------------------------------
    ISW = 0; XPS=0;
    tau0 = [0 for i in xrange(k)]
 
    mybounds=[(1e-4,1e2) for i in xrange(k)]
    LLF1 = so.fmin_l_bfgs_b(hbm.LogL, x0=tau0,
                            args=(y, F, H, G, R, limy, ISW, k, m, N, Q0),
                            bounds=mybounds, approx_grad=True)         
    # TAU2の最尤推定
    TAU2=LLF1[0]; #LLF1['x']

    # カルマンフィルタ
    Q = hbm.Qset(Q0 ,TAU2);
    XF0 = np.zeros(m); VF0 = np.float(10) * np.identity(m)
    OSW = 1
    LLF2 = hbm.KF(y, XF0, VF0, F, H, G, Q, R, limy, ISW, OSW, m, N)
    XPS = LLF2['XPS']; XFS = LLF2['XFS']
    VPS = LLF2['VPS']; VFS = LLF2['VFS']
    SIG2 = LLF2['Ovar']; GSIG2 = 1
    # 平滑化 ----------------------------------------------------------
    LLF3 = hbm.SMO(XPS, XFS, VPS, VFS, F, GSIG2, k, SEASONALYTY, 0, m, N)
    return {'LLF3':LLF3, 'XF':XFS, 'VF':VFS, 'SIG2':SIG2, 'Q':Q}

if __name__ == "__main__":
    res = Kalman_filtering(y) 
    LLF3 = res['LLF3']

    pred = hbm.pred(res['XF'], res['VF'], F, G, H, R, res['Q'], 30)

    trd = np.hstack( (LLF3['trd'],pred) )
    sea = LLF3['sea']

    np.savetxt('D:/workspace/python/MyPythonApp/works/output/output_t.txt',
                    trd,delimiter='\t')
    np.savetxt('D:/workspace/python/MyPythonApp/works/output/output_s.txt',
                    sea,delimiter='\t')
    print("that's all")