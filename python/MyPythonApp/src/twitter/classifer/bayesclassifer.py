# coding: utf-8
'''
Created on 2013/11/11

@author: RN-017
'''
import sqlite3 as sqlite
import pickle
from math import log, exp

from separatewords import MecabTokenize

class BF(object):
    """ベイズ分類器の訓練とテストを行う
    defaultでテーブルが存在していたら削除するので、
    既存のDBを使用する場合は、create_table=0を引数に加える
    """    
    def __init__(self, fname, dbname, use=0):
        """trainingではuse=0
        testではuse=1
        classifyではuse=2
        """
        self.fname = fname # input file name
        self.con = sqlite.connect(dbname)
        self.con.text_factory = str # utf-8を使用するためにstrを指定
        if use==0:
            self.createindextables() # tableの作成
        
        self.spam_denominator = 0.0
        self.ham_denominator = 0.0
        
        self.ham_weight = 1.0
        self.init_pai = 0.4
        self.threshold = 0.1

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()
                
    def train(self):
        """10文字未満のtweetは対象外とする"""
        with open(self.fname,'r', 1000) as trainf:
            for line in trainf:
                tid, dtime, aid, tweet, y = line.strip().split('\t')

                wordlist = self.get_wordlist(tweet)
                # 文が10文字未満だとmecabがバグるので飛ばす
                if wordlist == True: print 'skip: %s' % (tweet); continue
                
                y = int(0) if int(y)<1 else int(1)  # spam=1, ham=0に統一する
                
                self.addtoindex_tweet(tweet, wordlist, y, dtime)
                if y==1: self.addtoindex_class(wordlist,'spam_words')
                else: self.addtoindex_class(wordlist,'ham_words')
                self.addtoindex_score(wordlist)
        self.calc_denominator()
        self.calc_word_prob()
        self.predict()

    def test(self, ifname):
        """訓練済みDBを使用して交差検証を行う
        10文字未満のtweetは対象外とする
        """
        with open(ifname, 'r', 1000) as testf:
            prior_spam, prior_ham = self.calc_cat_prob() # p(spam), p(ham)
            log_prior_spam = log(prior_spam)
            log_prior_ham = log(prior_ham)

            res = []
            ans = [0.0, 0.0, 0.0, 0.0]
            
            for line in testf:
                tid, dtime, aid, tweet, y = line.strip().split('\t')
                print 'testing:', tweet
                
                wordlist = self.get_wordlist(tweet)
                # 文が10文字未満だとmecabがバグるので飛ばす
                if wordlist == True: print 'skip: %s' % (tweet); continue
                
                y = int(0) if int(y)<1 else int(1)  # spam=1, ham=0に統一する
                
                spam_score = self.pred_score(wordlist,log_prior_spam,log_prior_ham)
                res = 1 if spam_score > 0.5 else 0
                
                # 結果の表の計算
                ans = self.get_ans(ans, y, res)
            print ans
                             
    def classify(self,clfname,classify_dbname):
        """10文字未満のtweetは対象外とする"""
        self.clsfdb_con = sqlite.connect(classify_dbname)
        self.create_classified_indextables()
        self.clsfdb_con.text_factory = str # utf-8を使用するためにstrを指定
        
        with open(clfname, 'r', 1000) as testf:
            prior_spam, prior_ham = self.calc_cat_prob() # p(spam), p(ham)
            log_prior_spam = log(prior_spam)
            log_prior_ham = log(prior_ham)
            
            for line in testf:
                tid, dtime, aid, tweet = line.strip().split('\t')
                
                wordlist = self.get_wordlist(tweet)
                # 文が10文字未満だとmecabがバグるので飛ばす
                if wordlist == True: print 'skip: %s' % (tweet); continue

                spam_score = self.pred_score(wordlist,log_prior_spam,log_prior_ham)
                label = 1 if spam_score > 0.5 else 0
                self.addtoindex_classified_table(tweet, wordlist, spam_score, label, dtime)

    def pred_score(self,wordlist,log_prior_spam,log_prior_ham):
        """spam_scoreの推定する"""
        m = len(wordlist) - 1
        psm = m*log_prior_spam
        phm = m*log_prior_ham
        denom_prior = phm - psm
        denom_score = 0.0
        for word in wordlist:
            w_score = self.con.execute("select spam_score from words_score where word='%s'" % (word)).fetchone()
            if w_score is None: w_score = self.init_pai
            else: w_score = w_score[0]
            if abs(w_score-0.5) > self.threshold:
                denom_score += log(1-w_score) - log(w_score)
        denom = exp(denom_prior + denom_score)
        denom += 1
        prob_spam = float(1.0)/denom
        print 'spam_probability:', prob_spam
        
        return prob_spam
        # return 1 if prob_spam > 0.5 else 0

    def get_wordlist(self, tweet):
        # 文が10文字未満だとmecabがバグるので飛ばす
        if len(tweet.decode('utf-8')) < 10: return True
        wordlist = MecabTokenize.tokenize(tweet)
        if wordlist is None: return True
        else: return wordlist

    def get_ans(self,ans,y,res):
        if y==1 and res==1: # 真陽性
            ans[0] += 1
        elif y==1 and res==0: # 偽陽性
            ans[1] += 1
        elif y==0 and res==1: # 偽陰性
            ans[2] += 1
        else: # 真陰性
            ans[3] += 1
            
        return ans

    def predict(self):
        """ documentのカテゴリ所属確率を求め、所属するカテゴリを判定 
        p(category|document)
        """
        # 精度確認のための箱
        ans = [0.0, 0.0, 0.0, 0.0]

        prior_spam, prior_ham = self.calc_cat_prob() # p(spam), p(ham)
        log_prior_spam = log(prior_spam)
        log_prior_ham = log(prior_ham)
        wordlists = self.con.execute("select wordlist from tweet_master")
        true_labels = self.con.execute("select label from tweet_master")
        res = []
        while 1:
            tmp = wordlists.fetchone()
            if tmp == None: break
            wordlist = pickle.loads( tmp[0] )
            m = len(wordlist) - 1
            psm = m*log_prior_spam
            phm = m*log_prior_ham
            denom_prior = phm - psm
            denom_score = 0.0
            for word in wordlist:
