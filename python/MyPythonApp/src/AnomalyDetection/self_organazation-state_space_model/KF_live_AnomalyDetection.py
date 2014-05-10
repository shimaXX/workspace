# coding: utf-8
from math import log, ceil
import numpy as np
from scipy.stats import norm, t
import matplotlib.pyplot as plt
import sqlite3 as sqlite
import cPickle as pickle
import time
from datetime import datetime, timedelta
import base64
import KF

class KFAnomalyDetection:
    datalist = []
    outlier_score = 0.0
    change_score = 0.0
    outlier_score_smooth = 0.0
    change_score_smooth = 0.0
    outlier_resid = None
    change_resid = None
    outlier_pred = None
    change_pred = None
    
    def __init__(self, term, smooth, k=2, p=0, q=0, w=10):
        self.kf_outlier_score = KF.KalmanFiltering(k,p,q,term=term, w=w)
        self.kf_first_smooth_score = KF.KalmanFiltering(k,p,q,term=smooth, w=w)
        self.kf_change_score = KF.KalmanFiltering(k,p,q,term=term, w=w)
        self.kf_second_smooth_score = KF.KalmanFiltering(k,p,q,term=smooth, w=w)
        self.term = term
    
    def initialize(self, last_got_date, scoredb):
        if last_got_date is None:
            return '0000-00-00 00:00:00'
        else:
            params = pickle.loads( base64.decodestring( scoredb.get_params('outlier_score') ) )
            self.kf_outlier_score.initialize_parameters(params['XFS'], params['VFS'], params['NSUM'])
            params = pickle.loads( base64.decodestring( scoredb.get_params('first_smooth_score') ) )
            self.kf_first_smooth_score.initialize_parameters(params['XFS'], params['VFS'], params['NSUM'])
            params = pickle.loads( base64.decodestring( scoredb.get_params('change_score') ) )
            self.kf_change_score.initialize_parameters(params['XFS'], params['VFS'], params['NSUM'])
            params = pickle.loads( base64.decodestring( scoredb.get_params('second_smooth_score') ) )
            self.kf_second_smooth_score.initialize_parameters(params['XFS'], params['VFS'], params['NSUM'])
            params = pickle.loads( base64.decodestring( scoredb.get_params('data_list') ) )
            self.datalist = params

            return last_got_date
    
    def forward_step(self, new_data):
        # add new_data to datalist
        if len(self.datalist)>=self.term:
            self.datalist.pop(0)
            self.datalist.append(new_data)
        else:
            self.datalist.append(new_data)

        # compute score
        if self.outlier_pred is None:
            self.first_step(new_data)
        else:
            self.calculate_score_step(new_data)
            self.learn_step(new_data)
    
    def conversion_score(self, train, var):
        """convert score to log loss"""
        m = np.mean(train)
        s = np.std(train)
        try:
            if s < 1: s=1
            px = norm.pdf(var, m, s) if norm.pdf(var, m, s)!=0.0 else 1e-308
            res = -log(px)
            return res
        except:
            return 0

    def first_step(self, new_data):
        # learn outlier model
        self.outlier_resid, self.outlier_pred = \
                self.learn_KF(self.kf_outlier_score, new_data)
        # calculate outlier score
        self.outlier_score, self.outlier_score_smooth = \
            self.calculate_score(self.kf_first_smooth_score, self.outlier_resid,
                        self.outlier_pred, new_data)
        # learn cnage model
        self.change_resid, self.change_pred = \
                self.learn_KF(self.kf_change_score, self.outlier_score_smooth)
        # calculate change score
        self.change_score, self.change_score_smooth = \
            self.calculate_score(self.kf_second_smooth_score, self.change_resid,
                        self.change_pred, self.outlier_score_smooth)

    def learn_step(self, data):
        self.outlier_resid, self.outlier_pred = \
                self.learn_KF(self.kf_outlier_score, data)
        self.change_resid, self.change_pred = \
                self.learn_KF(self.kf_change_score, self.outlier_score_smooth)
    
    def learn_KF(self, func, data):
        """leaning KF from new data"""
        pred = func.forward_backward(data)
        resid = np.abs( func.XSS[:func.term,0] - np.array(self.datalist) ) # 平滑分布とデータの残差
        return resid, pred
         
    def calculate_score_step(self, new_data):
        # calculate outlier score
        self.outlier_score, self.outlier_score_smooth = \
            self.calculate_score(self.kf_first_smooth_score, self.outlier_resid,
                        self.outlier_pred, new_data)
        # calculate change score
        self.change_score, self.change_score_smooth = \
            self.calculate_score(self.kf_second_smooth_score, self.change_resid,
                        self.change_pred, self.outlier_score_smooth)

    def calculate_score(self, func, resid, pred, new_data):
        score = self.conversion_score( resid, abs(float(pred) - float(new_data)) )
        print 'got score', score
        print 'smoothing score'
        return score, func.forward_backward(score, smoothing=1)
         
