# coding: utf8

import numpy.random as npr
from numpy.oldnumeric.linear_algebra import inverse
from scipy import linalg
import scipy.stats.distributions as dis
import scipy.stats as ss
import numpy as np
import math
from scipy.linalg import inv,cholesky,det

### 季節調整モデルの状態空間表現の行列設定
def FGHset(al, k, p, q):  #alはARモデルのαベクトル、k;p;qはトレンド、季節、AR
    m = k + p + q -1
    if(q>0): G = np.zeros((m,3), dtype=np.float) # 状態モデルでトレンド、季節、ARの3つを含む場合
    else: G = np.zeros((m,2), dtype=np.float)    #AR成分を含まない場合(q=0)
    F = np.zeros((m,m), dtype=np.float)
    H = np.zeros((1,m), dtype=np.float)          #Hの代わりにZtldを使うので、Hは不要
  
    ## トレンドモデルのブロック行列の構築
    G[0,0] = 1
    H[0,0] = 1
    if k==1: F[0,0] = 1
    if k==2: F[0,0] = 2; F[0,1] = -1; F[1,0] = 1
    if k==3: F[0,0] = 3; F[0,1] = -3; F[0,2] = 1; F[1,0] = 1; F[2,1] = 1
    LS = k; NS = 2
  
    ## 季節調整成分のブロック行列の構築
    G[LS, NS-1] = 1
    H[0,LS] = 1
    for i in xrange(p-1): F[LS, LS+i] = -1
    for i in xrange(p-2): F[LS+i+1, LS+i] = 1
  
    if q>0:
        NS = NS +1
        G[LS, NS-1] = 1
        H[0,LS] = 1
        for i in xrange(q): F[LS, LS+i-1] = al[i]
        if q>1:
            for i in xrange(q-1): F[LS+i, LS+i-1] = 1
  
    ## シスムモデルの分散共分散行列Qの枠の算出
    Q = np.identity(NS)
  
    return {'m':m, 'MatF':F, 'MatG':G, 'MatH':H, 'MatQ':Q}

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
    for n in xrange(N):
        # 1期先予測
        XP = np.ndarray.flatten( np.dot(F, XF.T) ) #2週目から縦ベクトルになってしまうので、常に横ベクトルに変換
        VP = np.dot( np.dot(F, VF), F.T ) +  np.dot( np.dot(G, Q), G.T)
        # フィルタ
        # Rは操作しなければ縦ベクトル。pythonは横ベクトルになるので注意！
        if y[n] < limy: 
            NSUM = NSUM + 1
            
            B = np.dot( np.dot(H, VP), H.T)  + R  # Hは数学的には横ベクトル
            B1 = inverse(B) # nvar次元の縦ベクトル
            K = np.matrix(np.dot(VP, H.T)) * np.matrix(B1) # Kは縦ベクトルになる(matrix)
            e = np.array(y[n]).T - np.dot(H, XP.T) # nvar次元の縦ベクトル            
            XF = np.array(XP) + np.array( K * np.matrix(e) ).T # 横ベクトル
            VF = np.array(VP) - np.array( K* np.matrix(H) * VP)           
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
        
    t=np.arange(N, dtype=np.float); s=np.arange(N, dtype=np.float);
    tv=np.arange(N, dtype=np.float); sv=np.arange(N, dtype=np.float)
 
    if p>0:
        for n in xrange(N):
            t[n]=XSS[n,0]; s[n]=XSS[n,k]
            tv[n]=GSIG2*VSS[n,0,0]
            sv[n]=GSIG2*VSS[n,k,k]
    else:
        for n in xrange(N):
            t[n]=XSS[n,0]; tv[n]=GSIG2*VSS[n,0,0]
    
    return {'trd':t, 'sea':s, 'trv':tv ,'sev':sv}

# TAU2xの対数尤度関数の定義 ----------------------------------------
def LogL(parm, *args):
    y=args[0]; F=args[1]; H=args[2]; G=args[3]; R=args[4]; limy=args[5]
    ISW=args[6]; k=args[7]; m=args[8]; N=args[9]; Q0=args[10]
    Q = Qset(Q0 ,parm)
    XF0 = np.arange(m, dtype=np.float);
    VF0 = np.float(10)*np.identity(m); OSW = 0
    LLF = KF(y, XF0, VF0, F, H, G, Q, R, limy, ISW, OSW, m, N)
    LL = LLF['LLF']
    return -LL # optimezeが最小化関数なので、対数尤度にマイナスをかけたものを返す

def pred(XF, VF, F, G, H, Q, R, N):
    y = np.zeros(N, dtype=np.float)
    XFp=XF[XF.shape[0]-1,:] #直近のデータ行列のみ取得
    VFp=VF[XF.shape[0]-1,:]
    
    for n in xrange(N):
        XP = np.ndarray.flatten( np.dot(F, XFp.T) )
#        VP = np.dot( np.dot(F, VF), F.T ) +  np.dot( np.dot(G, Q), G.T )
        y[n] = np.dot(H, XP) + npr.normal()
        XFp=XP
    return y