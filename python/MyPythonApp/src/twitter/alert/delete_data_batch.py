# coding: utf-8

import sqlite3 as sqlite
from datetime import datetime, timedelta
import io


class DBModifier:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname, isolation_level='DEFERRED')
    
    def __del__(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()
    
    def delete_data(self, table_name, target_date):
        sql = "delete from %s where created_at<'%s'" % (table_name, target_date)
        self.con.execute(sql)
        self.dbcommit()
        
    def dump_data(self, table_name, t_date, ofname):
        sql = "select * from %s where created_at<'%s'" % (table_name, t_date)
        response = self.con.execute(sql)
        of = io.open(ofname, 'w')
        while 1:
            res = response.fetchone()
            if res is None: break
            
            string = '\t'.join( (lambda tup: [str(x) for x in tup])(res) )
            of.write(string+u'\n')
            
if __name__=='__main__':
    datadbname = 'test_tweet.db'
    scoredbname = 'D:/workspace/python/MyPythonApp/src/AnomalyDetection/anomaly.db'
    today = datetime.now()
    target_date = today - timedelta(days=2) # 前2日分のデータを残して削除
    target_date = target_date.strftime('%Y-%m-%d 00:00:00')

    # delete tweet data
    dataofname = 'dump_tweet_cnt_data_' + target_date[:10]
    datadb = DBModifier(datadbname)
    print "dumping data:", datadbname
    datadb.dump_data('cnt_master', target_date, dataofname)
    print "deleting data:", datadbname
    datadb.delete_data('tweet_master', target_date)
    datadb.delete_data('cnt_master', target_date)
    
    # delete score data
    scoreofname = 'dump_score_data_' + target_date[:10]
    scoredb = DBModifier(scoredbname)
    print "dumping data:", scoredbname
    scoredb.dump_data('score_master', target_date, scoreofname)
    print "deleting data:", scoredbname
    scoredb.delete_data('score_master', target_date)