# -*- coding: utf-8 -*-
'''
Created on 2013/04/26

@author: n_shimada
'''
import imtools
imlist = sorted(imtools.get_imlist('new_data'))
import pickle
import sift
import numpy as np
import scipy
from numpy import *

def main():
    with open('voc_centroid.pkl','rb') as f:
        centors = pickle.load(f)
        
    nbr_images = len(imlist)
    featlist = [ imlist[i][:-3]+'sift' for i in xrange(nbr_images)]
    
    desc = get_descriptors(featlist,nbr_images)
    get_dist(desc, centors, nbr_images)
    

def get_descriptors(featurefiles,nbr_images):
    descr = []
    descr.append(sift.read_features_from_file(featurefiles[0])[1])

    # optional.view feature points.
    descriptors = descr[0] #stack all features for k-means
    for i in arange(1,nbr_images):
        descr.append(sift.read_features_from_file(featurefiles[i])[1])
        descriptors = vstack((descriptors,descr[i]))
    return descriptors


def get_dist(desc, centors, nbr_images):
    imhist = np.zeros((nbr_images, len(centors)))
    for i in xrange(nbr_images):    
        for d in desc[i]:
            tmp = np.sum((centors - d)**2, axis=1).flatten()
            w = np.where( tmp == np.min(tmp) )[0]
            print w
            imhist[i,w] += 1
    print imhist
            
if __name__=='__main__':
    main()

