'''
Created on 2012/10/16

@author: n_shimada
'''

import socialGraphXver2
reload(socialGraphXver2)
from numpy import *
#csv_filename = "C:/HadoopPig/workspace/HadoopPig/works/output/actionGraph/part-r-00000.csv"
csv_filename = "C:/HadoopPig/workspace/HadoopPig/works/output/Ci-Labo/Ci-LaboTrack1203/part-m-00000.csv"
db_filename = "verb_data.db"

db = socialGraphXver2.get_db_conn(db_filename)
print "importing data"
socialGraphXver2.import_data(db, csv_filename)
print "done"
sn = socialGraphXver2.SocialNetwork(db)
print "okSN"

print "creating Graph"
sn.createGraph()
print "Done"

sn.close()