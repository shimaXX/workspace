# coding: utf8

from numpy.oldnumeric.linear_algebra import inverse
from scipy import linalg
import numpy as np
from math import log

class KalmanFiltering:
    limy = 1e20 # 欠測とみなす数値の境界
    GSIG2 = 1
    L = 1
    R = np.identity(L)
    NSUM = 0.0
    SIG2 = 0.0
    LDET = 0.0
    
    def __init__(self, k, p, q, term=10, w=10):
        self.k = k # 階差
        self.p = p # 季節性循環
        self.q = q # AR成分
        self.m, self.F, self.G, \
            self.H, self.Q = self.FGHset(0,k,p,q,w)
        self.term = term
        self.strg_trm = term
        
        self.resid = np.zeros(self.term)
        self.pred = 0.0
        
        # matrix for storage predicted value
        self.XPS = np.zeros((term,self.m), dtype=np.float)
        self.VPS = np.array([np.eye(self.m, dtype=np.float)]*term)
        # matrix for storage predicted value
        self.XFS = np.zeros((term,self.m), dtype=np.float)
        self.VFS = np.array([np.eye(self.m, dtype=np.float)]*term)
        # matrix for storage smoothed value
        self.XSS = np.zeros((term,self.m), dtype=np.float)
        self.VSS = np.array([np.eye(self.m, dtype=np.float)]*term)

    def initialize_parameters(self, xfs, vfs, t):
        self.XFS = xfs
        self.VFS = vfs
        self.NSUM = t

    def forward_backward(self, new_data, smoothing=0):
        self.NSUM += 1 
        if self.NSUM < self.strg_trm:
            self.term = int(self.NSUM)
        else:
            self.term = self.strg_trm
        # forward
        self.forward(new_data)
        # smoothing
        self.SMO()
        if smoothing==1:
            return np.mean( self.XSS[:self.term,0] )
                    
        return self.predict()[0]
    
    def forward(self, y):
        XF = self.XFS[self.term-1]
        VF = self.VFS[self.term-1]     

        # 1span predicting
        XP, VP = self.forward_predicting(VF, XF)
        XF, VF = self.filtering(y, XP, VP)
        self.storage_params(XP, XF, VP, VF)
