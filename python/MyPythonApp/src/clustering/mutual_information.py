# coding: utf-8

import sys
from math import log

#一次元時系列同士の相互情報量
def mic(xseq , yseq):
   xmax,xmin = max(xseq),min(xseq)
   ymax,ymin = max(yseq),min(yseq)
   N = min(len(xseq) , len(yseq))
   L, Nx , Ny = sys.float_info.max , 1 , 1
   if xmax==xmin or ymax==ymin:
      return 0.0
   #-- 赤池情報量基準に基づいて分割数を決める
   for n in xrange(2,N):
      p = dict()
      for (x,y) in zip(xseq,yseq):
         nx = int( n*(x-xmin)/(xmax-xmin) )
         ny = int( n*(y-ymin)/(ymax-ymin) )
         p[(nx,ny)] = p.get( (nx,ny) , 0) + 1
      AIC = -(sum( [Nxy*log(float(Nxy)/N , 2) for Nxy in p.itervalues()] ) + N*log(n,2)*2) + (n*n-1)
      if AIC < L:
         L = AIC
         Nx = n
         Ny = n
   #-- 相互情報量の推定
   px,py,p = dict(),dict(),dict()
   for (x,y) in zip(xseq,yseq):
       nx = int( Nx*(x-xmin)/(xmax-xmin) )
       ny = int( Ny*(y-ymin)/(ymax-ymin) )
       px[nx] = px.get(nx,0)+1
       py[ny] = py.get(ny,0)+1
       p[(nx,ny)] = p.get( (nx,ny) , 0) + 1
   return sum([p0*log(N*float(p0)/(px[nx]*py[ny]) , 2) for ((nx,ny) , p0) in p.iteritems()])/(N*N)