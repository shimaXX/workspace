# coding: utf-8
"""
retweet, mentionは置換 
url, hashtagは残したままで保存することのみを行う
文字正規化はunicode正規化のみ
全角化などはまだ行わない
連続文字などは置換する
"""

import re, os, io
import time
import simplejson as json
from tweepy.auth import OAuthHandler
from tweepy.api import API
from tweepy import Cursor
import sqlite3 as sqlite
import pickle
from datetime import datetime, timedelta

from normalizewords import Transform, Replace

class Searcher:
    d_time = None
    cnt = 0
    def __init__(self, token, consumer, dbname):
        self.token=token
        self.consumer=consumer
        self.db = DBCreater(dbname)
    
    def search_tweet(self,query):
        auth = self.get_oauth()
        api = API(auth)
        
        # ツイートの検索
        tweets = self.get_tweets(api, query)
        # ツイートの出力
        self.output_tweets(tweets)

    def get_oauth(self,):
        consumer_key = self.consumer['key']
        consumer_secret = self.consumer['secret']
        access_token = self.token['token']
        access_secret = self.token['secret']
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        return auth
    
    def get_tweets(self,api, query, rtype='recent',languages='ja'):
        tweets = Cursor(api.search, 
                        q=query,
                        count=100,
                        #geocode=geo,
                        result_type=rtype, # recent, popular, mixed 
                        include_entities=True,
                        lang=languages).items()
        return tweets
    
    def output_tweets(self,tweets):
        for tweet in tweets:
            dt = tweet.created_at + timedelta(hours=9)
            dt = dt.strftime('%Y-%m-%d %H:%M')
            if self.d_time != dt:
                print self.d_time
                if self.d_time is not None:
                    self.db.update_tables(self.d_time, self.cnt)
                self.d_time = dt
                self.cnt = 0
            
            ## ブラックリストの処理
            
            text = tweet.text.strip()
            text = re.sub(r'[\n\r]', '￥n', text)
            text = Replace.str_replace(text)
            print "rep:", text
            # 文字の正規化
            text = Transform.tf_unicodenorm(text)
            
            ## wordlistの作成（mensionのブラックリスト処理）
            ## spamの判断
            
            if self.db.isnewdata(tweet.id):
                t_date = tweet.created_at + timedelta(hours=9)
                self.db.addtoindex(tweet.id, tweet.user.screen_name, t_date , text, "")
                self.cnt += 1
            else: break
#             res = str(tweet.id)+'\t'+str(tweet.user.screen_name)+'\t'+str(tweet.created_at)+'\t'+text
#             fout.write(res + "\n")
        time.sleep(10)

class DBCreater:
    def __init__(self,dbname):
        self.con = sqlite.connect(dbname, isolation_level='EXCLUSIVE')
        try: self.create_tables()
        except: pass
        
    def __del__(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()
        
    def addtoindex(self, tweet_id, screen_name, created_at, tweet, wordlist):
        self.con.execute( "insert into tweet_master values(?,?,?,?,?)", \
                            (tweet_id, screen_name, created_at, tweet, pickle.dumps(wordlist)) )
        self.dbcommit()
        
    def isnewdata(self, tweet_id):
        res = self.con.execute("select tweet_id from tweet_master where tweet_id='%s'" % tweet_id).fetchone()
        if res is None: return True
        else: return False
        
    def update_tables(self, dt, cnt):
        bln, b_cnt = self.iscounted(dt)
        if bln:
            self.con.execute("update cnt_master set tweet_cnt=%d where created_at='%s'" % (b_cnt+cnt, dt))
        else:
            self.con.execute( "insert into cnt_master values(?,?)" , (dt, cnt) )
        self.dbcommit()    
        
    def iscounted(self, dt):
        res = self.con.execute("select tweet_cnt from cnt_master where created_at='%s'" % dt).fetchone()
        if res is not None: return True, res[0]
        else: return False, ''
        
    def create_tables(self):
        t_name = ('tweet_master', 'cnt_master')
        """
        sql = "selcet name from sqlite_master where type='talbe' and name=%s" % t_name 
        res = self.con.execute(sql).fetchone()
        if res is not None:
            self.con.execute("drop table %s" % t_name)
        """
        self.con.execute("create table %s(tweet_id, screen_name, created_at, tweet, wordlist)" % t_name[0])
        self.con.execute("create table %s(created_at, tweet_cnt)" % t_name[1])
        self.con.execute("create index on %s(tweet_id, created_at)" % t_name[0])
        self.con.execute("create index timeidx  on %s(created_at)" % t_name[1])

if __name__=='__main__':
    dpath = 'D:/workspace/python/MyPythonApp/src/twitter/'
    with open(os.path.join(dpath, 'token.json')) as f:
        token = json.load(f)
    with open(os.path.join(dpath, 'consumer.json')) as f:
        consumer = json.load(f)
    
    dbname = 'test_tweet.db'
    src = Searcher(token, consumer, dbname)

    auth = src.get_oauth()
    api = API(auth)

    query = u'火事'
    while 1:
        try:
            src.search_tweet(query)
        except Exception, e:
            print "error is:", e
            print "sleeping..."
            time.sleep(60*15)
            src.search_tweet(query)