#                print word
                w_score = self.con.execute("select spam_score from words_score where word='%s'" % (word)).fetchone()
                if w_score is None: w_score = self.init_pai
                else: w_score = w_score[0]
#                print w_score
                if abs(w_score-0.5) > self.threshold:
                    denom_score += log(1-w_score) - log(w_score)
            denom = exp(denom_prior + denom_score)
            denom += 1
            prob_spam = float(1.0)/denom
            print 'spam_probability:', prob_spam
            
            label = 1 if prob_spam > 0.5 else 0
            res.append(label)
            ans = self.get_ans(ans, true_labels.fetchone()[0], label)
        print ans
        print res
        
    def calc_word_prob(self):
        """ カテゴリ中の単語のスコア(確率)を求める 
        p(word_i|category)
        """
        # 計算にはラプラススムージングを使用する
        wordlist = self.con.execute("select word from words_score")
        while 1:
            word = wordlist.fetchone()
            if word == None: break
            word = word[0]
            w_cnt_spam, w_cnt_ham = self.cnt_word_of_cat(word)
            spam_prob = float(w_cnt_spam+1)/self.spam_denominator # ラプラススムージングのために1をプラス
            ham_prob = min(1, self.ham_weight*float(w_cnt_ham+1)/self.ham_denominator)
            spam_score = spam_prob/(spam_prob+ham_prob)
            self.update_word_score(word, spam_score)
        self.dbcommit()
        
    def calc_denominator(self):
        """ カテゴリ中の単語のスコア(確率)を求めるための計算用の分母を求めておく 
        """
        # 計算にはラプラススムージングを使用する
        uniq_cnt_spam, uniq_cnt_ham = self.cnt_uniq_word_of_cat()
        total_cnt_spam, total_cnt_ham = self.cnt_total_word_of_cat()
        self.spam_denominator = total_cnt_spam + uniq_cnt_spam # ラプラススムージングのためにユニークの数をカウント
        self.ham_denominator = total_cnt_ham + uniq_cnt_ham

    def cnt_word_of_cat(self,word):
        """ 各カテゴリ中の特定の単語数をカウント 
        T(cat,word_i)
        """
        w_cnt_spam = self.con.execute("select count(*) from spam_words where word ='%s'" % (word)).fetchone()[0]
        w_cnt_ham = self.con.execute("select count(*) from ham_words where word ='%s'" % (word)).fetchone()[0]
        if w_cnt_spam is None: w_cnt_spam = 0
        if w_cnt_ham is None: w_cnt_ham = 0
        return w_cnt_spam, w_cnt_ham
    
    def cnt_uniq_word_of_cat(self):
        """ 各カテゴリ中の全単語数をカウント
        p(word_i|cat)の分母の|V|
        """
        uniq_cnt_spam = self.con.execute("select count(distinct word) from spam_words").fetchone()[0]
        uniq_cnt_ham = self.con.execute("select count(distinct word) from ham_words").fetchone()[0]
        return uniq_cnt_spam, uniq_cnt_ham
        
    def cnt_total_word_of_cat(self):
        """ 各カテゴリ中の全単語の出現回数の総和
        ΣT(cat, word')
        """
        total_cnt_spam = self.con.execute("select count(*) from spam_words").fetchone()[0]
        total_cnt_ham = self.con.execute("select count(*) from ham_words").fetchone()[0]
        return total_cnt_spam, total_cnt_ham
    
    def calc_cat_prob(self):
        """ p(categories)の算出 """
        cnt_spam_tweet = self.con.execute("select count(*) from tweet_master where label=1").fetchone()[0]
        cnt_total_tweet = self.con.execute("select count(*) from tweet_master").fetchone()[0]
        
        cat_prob_spam = float(cnt_spam_tweet)/cnt_total_tweet
        return cat_prob_spam, 1.0-cat_prob_spam

    def addtoindex_tweet(self, tweet, wordlist, label, dtime):
        """ tweetを格納する """
