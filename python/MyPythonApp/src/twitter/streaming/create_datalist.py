# coding: utf-8

import sqlite3 as sqlite
from collections import defaultdict
import cPickle as pickle
import copy
import matplotlib.pyplot as plt
import re, unicodedata
from normalizewords import Replace
from math import floor, sqrt

stopword = ('ＵＲＬＵＲＬＵＲＬ','＃', '?', '・', 'Д', '°', '・・', 'ＷＷ', 'ＷＷＷ', 'Ｗ', '▽',r'¥','⊖'
            '〜','♡','〜。','〜（','゚','！！','≡','ぁ','✌','▔•','ＡＴ','ＳＴＡ','ＯＴＨＥＲＳ','✩〃',
            '！！！（','））））！','（（（（','ーーー','ーー','ー','（＊°','∪','｜⊂','•▔','✧','∩。','。∩',
            '‐‐，','！！！','♡♡', 'ＲＴ','‐','！！！','❤','♪（','•','⚽','∴。',' ＺＺＺＺＺ','ＺＺＺ',
            '♥','‖','｜｜', '｜／','＿＿＿','∪∪','⊃','ＷＷＷＷ','ＷＷＷＷＷ','ＷＷＷＷＷＷ',
            '∴','∥','⌒','±','∀','￥￥','∩','➡','ーーーー','ーーーー','☻♡','ーーーーーー','ーーーーーー',
            'ーーーーー')

class DataCreater:
    date = []
    tweet_cnt = []
    ex_words_store = []
    now_words_store = []
    new_break_words = set()
    bin_cnt = 0
    p = re.compile("[!-/:-@[-`{-~]")
    
    def __init__(self, dbname, word_limit, ofname, oftcntname,ofnewword,ofcos):
        self.con = sqlite.connect(dbname)
        self.word_limit = word_limit
        self.ofword = open(ofname, 'w',1000)
        self.oftcnt = open(oftcntname, 'w',1000)
        self.ofnewwords = open(ofnewword,'w',1000)
        self.ofcos = open(ofcos,'w',1000)
    
    def __def__(self):
        self.ofword.close()
        self.oftcnt.close()
        self.ofnewwords.close()
    
    def re_aggregate(self,span,con_bin=10):
        """ using all function(i think...) """
        
        response = self.get_data_yeald()
        itr, tweet_cnt, word_cnt = self.initiarize_cnt()
        s_date = None
        while 1:
            res = response.fetchone()
            if res is None: break

            #print res[0]+', '+res[1]+', '+res[2]+', '+str(res[4])
            tweet_cnt += int(res[4])
            word_cnt = self.aggregate_word_cnt(pickle.loads(str(res[3])), word_cnt) 
            
            if itr==0:
                s_date = res[0]+' '+res[1].zfill(2)+':'+res[2]
                
            if itr == span-1:
                date = res[0]+' '+res[1].zfill(2)+':'+res[2]
                sorted_word_list = self.sort_word_dict(word_cnt)
                self.output_top10_word(s_date, sorted_word_list)
                self.output_tweet_cnt(s_date, tweet_cnt)
                self.date.append(s_date)
                self.tweet_cnt.append(tweet_cnt)
                s_date = date                
                    
                self.bin_cnt += 1
                self.store_now_dict(sorted_word_list[:self.word_limit])
                print len(self.now_words_store)
                if self.bin_cnt >= con_bin:
                    if len(self.ex_words_store)!=0:
                        self.store_new_words(sorted_word_list[:self.word_limit])
                        cos_sim = self.calculate_cos_similarity(sorted_word_list[:self.word_limit])
                        self.output_new_words(s_date)
                        self.output_cos_sim(s_date,cos_sim)
                        self.ex_words_store = copy.deepcopy( self.now_words_store )
                        self.now_words_store.pop(0)
                        self.new_break_words = set()
                    else:
                        self.ex_words_store = copy.deepcopy( self.now_words_store )
                        self.now_words_store.pop(0)
                    
                itr, tweet_cnt, word_cnt = self.initiarize_cnt()
            else:
                itr += 1
                
    def get_data_yeald(self, start_date=None, end_date=None):        
        return self.con.execute("select ymd, hour, minute, word_dict,tweet_cnt from word_count")            
                
    def initiarize_cnt(self):
        return 0, 0, defaultdict(int)

    def aggregate_word_cnt(self, new_word_dic, orig_word_dic):
        for k,v in new_word_dic.items():
            if k not in stopword:
                m = self.p.search(unicodedata.normalize('NFKC', unicode(k)))
                if m is None:
                    orig_word_dic[k] += v
        return orig_word_dic
    
    def sort_word_dict(self, word_dict):
        lst = word_dict.items()
        lst.sort(lambda p0,p1: cmp(p1[1],p0[1])) # get Top 10 data
        return lst
            
    def calculate_cos_similarity(self, sorted_wordlist):
        ex_words =[]
        now_word_list = []
        for w_list in self.ex_words_store:
            ex_words +=w_list  
        for k,_ in sorted_wordlist:
            now_word_list.append(k)
        numerator = sum([1 for c in now_word_list if c in ex_words])
        denominator =  sqrt(len(ex_words) * len(now_word_list))
        return 1-float(numerator) / denominator if denominator != 0 else 1        
            
    def output_top10_word(self, date, sorted_word_list):
        if len(sorted_word_list) >=self.word_limit:
            s_list = [ st[0]+':'+str(st[1]) for st in sorted_word_list[:self.word_limit]]
            s = '\t'.join(s_list)
            self.ofword.write(date+'\t'+s+'\n')
        else:
            s_list = [ st[0]+':'+str(st[1]) for st in sorted_word_list[:self.word_limit]]
            s = '\t'.join(s_list)
            self.ofword.write(date+'\t'+s+'\n')

    def output_tweet_cnt(self, date, cnt):
        s = date+'\t'+str(cnt)
        self.oftcnt.write(s+'\n')

    def output_new_words(self,date):
        s = '\t'.join(list(self.new_break_words))
        print date, s
        self.ofnewwords.write(date+'\t'+s+'\n')
        
    def output_cos_sim(self, date, cos_sim):
        self.ofcos.write(date+'\t'+str(cos_sim)+'\n')
        
    def store_now_dict(self, sorted_wordlist):
        words = [k for k,_ in sorted_wordlist]
        self.now_words_store.append(words)
    
    def store_new_words(self, sorted_wordlist):
        ex_words =[]
        for w_list in self.ex_words_store:
            ex_words +=w_list  
        for k,_ in sorted_wordlist:
            if k not in ex_words:
                self.new_break_words.add(k)

if __name__=='__main__':
    dbname = 'stream_word_cnt.db'
    ofname = 'topNwords'
    oftcnt = 'tweetcnt'
    ofnewword = 'newword'
    ofcos = 'cos_simularity'
    word_top = 100 # top何ワードを取得するか
    span = 6 # 10分単位のカウント何個分を結合して再集計するか
    
    dc = DataCreater(dbname, word_top, ofname, oftcnt,ofnewword,ofcos)
    dc.re_aggregate(span,con_bin=24) #con_binはspan何個分のデータのwordに含まれていないかを確認
    
    tick = int(floor(len(dc.tweet_cnt)/7))
    
    plt.plot(range(len(dc.tweet_cnt)), dc.tweet_cnt)
    plt.xticks(range(0, len(dc.tweet_cnt), tick), dc.date[::tick], rotation=40)
    plt.show()