# coding: utf8
'''
Created on 2013/02/25

@author: n_shimada
'''
import createDdata
reload(createDdata)

db_filename = 'D_datas.db'
#inpt_filename03 = 'C:/Users/n_shimada/Desktop/Galster_CRM.csv'

db = createDdata.get_db_conn(db_filename)
print "importing data"
createDdata.import_data(db)
print "done"
cd = createDdata.create_data(db)
print "okCD"
cd.create_D_data()
print "fnish culculate"
#cd.close()