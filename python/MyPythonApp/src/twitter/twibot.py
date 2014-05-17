# coding: utf-8
'''
Created on 2014/01/26

@author: nahki
'''
"""
retweet, mentionは置換 
url, hashtagは残したままで保存することのみを行う
文字正規化はunicode正規化のみ
全角化などはまだ行わない
連続文字などは置換する
"""
# See http://blog.unfindable.net/archives/4257                                                        
# See http://qiita.com/who_you_me/items/b469541b383f9f2088f2
# See http://kimux.net/?p=1378
# See http://tomono.eleho.net/2013/09/03/4505/
# See(about API) http://akiniwa.hatenablog.jp/entry/2013/07/30/110613
# See http://d.hatena.ne.jp/niiyan/20110525/1306335576
# tweepy cursor http://stackoverflow.com/questions/17371652/tweepy-twitter-api-not-returning-all-search-results
# network http://sub-tan.hatenablog.com/entry/2013/03/20/182250
# http://blog.glasses-factory.net/2011/04/11/GAE-py-for-Flasher---6-twitter
# http://waman.hatenablog.com/entry/20111004/1317684795
# twitter document https://dev.twitter.com/docs/api/1/get/search

""" API制限
At this time, users represented by access tokens can make 180 requests/queries per 15 minutes
Limit your searches to 10 keywords and operators
"""

import re
import unicodedata
import datetime, os
import json
from tweepy.streaming import StreamListener, Stream
from tweepy.auth import OAuthHandler
from tweepy.api import API
from tweepy import Cursor

from normalizewords import Transform, Replace

out_prefix = "D:/workspace/python/MyPythonApp/works/output/asumama_test"

dpath = 'D:/workspace/python/MyPythonApp/src/twitter/'
with open(os.path.join(dpath, 'token.json')) as f:
    token = json.load(f)
with open(os.path.join(dpath, 'consumer.json')) as f:
    consumer = json.load(f)

""" filter条件"""
locationsL=[122.87,24.84,153.01,46.80] # Any geotagged Tweet.https://dev.twitter.com/docs/streaming-apis/parameters#locations
# 122.87,24.84,153.01,46.80 日本のlocation
# -180,-90,180,90 指定なし
languages='ja'
rtype = 'mixed' # recent, popular, mixed
#trackL=[u'明日ママ']


def get_oauth():
    consumer_key = consumer['key']
    consumer_secret = consumer['secret']
    access_token = token['token']
    access_secret = token['secret']
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    return auth

def search_tweet(query):
    auth = get_oauth()
    api = API(auth)
    
    # ツイートの検索
    tweets = get_tweets(api, query)
    # ツイートの出力
    output_tweets(tweets)

def get_tweets(api, query):
    tweets = Cursor(api.search, 
                    q=query,
                    count=100,
                    #geocode=geo,
                    result_type=rtype, # recent, popular, mixed 
                    include_entities=True,
                    lang=languages).items()
    return tweets

def output_tweets(tweets):
    fout = open( "%s.txt" % (out_prefix), 'w' )
    for tweet in tweets:
        print "raw:", tweet.text
        #print dir(tweet)
        #res = str(tweet.created_at)+'->'+str(tweet.user.screen_name)+'\n'+tweet.text # author.nameは表示名, user.screen_nameはアカウントid
        text = tweet.text
        text = re.sub(r'[\n\r]', ' ', text)
        text = Replace.str_replace(text)
        print "rep:",text
        # 文字の正規化
        text = Transform.tf_unicodenorm(text)
        
        # 出力用に情報を絞る
        res = str(tweet.id)+'\t'+str(tweet.created_at)+'\t'+str(tweet.user.screen_name)+'\t'+text # author.nameは表示名, user.screen_nameはアカウントid
        print "status:", str(tweet.id)
        fout.write(res + "\n")

class ComentListener(StreamListener):
    def __init__(self, api=None):
        StreamListener.__init__(self, api)
        self.d = datetime.date.today()
        self.out_prefix = "D:/workspace/python/MyPythonApp/works/output/filter"
        self.fout = open("%s-%s.jsonl" % (self.out_prefix,  self.d.isoformat()), 'a' )
        self.day = self.d.day

    def on_data(self, data):
        if self.day != datetime.date.today().day:
            self.fout.close()
            self.fout = open("%s-%s.jsonl" % (self.out_prefix,  self.d.isoformat()), 'a' )

        if data.startswith("{"):
#            line = unicode(data, 'unicode_escape').encode('utf-8')
#            line = line.replace('\\', '')
            print data
            jd = json.loads(data)
            print jd['text'].encode('utf-8')
            #self.fout.write(data + "\n")

    def on_timeout(self):
        self.fout.close()
        raise Exception

if __name__=='__main__':
    auth = get_oauth()
#    stream = Stream(auth, ComentListener())
    
    api = API(auth)
    #htl = api.home_timeline()
    #tl = api.user_timeline(id='@WSJJapan',count=10)
    """
    keywords = [u'温泉津', u'石見銀山', u'仁摩', u'大田市', u'三瓶山', u'邇摩']
    query = ' OR '.join(keywords) # or条件はORを半角スペースで囲む
    """
    query = u'明日ママ'
    search_tweet(query)
    

    """
    while True:
        try:
            # stream.filter(track=trackL, locations=locationsL, languages=languagesL)
            stream.filter(track=['AKB'], locations=locationsL, languages=languagesL)
        except Exception:
            time.sleep(60)
            stream = Stream(auth, ComentListener())
    """