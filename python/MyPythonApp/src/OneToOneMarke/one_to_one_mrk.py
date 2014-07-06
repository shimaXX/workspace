# coding: utf8

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

### 関数の定義------------------------------------
# 2項プロビットモデルのベイズ推定(step1用)
def rtnorm(mu, sigma, a, b):
    lngth = len(mu)
    FA = dis.norm.cdf(a, loc=mu, scale=sigma, size = lngth)
    FB = dis.norm.cdf(b, loc=mu, scale=sigma, size = lngth)
    result = np.array([
                      dis.norm.ppf( 
                                   np.dot(ss.uniform.rvs(loc=0, scale=1,size=len(np.matrix(mu[t]))),
                                  (FB[t] - FA[t]) + FA[t]),
                                   loc=mu[t], scale=sigma, size=len(np.matrix(mu[t])) ) #percent point = Q値
                        for t in xrange(lngth)
                        ]
                      )
    result[result == -np.inf] = -100
    result[result == np.inf] = 100
    return result[:,0]

# Zの値を基準化する関数(step1用)
def standardization(z):
    return np.log( 0.001 + (z - np.min(z))/(np.max(z) - np.min(z))*(0.999 - 0.001) )

# 単変量正規分布のカーネル部分の乗数の部分の計算(step4用)
def Nkernel(sita, H, D, Vsita):
    if Vsita == 0: Vsita=1e-6
    return ((sita - np.dot(H,D.T))**2)/Vsita

# 多変量正規分布のカーネル部分の乗数の部分の計算(step4用)
def NMkernel(sita, H, D, Vsita):
    res = sita - np.dot(H.T, D)
    return np.dot( np.dot(res.T, inverse(Vsita)), res )

### 季節調整モデルの状態空間表現の行列設定
def FGHset(al, k, p, q, nz):  #alはARモデルのαベクトル、k;p;qはトレンド、季節、AR
    m = k + p + q + nz -1
    if(q>0): G = np.zeros((m,3+nz)) # 状態モデルでトレンド、季節、ARの3つを含む場合
    else: G = np.zeros((m,2+nz))    #AR成分を含まない場合(q=0)
    F = np.zeros((m,m))
    #H = matrix(0,1,m)          #Hの代わりにZtldを使うので、Hは不要
  
    ## トレンドモデルのブロック行列の構築
    G[0,0] = 1
    if k==1: F[0,0] = 1
    if k==2: F[0,0] = 2; F[0,1] = -1; F[1,0] = 1
    if k==3: F[0,0] = 3; F[0,1] = -3; F[0,2] = 1; F[1,0] = 1; F[2,1] = 1
    LS = k
    NS = 2
  
    ## 季節調整成分のブロック行列の構築
    G[LS, NS-1] = 1
    for i in xrange(p-1): F[LS, LS+i] = -1
    for i in xrange(p-2): F[LS+i+1, LS+i] = 1

    ## Z成分のブロック行列の構築
    LS = LS + p -1
    NS = 2
    for i in xrange(nz): F[LS+i, LS+i] = 1
    for i in xrange(nz): G[LS+i, NS+i] = 1
  
    if q>0:
        NS = NS +1
        G[LS, NS-1] = 1
        for i in xrange(q): F[LS, LS+i-1] = al[i]
        if q>1:
            for i in xrange(q-1): F[LS+i, LS+i-1] = 1
  
    ## シスムモデルの分散共分散行列Qの枠の算出
    Q = np.identity(NS+nz)
  
    return {'m':m, 'MatF':F, 'MatG':G, 'MatQ':Q}

# 状態空間表現における行列Qの設定------------------------
def Qset(Q0,parm):
    NS = len(Q0)
    Q = Q0
    # シスムモデルの分散共分散行列Qの枠の算出
    for i in xrange(NS): Q[i,i] = parm[i]
    return np.array(Q)