#        if self.isindexed(tweet): return
        print 'Indexing: ' + tweet
            
        # tweet毎に単語リストをDBに格納
        self.con.execute( "insert into tweet_master values(?,?,?,?)", \
                            (tweet, pickle.dumps(wordlist), label, dtime) )
        self.dbcommit()

    def addtoindex_class(self, wordlist, class_table_name):
        """class毎にwordsを格納する"""
        # get tweet_id
        tweet_id = self.con.execute("select max(rowid) from tweet_master").fetchone()[0]
        
        # tweet_id毎に単語リストをDBに格納
        for word in wordlist:
            self.con.execute( "insert into %s values(?,?)" % (class_table_name), (tweet_id, word) )
        self.dbcommit()

    def addtoindex_score(self,wordlist):
        """score tableに単語を保存"""
        # 語リストをDBに格納
        for word in wordlist:
            if self.isindexed(word): continue
            else: 
                self.con.execute( "insert into words_score values(?,?)", (word, self.init_pai) ) # scoreには仮の値を入れる
        self.dbcommit()
        
    def addtoindex_classified_table(self, tweet, wordlist, spam_score, label, dtime):
        """ labelのついていないtweetを分類し格納する """
#        if self.isindexed(tweet): return
        print 'Classifying: ' + tweet
            
        # tweet毎に単語リストをDBに格納
        self.clsfdb_con.execute( "insert into tweet_master values(?,?,?,?,?)", \
                            (tweet, pickle.dumps(wordlist), spam_score, label, dtime) )
        self.clsfdb_con.commit()
        
    def isindexed(self,word):
        """ tweetが既にインデックスされていたらtureを返す """
        u=self.con.execute \
            ("select word from words_score where word='%s'" % (word)).fetchone()
        if u!=None: return True
        return False
     
    def update_word_score(self,word, spam_score):
        """単語ごとの各カテゴリへの所属確率を求める"""
        self.con.execute("update words_score set spam_score=%f where word='%s'" % \
                            (spam_score, word))
    
    def createindextables(self):
        """ データベースのテーブルを作る """
        tnlist = ['tweet_master' ,'spam_words', 'ham_words', 'words_score']

        for table_name in tnlist:        
            sql="SELECT name FROM sqlite_master WHERE type='table' AND name='MYTABLE';" \
                    .replace('MYTABLE', table_name)
            res = self.con.execute(sql).fetchone()
            if res is not None: # tableの存在確認
                self.con.execute('drop table %s' % (table_name))

        self.con.execute('create table tweet_master(tweet, wordlist, label, create_time)') # spamは1, hamは0
        self.con.execute('create table spam_words(tweet_id, word)')
        self.con.execute('create table ham_words(tweet_id, word)')
        self.con.execute('create table words_score(word, spam_score)')
        
        self.con.execute('create index tweetidx on tweet_master(tweet)')
        self.con.execute('create index spamidx on spam_words(word)')
        self.con.execute('create index hamidx on ham_words(word)')
        self.con.execute('create index scoreidx on words_score(word)')

        self.dbcommit()        

    def create_classified_indextables(self):
        """ データベースのテーブルを作る """
        table_name = 'tweet_master'

        sql="SELECT name FROM sqlite_master WHERE type='table' AND name='MYTABLE';" \
                .replace('MYTABLE', table_name)
        res = self.clsfdb_con.execute(sql).fetchone()
        if res is not None: # tableの存在確認
            self.clsfdb_con.execute('drop table %s' % (table_name))

        self.clsfdb_con.execute('create table tweet_master(tweet, wordlist, spam_score, label, create_time)') # spamは1, hamは0        
        self.clsfdb_con.execute('create index tweetidx on tweet_master(tweet)')
        self.clsfdb_con.commit()

if __name__=='__main__':
    """
    trfname = 'asumama_label_test.txt'
    dbname = 'asumama_bf.db'
    bf = BF(trfname, dbname, use=0) # 
    bf.train()
    """

    """
    tefname = 'asumama_label.txt'
    dbname = 'asumama_bf.db'
    bf = BF(tefname, dbname, use=1) # 
    bf.test(tefname)
    """
    
    clfname = 'D:/workspace/python/MyPythonApp/works/output/asumama.txt'
    trained_dbname = 'asumama_bf.db'
    classify_dbname = 'asumama_bf_classify.db'
    bf = BF(clfname, trained_dbname, use=2) # 
    bf.classify(clfname, classify_dbname)