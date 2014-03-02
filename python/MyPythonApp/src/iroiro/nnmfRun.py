# coding: utf-8 
'''
Created on 2012/12/19

@author: n_shimada
'''
from numpy import *
import multiprocessing
import nnmf
import newsfeatures
reload(nnmf)
reload(newsfeatures)

input_filename = 'C:/HadoopPig/workspace/HadoopPig/works/output/EVA/EvaVerbCount1212/Part-r-00000'

# get data
allv, action_data, verbmatrix, verbs, usr_names = newsfeatures.get_input_data(input_filename)

v = matrix(verbmatrix)

weights,feat = nnmf.factorize_kld(v, pc = 5, iter_num = 500)

topp, pn = newsfeatures.showfeatures(weights, feat, usr_names, verbs)

newsfeatures.showarticles(usr_names, topp, pn)