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
import json
from tweepy.auth import OAuthHandler
from tweepy.api import API
from tweepy import Cursor
import sqlite3 as sqlite
import pickle

from datetime import datetime, timedelta
from collections import defaultdict
import base64

from normalizewords import Transform, Replace
from bayesclassifer import BF
from cos_sim_filter import CosSimFilter
from separatewords import MecabTokenize


class Searcher:
    d_time = None
    cnt = 0
    before_text = defaultdict(int)
    word_dict = defaultdict(int)
    sequence_cnt = 0
    N = 20
    
    def __init__(self, token, consumer, dbname, blacklist_dbname, trained_dbname):
        self.token=token
        self.consumer=consumer
        self.db = DBCreater(dbname)
        #self.db.drop_table()
        #self.db.create_tables()
        self.bllist_con = sqlite.connect(blacklist_dbname)
        #self.bf = BF(trained_dbname) # introduce bayes clussifer
        self.csf = CosSimFilter(dbname, self.N) # filtere top N words
    
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

            from_date = dt - timedelta(minutes=1) - timedelta(hours=24)
            from_date = from_date.strftime('%Y-%m-%d %H:%M')
            to_date = dt - timedelta(minutes=1)
            to_date = to_date.strftime('%Y-%m-%d %H:%M')

            dt = dt.strftime('%Y-%m-%d %H:%M')
            if self.d_time != dt:
                print self.d_time
                if self.d_time is not None:
                    self.db.update_tables(self.d_time, self.cnt)
                    self.db.update_dict_tables(dt, self.word_dict)
                    self.before_text = defaultdict(int)
                    self.word_dict = defaultdict(int)
                self.d_time = dt
                self.cnt = 0
            
            # get userID and text
            name = tweet.user.screen_name
            text = tweet.text.strip()
            text_rep_rt = re.sub(ur'Retweet', '', text)
            text_rep_hasht = re.sub(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?#＃)[\s　,、\.。$]', '', text_rep_rt)
            text_rep_men = re.sub(ur'@(.*?)[\s:]', '', text_rep_hasht)
            text_rep_url = re.sub(ur'(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)', '', text_rep_men)
            self.before_text[text_rep_url] +=1
            if self.before_text[text_rep_url]>3:  print 'skip the tweet.reason is sequencing.  :', text; continue
            
#            if self.check_name(name): print 'skip:', text; continue # except news tweet
#            if self.check_blacklist(name): print 'skip:', text; continue # except spam tweet and news tweet
            
            text = re.sub(r'[(\n)(\r)]', '￥ｎ', text)
            text = Replace.str_replace(text)
            print "rep:", text
            # normalize text
            text = Transform.tf_unicodenorm(text)
            
            # judge spam and  get wordlist
            res = self.get_word_list(text)
            if res is None: print 'skip:', text; continue
            
            #res = self.bf.classify(blacklist_dbname, name, text)
            wordlist, urls = res
            res = self.csf.filter(wordlist, from_date, to_date)
            if res is None: print 'skip:', text; continue
            
            self.create_word_dict(wordlist)
            
            # get geo data
            geo = tweet.geo # [緯度, 経度]
            geo=  geo['coordinates'] if  geo is not None else '' 
            if self.db.isnewdata(tweet.id):
                t_date = tweet.created_at + timedelta(hours=9)
                self.db.addtoindex(tweet.id, name, t_date , text, wordlist, urls, geo)
                self.cnt += 1
            else: break
        time.sleep(40)

    def create_word_dict(self,word_list):
        for w in word_list:
            self.word_dict[w]+=1

    def get_word_list(self, tweet):
        res = self.separate_words(tweet)
        if res is None: return None        
        return res[0], res[1]

    def separate_words(self, tweet):
        # 文が10文字未満だとmecabがバグるので飛ばす
        if len(tweet.decode('utf-8')) < 10: return None
        res = MecabTokenize.tokenize(tweet)
        if res is None: return None
        else:
            if len(res[0])==0: return None
            return res[0], res[1]

class DBCreater:
    def __init__(self,dbname):
        self.con = sqlite.connect(dbname, isolation_level='EXCLUSIVE')
        self.con.text_factory = str # utf-8を使用するためにstrを指定
        try: self.create_tables()
        except: pass
        
    def __del__(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()
        
    def addtoindex(self, tweet_id, screen_name, created_at, tweet, wordlist, urls, geo):
        self.con.execute( "insert into tweet_master values(?,?,?,?,?,?,?)", \
                            (tweet_id, screen_name, created_at, tweet, pickle.dumps(wordlist), pickle.dumps(urls),pickle.dumps(geo)))
        self.dbcommit()
    
    def isnewdata(self, tweet_id):
        res = self.con.execute("select tweet_id from tweet_master where tweet_id=%s" % tweet_id).fetchone()
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
    
    def update_dict_tables(self, dt, word_dict):
        indexed_flag, w_dict = self.isindexed(dt)
        if indexed_flag:
            for k,v in word_dict.items():
                if '\\' not in k or ' ' not in k:
                    w_dict[k]+=v
            self.con.execute("update dict set word_dict=?" , (pickle.dumps(w_dict),) )
        else:
            self.con.execute("insert into dict values(?,?)", (dt, pickle.dumps(word_dict)))
        self.dbcommit()
        
    def isindexed(self, dt):
        res = self.con.execute("select word_dict from dict where created_at='%s'" % dt).fetchone()
        if res is not None: return True, pickle.loads(res[0])
        else: return False, ''
      
    def drop_table(self):
        self.con.execute("drop table dict")
        self.dbcommit()
        
    def create_tables(self):
        t_name = ('tweet_master', 'cnt_master', 'dict')

        sql = "select name from sqlite_master where type='talbe' and name='%s'" % t_name[2]
        res = self.con.execute(sql).fetchone()
        """
        if res is not None:
            self.con.execute("drop table %s" % t_name)
        """
        if res is None:
            """
            self.con.execute("create table %s(tweet_id, screen_name, created_at, tweet, wordlist, urls, geo)" % t_name[0])
            self.con.execute("create table %s(created_at, tweet_cnt)" % t_name[1])
            self.con.execute("create index on %s(tweet_id, created_at)" % t_name[0])
            self.con.execute("create index timeidx  on %s(created_at)" % t_name[1])
            """
            self.con.execute("create table %s(created_at, word_dict)" % t_name[2])
            self.con.execute("create index timeidx on %s(created_at)" % t_name[2])


def do_loop(func,query):
    while 1:
        try:
            func.search_tweet(query)
        except Exception, e:
            import traceback
            print traceback.format_exc()
            print "error is:", e
            print "sleeping..."
            time.sleep(60*15)
            do_loop(func, query)

if __name__=='__main__':
    with open('token.json') as f:
        token = json.load(f)
    with open('consumer.json') as f:
        consumer = json.load(f)
    
    trained_dbname = 'kaji_NB_full.db'
    blacklist_dbname = 'black_list.db'
    dbname = 'test_tweet.db'
    src = Searcher(token, consumer, dbname, blacklist_dbname, trained_dbname)

    auth = src.get_oauth()
    api = API(auth)

    query = u'火事'
    do_loop(src, query)