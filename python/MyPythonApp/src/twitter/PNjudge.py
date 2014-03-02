# coding: utf-8
'''
Created on 2014/02/17

@author: nahki
'''
"""
retweet, mention, url,hashtagはurl, hashtagのみ取得する処理を施す
"""

import io
import unicodedata
import sqlite3 as sqlite
import pickle
from separatewords import MecabTokenize
from normalizewords import Transform

def get_pnelist(pne_fname):
    """ 名詞評価極性辞書を読み込む  """
    pne = []
    with open('pne.txt','r', 1000) as in_file:
        for line in in_file:
            line = line.strip().split('\t')
            if line[1] == 'p': score = 1.0
            elif line[1] == 'e': score = 0.5
            elif line[1] == 'n': score = 0.0
            
            # unicode正規化
            string = unicodedata.normalize('NFKC', unicode(line[0]))
            string = Transform.tf_cnvk(string.upper())
            pne.append((string.encode('utf-8'), score))
    return pne
    
# トークンのリストのP/Nを判定する。
def judge_pn(tokens,pne):
    score = 0
    num_score = 0
    for token in tokens:
        for _pne in pne:
            if token == _pne[0]:
                score += _pne[1]
                num_score += 1
    if num_score != 0:
        pn_rate = float(score)/float(num_score)
    else: pn_rate = 0.5 # あとで0.0に変換?
    
    return pn_rate

# 個々のツイート本文をトークン化
def tokenize_list(text):
    return MecabTokenize.tokenize(text) # 形態素分析 

# P/E/Nスコアを算出して出力する
def get_scores(pn, pen, pen_num):
    if pn > 0.5: 
        pen[0] += pn
        pen_num[0] += 1
    elif pn == 0.5:
        pen[1] += pn
        pen_num[1] += 1
    elif pn < 0.5:
        pen[2] += pn
        pen_num[2] += 1    
    return pen, pen_num
    
class DataStorage:
    def __init__(self,dbname,t_name='pnscore'):
        self.dbname = dbname 
        self.con = sqlite.connect(dbname) # tableが存在した場合はdropさせているので注意
        self.table_name = t_name
        self.con.text_factory = str # utf-8を使用するためにstrを指定
        self.TIME_SPAN = 5
        
        # table作成
        self.createindextables()
        
    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    # pnラベル付け
    def get_label(self,pn_score):
        if pn_score > 0.5:
            label = 'p'
        elif pn_score == 0.5:
            label = 'e'
        else:
            label = 'n'
        return label

    # time stampの分割
    def get_time_label(self, dtime):
        ymd, time = dtime.split(' ')
        year, month, day = ymd.split('-')        

        hour, minit, second = time.split(':')
        tag = '%02d' %( ( int(minit) % self.TIME_SPAN )*self.TIME_SPAN )
        
        return year, month, day, hour, tag

    # 個々の結果を格納する
    def addtoindex(self, tweet, words, pn_score, dtime):
#        if self.isindexed(tweet): return
        print 'Indexing: ' + tweet

        # 年、月、時間などの取得
        year, month, day, hour, time_tag = self.get_time_label(dtime)

        # ポジネガのラベル取得
        pn_label = self.get_label(pn_score)
        # tweet毎に単語リストをDBに格納
        self.con.execute( "insert into %s values(?,?,?,?,?,?)" % (self.table_name) , \
                            (tweet, pickle.dumps(words), pn_score, pn_label, dtime,time_tag) )
        self.dbcommit()
    
    # tweetが既にインデックスされていたらtureを返す
    def isindexed(self,tweet):
        u=self.con.execute \
            ("select pn_score from %s where tweet='%s'" % (self.table_name, tweet)).fetchone()
        if u!=None:
            return True
        return False
    
    # データベースのテーブルを作る
    def createindextables(self):
        sql="SELECT name FROM sqlite_master WHERE type='table' AND name='MYTABLE';" \
                .replace('MYTABLE', self.table_name)
        res = self.con.execute(sql).fetchone()
        if res is None: # tableの存在確認
            self.con.execute('create table %s(tweet, wordlist, pn_score, pn_label, dtime, time_tag)' % (self.table_name))
            self.con.execute('create index tweetidx on %s(tweet)' % (self.table_name))
            self.dbcommit()
        else:
            self.con.execute('drop table %s' % (self.table_name))
            self.con.execute('create table %s(tweet, wordlist, pn_score, pn_label, dtime, time_tag)' % (self.table_name))
            self.con.execute('create index tweetidx on %s(tweet)' % (self.table_name))
            self.dbcommit()

if __name__ == '__main__':
    in_fn = 'D:/workspace/python/MyPythonApp/works/output/asumama_test.txt'
    pne_fname = 'pne.txt'
    dbname = 'pnscore.db'
    db = DataStorage(dbname)
    pne = get_pnelist(pne_fname)

    pne_score = [0.0, 0.0, 0.0]
    pne_num = [0.0, 0.0, 0.0]
    with open(in_fn, 'r', 1000) as in_f:
        for line in in_f:
            dtime = line.strip().split('\t')[1]
            text = line.strip().split('\t')[3].striop()

            # 文が10文字未満だとmecabがバグるので飛ばす
            if len(text.decode('utf-8')) < 10: continue
            sent = tokenize_list(text)
            # mecabがバグった場合はとばす
            if sent is None: continue
            
            pn_rate = judge_pn(sent, pne)            
            # db格納
            db.addtoindex(text, sent, pn_rate, dtime)
            print "%s\t%s\n" % (text, pn_rate)
            pne_score, pen_num = get_scores(pn_rate, pne_score, pne_num)
    sumation = sum(pen_num)
    print pne_score, pen_num
    print pne_score[0]/sumation, pne_score[1]/sumation, pne_score[2]/sumation