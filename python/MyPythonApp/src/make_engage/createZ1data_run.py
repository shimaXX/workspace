'''
Created on 2013/02/25

@author: n_shimada
'''
import createZ1data_rev1
reload(createZ1data_rev1)

db_filename = 'interval_date_data.db'
#inpt_filename01 = 'C:/HadoopPig/workspace/HadoopPig/works/output/Mining/GalsterCPM_Z_20130225/Part-m-00000'
#inpt_filename02 = 'C:/HadoopPig/workspace/HadoopPig/works/output/Mining/GalsterCPM_Z_20130225/Part-m-00001'
inpt_filenames = []
#inpt_filenames.append(inpt_filename01)
#inpt_filenames.append(inpt_filename02)
inpt_filenames.append('C:/HadoopPig/workspace/HadoopPig/works/output/Mining/GalsterCPM_PAYMENT_20130322/Part-r-00000')
#inpt_filename03 = 'C:/Users/n_shimada/Desktop/Galster_CRM.csv'

db = createZ1data_rev1.get_db_conn(db_filename)
print "importing data"
createZ1data_rev1.import_data(db, inpt_filenames)
print "done"
cd = createZ1data_rev1.create_data(db)
print "okCD"
cd.create_Z_data()
print "fnish culculate"
cd.close()