#-*- coding: utf-8 -*-
'''
Created on 2012/12/17

@author: n_shimada
'''
import AnomalyDetection

#input pathとDB名の定義
input_filename = "C:/HadoopPig/workspace/HadoopPig/works/output/TEST/EvaSeq1209/part-r-00000"

input_data = AnomalyDetection.get_input_data(input_filename)
print "dune_get_data"

result = AnomalyDetection.culcurate_score(input_data)
print "dune_culcurate"

result