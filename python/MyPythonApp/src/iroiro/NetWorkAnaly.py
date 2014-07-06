'''
Created on 2012/10/16

@author: n_shimada
'''

import socialnetwork
import optimization
from numpy import *

#csv_filename = "C:/HadoopPig/workspace/HadoopPig/works/output/actionGraph/part-r-00000.csv"
csv_filename = "C:/HadoopPig/workspace/HadoopPig/works/output/testLowGraph09-01_09-08/part-r-00000.csv"
db_filename = "verb_data.db"

db = socialnetwork.get_db_conn(db_filename)
print "importing data"
socialnetwork.import_data(db, csv_filename)
print "done"
sn = socialnetwork.SocialNetwork(db)
print "okSN"

sol=optimization.randomoptimize(socialnetwork.domain,sn.crosscount)
print "OPTIMIZE done"
sol=optimization.annealingoptimize(socialnetwork.domain,sn.crosscount,step=50,cool=0.99)
print "annealing done"
sn.crosscount(sol)
print "outputing count number of crosses"
#sol
sn.drawnetwork(sol)
print "Drawed Network"

sn.close()