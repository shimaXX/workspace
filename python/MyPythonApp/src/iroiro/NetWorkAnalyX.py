'''
Created on 2012/10/16

@author: n_shimada
'''

import socialGraphX
reload(socialGraphX)
from numpy import *
#csv_filename = "C:/HadoopPig/workspace/HadoopPig/works/output/actionGraph/part-r-00000.csv"
csv_filename = "C:/HadoopPig/workspace/HadoopPig/works/output/TEST/getNextVerbOnlyBuySession/part-m-00000.csv"
db_filename = "verb_data.db"

db = socialGraphX.get_db_conn(db_filename)
print "importing data"
socialGraphX.import_data(db, csv_filename)
print "done"
sn = socialGraphX.SocialNetwork(db)
print "okSN"

print "creating Graph"
sn.createGraph()
print "Done"

sn.close()