class DBCreater:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname, isolation_level='EXCLUSIVE')
        self.con.text_factory = str # utf-8を使用するためにstrを指定
        try: self.create_tables()
        except: pass
        
    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def get_params(self, filter_name):
        sql = "select parameter_dict from parameters_master where filter_name='%s'" \
                % filter_name
        res = self.con.execute(sql).fetchone()
        return res[0]

    def update_params(self, paramdict, dtime):
        res = self.get_param_last_update_time()
        if res is None:
            for k, v in paramdict.iteritems():
                self.con.execute("insert into parameters_master values(?,?,?)", \
                                (k, base64.encodestring(pickle.dumps(v)), dtime) )
        else:
            for k, v in paramdict.iteritems():
                if res<dtime:
                    self.con.execute("update parameters_master \
                        set parameter_dict='%s', created_at='%s' where \
                        filter_name='%s'" % (base64.encodestring(pickle.dumps(v)), dtime, k))
        self.dbcommit()

    def update_score(self, score, dtime):
        res = self.get_score_last_update_time()
        if res is None:
            self.con.execute("insert into score_master values(?,?)", (dtime, score) )
        else: 
            if res<dtime:
                self.con.execute( "insert into score_master values(?,?)", (dtime, score) )
        self.dbcommit()
        
    def get_score_last_update_time(self):
        res = self.con.execute("select max(created_at) from score_master").fetchone()
        if res is not None: return res[0] 
        else: return res

    def get_param_last_update_time(self):
        res = self.con.execute("select created_at from parameters_master").fetchone()
        if res is not None: return res[0] 
        else: return res
        
    def create_tables(self):
        tname = ['score_master', 'parameters_master']
        """
        sql = "select name from sqlite_master where type='table' and name='%s'" % tname
        res = self.con.execute(sql).fetchone()
        if res is None:
        """
        self.con.execute("create table %s(created_at, score)" % tname[0])
        self.con.execute("create index timeidx on %s(created_at)" % tname[0])
        self.con.execute("create table %s(filter_name, parameter_dict, created_at)" % tname[1]) # XFS, VFS, T
        self.con.execute("create index timeidx on %s(created_at)" % tname[1])        

class DataGetter:
    def __init__(self, dbname):
        self.datadb = sqlite.connect(dbname, isolation_level='SHARED')
        
    def get_data(self, last_got_date):
        sql = "select tweet_cnt, created_at from cnt_master where created_at>'%s' order by created_at" % last_got_date
        return self.datadb.execute(sql)

if __name__=='__main__':
    score_dbname = 'anomaly.db'
    data_dbname = 'D:/workspace/python/MyPythonApp/src/twitter/alert/test_tweet.db'
    term = 3 # time window of training
    smooth = 1
    kfad = KFAnomalyDetection(term,smooth,2,0,0,20)

    scoredb = DBCreater(score_dbname)
    datadb = DataGetter(data_dbname)
    
    last_got_date = scoredb.get_score_last_update_time()
    last_got_date =  kfad.initialize(last_got_date, scoredb)
    while 1:
        n_date = datetime.now() - timedelta(minutes=1)
        n_date = n_date.strftime('%Y-%m-%d %H:%M:00')
        
        """you must not calculate score at curent time.
        thus, wait until finishing counting tweet number at curent time.
        """
        if last_got_date >= n_date: 
            print "counter have not yet counted."
            print "sleeping..."
            time.sleep(30)
            continue
        print last_got_date
        
        # get tweet count data
        data_tup = datadb.get_data(last_got_date)
        while 1:
            res = data_tup.fetchone()
            if res is None: 
                print 'sleeping...'
                time.sleep(30)
                break
            print "calculating:", last_got_date
            data, last_got_date = res
            
            kfad.forward_step(data)
            paramdict = \
                {'outlier_score': {u'XFS':kfad.kf_outlier_score.XFS,u'VFS':kfad.kf_outlier_score.VFS,u'NSUM':kfad.kf_outlier_score.NSUM},
                 'first_smooth_score': {u'XFS':kfad.kf_first_smooth_score.XFS,u'VFS':kfad.kf_first_smooth_score.VFS,u'NSUM':kfad.kf_first_smooth_score.NSUM},
                 'change_score': {u'XFS':kfad.kf_change_score.XFS,u'VFS':kfad.kf_change_score.VFS,u'NSUM':kfad.kf_change_score.NSUM},
                 'second_smooth_score': {u'XFS':kfad.kf_second_smooth_score.XFS,u'VFS':kfad.kf_second_smooth_score.VFS,u'NSUM':kfad.kf_second_smooth_score.NSUM},
                 'data_list': kfad.datalist
                 }
            scoredb.update_params(paramdict, last_got_date)
            scoredb.update_score(kfad.change_score_smooth, last_got_date)