# カルマンフィルタの関数 ------------------------------------------
def KF(y, XF0, VF0, F, H, G, Q, R, limy, ISW, OSW, m, N):
    if OSW == 1:
        XPS = np.zeros((N,m),dtype=np.float); XFS = np.zeros((N,m),dtype=np.float)
        VPS = np.zeros((N,m,m),dtype=np.float); VFS = np.zeros((N,m,m),dtype=np.float)
    XF = XF0; VF = VF0; NSUM = 0.0; SIG2 = 0.0; LDET = 0.0    
    for  n in xrange(N):
        # 1期先予測
        XP = np.ndarray.flatten( np.dot(F, XF.T) ) #2週目から縦ベクトルになってしまうので、常に横ベクトルに変換
        VP = np.dot( np.dot(F, VF), F.T ) +  np.dot( np.dot(G, Q), G.T)
        # フィルタ
        # Rは操作しなければ縦ベクトル。pythonは横ベクトルになるので注意！
        if y[n] < limy: 
            NSUM = NSUM + 1
            B = np.dot( np.dot(H[:,n], VP), H[:,n].T)  + R  # Hは数学的には横ベクトル
            B1 = inverse(B) # nvar次元の縦ベクトル                        
            K = np.matrix(np.dot(VP, H[:,n].T)).T * np.matrix(B1) # Kは縦ベクトルになる(matrix)           
            e = np.array(y[n]).T - np.dot(H[:,n], XP.T) # nvar次元の縦ベクトル            
            XF = np.array(XP) + np.array( K * np.matrix(e) ).T # 横ベクトル
            VF = np.array(VP) - np.array( K* np.matrix(H[:,n]) * VP)           
            SIG2 = SIG2 + np.ndarray.flatten(np.array( np.matrix(e) * np.matrix(B1) * np.matrix(e).T ))[0] # 1次元でも計算できるようにmatrixにする
            LDET = LDET + math.log(linalg.det(B))
        else:
            XF = XP; VF = VP
        if OSW == 1:
            XPS[n,:] = XP; XFS[n,:] = XF; VPS[n,:,:] = VP; VFS[n,:,:] = VF
    SIG2 = SIG2 / NSUM
    if ISW == 0:
        FF = -0.5 * (NSUM * (math.log(2 * np.pi * SIG2) + 1) + LDET)
    else:
        FF = -0.5 * (NSUM * (math.log(2 * np.pi) + SIG2) + LDET)
    if OSW == 0:
        return {'LLF':FF, 'Ovar':SIG2}
    if OSW == 1:
        return {'XPS':XPS, 'XFS':XFS, 'VPS':VPS, 'VFS':VFS, 'LLF':FF, 'Ovar':SIG2}

# 平滑化の関数 ----------------------------------------------------
def SMO(XPS, XFS, VPS, VFS, F, GSIG2, k, p, q, m, N):
    XSS =  np.zeros((N,m),dtype=np.float); VSS =  np.zeros((N,m,m),dtype=np.float)
    XS1 = XFS[N-1,:]; VS1 = VFS[N-1,:,:]
    XSS[N-1,:] = XS1; VSS[N-1,:,:] = VS1
    for n1 in xrange(N-1):        
        n = (N-1) - n1; XP = XPS[n,:]; XF = XFS[n-1,:]
        VP = VPS[n,:,:]; VF = VFS[n-1,:,:]; VPI = inverse(VP)
        A = np.dot( np.dot(VF, F.T), VPI)
        XS2 = XF + np.dot(A, (XS1 - XP))
        VS2 = VF + np.dot( np.dot(A, (VS1 - VP)), A.T )
        XS1 = XS2; VS1 = VS2
        XSS[n-1,:] = XS1; VSS[n-1,:,:] = VS1
    return {'XSS':XSS, 'VSS':VSS}

# TAU2xの対数尤度関数の定義 ----------------------------------------
def LogL(parm, *args):
    y=args[0]; F=args[1]; H=args[2]; G=args[3]; R=args[4]; limy=args[5]
    ISW=args[6]; k=args[7]; m=args[8]; N=args[9]; Q0=args[10]
    Q = Qset(Q0 ,parm)
    XF0 = np.array([0]*k); VF0 = np.array(10 * np.identity(k)); OSW = 0
    LLF = KF(y, XF0, VF0, F, H, G, Q, R, limy, ISW, OSW, k, N)
    LL = LLF['LLF']
    return -LL # optimezeが最小化関数なので、対数尤度にマイナスをかけたものを返す

# 多変量正規分布の発生関数の定義--------------------------------------
def randn_multivariate(mu,Sigma,n=1):
    X = np.random.randn(n,len(mu))    
    A = linalg.cholesky(Sigma)    
    Y = np.dot(np.array(X),np.array(A)) + mu
    return Y

# 逆ウィッシャート関数の定義----------------------------------------------
def invwishartrand_prec(nu,phi):
    return inv(wishartrand(nu,phi))

def invwishartrand(nu, phi):
    return inv(wishartrand(nu, inv(phi)))
 
def wishartrand(nu, phi):
    dim = phi.shape[0]
    chol = cholesky(phi)
    foo = np.zeros((dim,dim))
    
    for i in xrange(dim):
        for j in xrange(i+1):
            if i == j:
                foo[i,j] = np.sqrt(chi2.rvs(nu-(i+1)+1))
            else:
                foo[i,j]  = npr.normal(0,1)
    return np.dot(chol, np.dot(foo, np.dot(foo.T, chol.T)))
# -------------------------------------------------------

# 疑似家庭内在庫金額の計算----------------------------------------------
def calc_INV(TIMES, PM, C, nhh):
    ## 顧客の消費傾向Data
    INV = np.zeros((TIMES,nhh),dtype = np.double)
    dlt = np.array([np.float(1.0)]*nhh)
    lmbd = np.array([np.float(1.0)]*nhh)
    for t in xrange(1,TIMES):
        denom = np.array(dlt[:]*C[:] + (INV[t-1,:])**lmbd[:])
        denom[denom==0.0] = 1e-6
        Cons = INV[t-1,:]*dlt[:]*C[:]/denom
        INV[t,:] = INV[t-1,:] + PM[:,t-1] - Cons
    return np.array(INV)
# -------------------------------------------------------