# codeing: utf-8

#pip install -U scikit-learn

import numpy as np
from numpy.random import uniform
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from sklearn import manifold

n=1000
k=10

a=np.array(3*np.pi*uniform(0,1,n), dtype=np.float64)
x = np.vstack((a*np.cos(a), 30*uniform(0,1,n), a*np.sin(a)))

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter(x[0,:],x[1,:],x[2,:], c=x[0,:]+x[2,:])
plt.show()

embedder = manifold.SpectralEmbedding(n_components=2, random_state=0, n_neighbors=k,
                                      eigen_solver="arpack")
x_se = embedder.fit_transform(x.T)

plt.scatter(x_se[:,0],x_se[:,1], c=x_se[:,0]+x_se[:,1])
plt.show()