#         sig2 = self.SIG2 / self.NSUM
#         FF = -0.5 * (self.NSUM * (log(2 * np.pi * sig2) + 1) + self.LDET)
#         return {'LLF':FF, 'Ovar':sig2}
    
    def storage_params(self, XP, XF, VP, VF):
        if self.NSUM>self.term:
            self.XPS[:self.term-1] = self.XPS[1:self.term] 
            self.XFS[:self.term-1] = self.XFS[1:self.term]
            self.VPS[:self.term-1] = self.VPS[1:self.term]
            self.VFS[:self.term-1] = self.VFS[1:self.term]
            self.normal_storage(XP, XF, VP, VF)
        else:
            self.normal_storage(XP, XF, VP, VF)
                
    def normal_storage(self, XP, XF, VP, VF):
        self.XPS[self.term-1] = XP 
        self.XFS[self.term-1] = XF
        self.VPS[self.term-1] = VP
        self.VFS[self.term-1] = VF
    
    def forward_predicting(self, VF, XF):
        """1span predicting"""
        XP = np.ndarray.flatten( np.dot(self.F, XF.T) ) #2週目から縦ベクトルになってしまうので、常に横ベクトルに変換
        VP = self.F.dot(VF).dot(self.F.T) +  self.G.dot(self.Q).dot(self.G.T)
        return XP, VP
    
    def filtering(self, y, XP, VP):
        if y < self.limy: 
            B = np.dot( np.dot(self.H, VP), self.H.T)  + self.R  # Hは数学的には横ベクトル
            B1 = inverse(B)
            K = np.matrix(np.dot(VP, self.H.T)) * np.matrix(B1) # Kは縦ベクトルになる(matrix)
            e = np.array(y).T - np.dot(self.H, XP.T)            
            XF = np.array(XP) + np.array( K * np.matrix(e) ).T # 横ベクトル
            VF = np.array(VP) - np.array( K* np.matrix(self.H) * VP)           
            self.SIG2 += np.ndarray.flatten(np.array( np.matrix(e) * np.matrix(B1) * np.matrix(e).T ))[0] # 1次元でも計算できるようにmatrixにする
            self.LDET += log(linalg.det(B))
        else:
            XF = XP; VF = VP
        return XF, VF
        
    def SMO(self):
        """fixed-interval smoothing"""
        XS1 = self.XFS[self.term-1]
        VS1 = self.VFS[self.term-1]
        self.XSS[self.term-1] = XS1
        self.VSS[self.term-1] = VS1
        for n1 in xrange(self.term):        
            n = (self.term-1) - n1; XP = self.XPS[n]; XF = self.XFS[n-1]
            VP = self.VPS[n]; VF = self.VFS[n-1]; VPI = inverse(VP)
            A = np.dot( np.dot(VF, self.F.T), VPI)
            XS2 = XF + np.dot(A, (XS1 - XP))
            VS2 = VF + np.dot( np.dot(A, (VS1 - VP)), A.T )
            XS1 = XS2; VS1 = VS2
            self.XSS[n-1] = XS1
            self.VSS[n-1] = VS1
                
    # TAU2xの対数尤度関数の定義 
    def LogL(self, parm, *args):
        y=args[0]
        LLF = self.forward(y)
        LL = LLF['LLF']
        return -LL # optimezeが最小化関数なので、対数尤度にマイナスをかけたものを返す
    
    def predict(self, forward_time=1):
        """pridint average value"""
        y = np.zeros(forward_time, dtype=np.float)
        XFp=self.XFS[-1] #直近のデータ行列のみ取得
        #VFp=VF[XF.shape[0]-1,:]
        
        for n in xrange(forward_time):
            XP = np.ndarray.flatten( np.dot(self.F, XFp.T) )
            #VP = np.dot( np.dot(F, VF), F.T ) +  np.dot( np.dot(G, Q), G.T )
            y[n] = np.dot(self.H, XP) # 期待値を取るのでノイズは入れない
            XFp=XP
        return y

    def FGHset(self, al, k, p, q, v=10):
        """季節調整モデルの状態空間表現の行列設定
        al：ARモデルのαベクトル
        k,p,q：階差、季節性周期、ARパラメタ数（予測する場合はk>=2とする）
        v：システム誤差の分散（変化点検出では小さめに決め打ちで設定しておけば良い）
        """
        m = k + p + q -1
    
        if q>0: G = np.zeros((m,3), dtype=np.float) # 状態モデルでトレンド、季節、ARの3つを含む場合
        elif p>0: G = np.zeros((m,2), dtype=np.float) #AR成分を含まない場合(q=0)
        else: m=k; G = np.zeros((m,1), dtype=np.float)
        F = np.zeros((m,m), dtype=np.float)
        H = np.zeros((1,m), dtype=np.float) #Hの代わりにZtldを使うので、Hは不要
      
        ns = 0; ls =0
        # トレンドモデルのブロック行列の構築
        if k>0:
            ns +=1
            G[0,0] = 1; H[0,0] = 1
            if k==1: F[0,0] = 1
            if k==2: F[0,0] = 2; F[0,1] = -1; F[1,0] = 1
            if k==3: F[0,0] = 3; F[0,1] = -3; F[0,2] = 1; F[1,0] = 1; F[2,1] = 1
            ls += k
      
        # 季節調整成分ブロック行列の構築
        if p>0:
            ns +=1
            G[ls, ns-1] = 1
            H[0,ls] = 1
            for i in xrange(p-1): F[ls, ls+i] = -1
            for i in xrange(p-2): F[ls+i+1, ls+i] = 1
            ls +=p-1
      
        # AR成分ブロック行列の構築
        if q>0:
            ns +=1
            G[ls, ns-1] = 1
            H[0,ls] = 1
            for i in xrange(q): F[ls, ls+i-1] = al[i]
            if q>1:
                for i in xrange(q-1): F[ls+i, ls+i-1] = 1
      
        # シスムモデルの分散共分散行列Qの枠の算出
        Q = np.eye(ns,dtype=np.float)*v
      
        return m, F, G, H, Q