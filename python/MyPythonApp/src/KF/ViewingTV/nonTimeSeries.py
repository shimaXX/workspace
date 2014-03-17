# coding: utf-8
'''
Created on 2014/03/16

@author: nahki
'''

import os
import numpy as np
from numpy.random import uniform, randn, multivariate_normal, normal
import scipy.stats.distributions as dis
from scipy.stats import norm, chi2
from scipy.linalg import inv,cholesky,det
from math import exp, log, floor


class HbBinLogit:
    nvar = 3 # ロジットモデルの説明変数の数
    hh = 200 # 個人数（放送局数）
    nobs = 10 # 個人辺りの選択回数
    nz = 2 # 個人属性の説明変数の数（後ほど3に修正）
    
    R = 12000
    sbeta = 0.2
    keep = 10

    nhh = hh # length(hhdata)
    """
    nz = nz # length(Z)
    nvar = nvar # length(X[0,:])
    """
    
    # 事前分布のパラメタ
    nu = nvar+3
    V = nu*np.eye(nvar)
    ADelta = 0.01 * np.eye(nz)
    Deltabar = np.zeros(nz*nvar).reshape( (nz,nvar) ) 
    
    # 結果格納用
    Vbetadraw = np.zeros( (floor(R/keep),nvar, nvar ) )
    betadraw = np.zeros((floor(R/keep),nhh,nvar))
    Deltadraw = np.zeros( (floor(R/keep), nz, nvar ) )

    reject = np.zeros(floor(R/keep)) # サンプリング棄却率
    llike = np.zeros(floor(R/keep)) # 対数尤度
    
    def __init__(self):
        np.random.seed(555)
        self.generate_data()
        self.oldbetas = np.zeros( (self.nhh,self.nvar) )
        self.oldVbeta = np.eye(self.nvar)
        self.oldVbetai = np.eye(self.nvar)
        self.oldDelta = np.zeros( (self.nz, self.nvar) )
        self.betad = np.zeros(self.nvar)
        self.betan = np.zeros(self.nvar)
                
    def generate_data(self):
        self.Z = np.vstack( (np.ones(self.hh,dtype=np.float), uniform(-1,1,size=self.hh)) ) # 本では縦ベクトル
        Delta = np.array([[-2,-1,2],[1,0,1]],dtype=np.float) # 横ベクトルのままで良い
        iota = np.ones(self.nvar).reshape( (self.nvar,1) ) # 縦ベクトル
        self.Vbeta = np.eye(self.nvar) + 0.5*iota.dot(iota.T)
        
        self.hhdata = []
        for i in xrange(self.hh):
            beta = Delta.T.dot(self.Z[:,i])+cholesky(self.Vbeta).T.dot(norm.rvs(size=self.nvar))
            X = uniform(size=self.nobs*self.nvar).reshape(self.nobs, self.nvar)
            prob = np.exp(X.dot(beta))/( 1+np.exp(X.dot(beta)) )
            unif = uniform(0,1,self.nobs)
            y = 1*(unif<prob)
            tmp = {'y':y, 'X':X,'beta':beta}
            self.hhdata.append(tmp)

    def loglike(self,y,X,beta):
        """2項ロジットモデルの対数尤度関数の定義"""
        pl = np.exp(X.dot(beta))/( 1+np.exp(X.dot(beta)) ) # nobs次元のベクトルが
        ll = y*np.log(pl)+(1-y)*np.log(1-pl)
        return sum(ll)

    def predict(self):
        for itr in xrange(self.R):
            rej = 0
            logl = 0
            sV = self.sbeta * self.oldVbeta # 新しいbetaの発生に使用
            root = cholesky(sV).T
            
            # MH法による個人別betaのサンプリング
            for i in xrange(self.nhh):
                self.betad = self.oldbetas[i,:]
                self.betan = self.betad + root.dot(norm.rvs(size=self.nvar))
                
                # 尤度の計算
                lognew = self.loglike(self.hhdata[i]["y"], self.hhdata[i]["X"], self.betan)
                logold = self.loglike(self.hhdata[i]["y"], self.hhdata[i]["X"], self.betad)
                
                # 事前分布の計算
                logknew = -0.5*( (self.betan - self.Z[:,i].dot(self.oldDelta).dot(self.oldVbetai)). \
                                 dot( (self.betan - self.Z[:,i].dot(self.oldDelta)) ) )
                logkold = -0.5*( (self.betad - self.Z[:,i].dot(self.oldDelta).dot(self.oldVbetai)). \
                                 dot( (self.betad - self.Z[:,i].dot(self.oldDelta)) ) )

                # 採択率の計算
                alpha = np.exp( lognew + logknew - logold - logkold )
                if alpha is None:
                    alpha = -1
                u = uniform(1)

                if u < alpha:
                    self.oldbetas[i,:] = self.betan
                    logl += lognew
                else:
                    logl += logold
                    rej += 1
            
            # ここからは全人間分のデータを扱う
            # 多変量回帰によるDeltaのギブスサンプリング
            ZtZ = self.Z.dot(self.Z.T)
            Z2pA = ZtZ + self.ADelta
            Deltahat = inv(ZtZ).dot(self.Z).dot(self.oldbetas)
            
            Dtld = inv( Z2pA ) \
                    .dot( ZtZ.dot(Deltahat) + self.ADelta.dot(self.Deltabar) )
            Dvec = np.ndarray.flatten(Dtld)
            Delta = multivariate_normal( Dvec, np.kron(self.Vbeta, inv(Z2pA)) )
            self.oldDelta = Delta.reshape((self.nz, self.nvar))

            # 逆ウィシャート分布のギブスサンプリング
            div = self.oldbetas.T - self.oldDelta.T.dot( self.Z )
            S = np.dot(div, div.T) # 上の計算でdivは横ベクトルになるのでSをスカラにするためにTは後ろ
            # 逆ウィッシャート分布でサンプリング
            self.oldVbeta = self.invwishartrand(self.nu + self.nhh, self.V + S)            
            self.oldVbetai = inv(self.oldVbeta)  

            # サンプリング数の表示
            if itr % 100 == 0: print "iter:",itr
            
            # keep回ごとにサンプリング結果を保存
            mkeep = itr/self.keep
            if itr % self.keep:
                self.Deltadraw[mkeep,:,:] = self.oldDelta
                self.Vbetadraw[mkeep,:,:] = self.oldVbeta
                self.betadraw[mkeep,:,:] = self.oldbetas
                self.llike[mkeep]=logl
                self.reject[mkeep]=rej/self.nhh

            print "likelihood",self.llike[mkeep]

    # 逆ウィッシャート関数の定義----------------------------------------------
    def invwishartrand_prec(self, nu,phi):
        return inv(self.wishartrand(nu,phi))
    
    def invwishartrand(self, nu, phi):
        return inv(self.wishartrand(nu, inv(phi)))
     
    def wishartrand(self, nu, phi):
        dim = phi.shape[0]
        chol = cholesky(phi)
        foo = np.zeros((dim,dim))
        
        for i in xrange(dim):
            for j in xrange(i+1):
                if i == j:
                    foo[i,j] = np.sqrt(chi2.rvs(nu-(i+1)+1))
                else:
                    foo[i,j]  = normal(0,1)
        return np.dot(chol, np.dot(foo, np.dot(foo.T, chol.T)))

if __name__=='__main__':
    c = HbBinLogit()
    c.predict()