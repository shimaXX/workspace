#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append('c:\\python27\\libsvm-3.17\\python')
from PIL import Image
from pylab import *
import pickle
from sqlite3 import dbapi2 as sqlite
import PLSA
import numpy as np
from svm import *
from svmutil import *

class Indexer(object):

  def __init__(self,db,voc):
    """ データベース名とボキャブラリオブジェクトを
       用いて初期化する """

    self.con = sqlite.connect(db)
    self.voc = voc

  def __del__(self):
    self.con.close()

  def db_commit(self):
    self.con.commit()

  def create_tables(self):
    """ データベースのテーブルを作成する """
    self.con.execute('create table imlist(filename)')
    self.con.execute('create table imwords(imid,wordid,vocname)')
    self.con.execute('create table imhistograms(imid,histogram,vocname)')
    self.con.execute('create index im_idx on imlist(filename)')
    self.con.execute('create index wordid_idx on imwords(wordid)')
    self.con.execute('create index imid_idx on imwords(imid)')
    self.con.execute('create index imidhist_idx on imhistograms(imid)')
    self.db_commit()


  def add_to_index(self,imname,descr):
    """ 画像と特徴量記述子を入力し、ボキャブラリに
       射影して、データベースに追加する """

    if self.is_indexed(imname): return
    print 'indexing', imname

    # 画像IDを取得する
    imid = self.get_id(imname)

    # ワードを取得する
    imwords = self.voc.project(descr)
    nbr_words = imwords.shape[0]

    # 各ワードを画像に関係づける
    for i in range(nbr_words):
      word = imwords[i]
      # ワード番号をワードIDとする
      self.con.execute("insert into imwords(imid,wordid,vocname) \
        values (?,?,?)", (imid,word,self.voc.name))

    # 画像のワードヒストグラムを記録する
    # NumPyの配列を文字列に変換するためにpickleを用いる
    self.con.execute("insert into imhistograms(imid,histogram,vocname) \
      values (?,?,?)", (imid,pickle.dumps(imwords),self.voc.name))

  def is_indexed(self,imname):
    """ imnameがインデクスを持っていればTrueを返す """

    im = self.con.execute("select rowid from imlist where \
          filename='%s'" % imname).fetchone()
    return im != None

  def get_id(self,imname):
    """ 成分のIDを取得する。なければ追加する """

    cur = self.con.execute(
      "select rowid from imlist where filename='%s'" % imname)
    res=cur.fetchone()
    if res==None:
      cur = self.con.execute(
        "insert into imlist(filename) values ('%s')" % imname)
      return cur.lastrowid
    else:
      return res[0]


class Searcher(object):

  def __init__(self,db,voc):
    """ データベース名とボキャブラリを用いて初期化する """
    self.con = sqlite.connect(db)
    self.voc = voc

  def __del__(self):
    self.con.close()

  def candidates_from_word(self,imword):
    """ imwordを含む画像のリストを取得する """

    im_ids = self.con.execute(
      "select distinct imid from imwords where wordid=%d" % imword).fetchall()
    return [i[0] for i in im_ids]

  def candidates_from_histogram(self,imwords):
    """ 複数の類似ワードを持つ画像のリストを取得する """

    # ワードのIDを取得する
    words = imwords.nonzero()[0]

    # 候補を見つける
    candidates = []
    for word in words:
      c = self.candidates_from_word(word)
      candidates+=c

    # 全ワードを重複なく抽出し、出現回数の大きい順にソートする
    tmp = [(w,candidates.count(w)) for w in set(candidates)]
    tmp.sort(cmp=lambda x,y:cmp(x[1],y[1]))
    tmp.reverse()

    # 一致するものほど先になるようにソートしたリストを返す
    return [w[0] for w in tmp]

  def get_imhistogram(self,imname):
    """ 画像のワードヒストグラムを返す """
    im_id = self.con.execute(
      "select rowid from imlist where filename='%s'" % imname).fetchone()
    s = self.con.execute(
      "select histogram from imhistograms where rowid='%d'" % im_id).fetchone()

    # pickleを使って文字列をNumPy配列に変換する
    return pickle.loads(str(s[0]))

  def query(self,imname):
    """ imnameの画像に一致する画像のリストを見つける """
    #nz = 2 # plsaで扱う潜在変数の数
    
    h = self.get_imhistogram(imname)
    candidates = self.candidates_from_histogram(h)
    
    matchscores = []
    # cand_hm = [] # PLSAで類似度判定する場合は必要
    for imid in candidates:
      # 名前を取得する
      cand_name = self.con.execute(
        "select filename from imlist where rowid=%d" % imid).fetchone()
      cand_h = self.get_imhistogram(cand_name)
      #cand_hm.append(cand_h) # PLSAで類似度判定する場合は必要 
    
    # PLSAによって類似度を算出
    """  
    matchscores = self.plsa(cand_hm, nz)
    matchscores.sort()
    """
    
    # ユークリッド距離を使用して類似判定を行う場合はこちらを使用する
    for imid in candidates:
      # 名前を取得する
      cand_name = self.con.execute(
        "select filename from imlist where rowid=%d" % imid).fetchone()
      cand_h = self.get_imhistogram(cand_name)
            
      cand_dist = sqrt( sum( (h-cand_h)**2 ) ) # L2距離を用いる。ここをsvmやRFに変更可能。
      matchscores.append( (cand_dist,imid) )
    
    mtch_lng = len(matchscores)
    #print mtch_lng  
    # 距離の小さい順にソートした距離と画像IDを返す
    if mtch_lng < 4:
        for i in xrange(4 - mtch_lng): matchscores.append( (0,0) )
    
    matchscores.sort()
    return matchscores

  def get_filename(self,imid):
    """ 画像IDに対応するファイル名を返す """
  
    s = self.con.execute(
      "select filename from imlist where rowid='%d'" % imid).fetchone()
    print imid
    print s
    return s[0]

  def plsa(self,cand_hm,nz):
    ''' PLSAを使って類似度判定する場合にこちらを使用する '''
    cand_hm = np.array(cand_hm)
    p = PLSA.plsa(cand_hm, nz = nz)
    p.train()
    p.pzd
      
    ph = np.array(p.pzd[0])
    cnad_ph = p.pzd[1:]
    cand_dist = sqrt( sum( (ph-cnad_ph)**2 ) , axis = 0)
    matchscores = cand_dist
    return matchscores  

  def classify_via_svm(self, labels, imnames, HSV_fname):
    HSV_hist = np.loadtxt(HSV_fname)
    """ svmのtrainingを行う """
    # cand_hm = [] # PLSAで類似度判定する場合は必要
    # 名前を取得する
    cand_name = self.con.execute(
      #"select filename from imlist where filename not like '%images1%' and filename not like '%images2%'").fetchall()
      "select filename from imlist where filename not like '%images2%'").fetchall()
      #"select filename from imlist").fetchall()
      #"select filename from imlist where filename not like '%images1%' and filename not like '%01nail003%' \
      # and filename not like '%02tip003%'").fetchall()
    #cand_name = imnames
    hist = []
    itr = 0
    for cn in cand_name: 
        cand_h = self.get_imhistogram(cn)
        #cand_h = np.float32(cand_h)/np.max(cand_h)
        #tmp = np.hstack((cand_h, HSV_hist[itr]))
        hist.append(cand_h.tolist())
        itr += 1
    print "len", len(hist)
    print "label", len(labels)
    problem = svm_problem(labels,hist)
    param = svm_parameter('-s 0 -t 2') # デフォルト0 -- C-SVC、2 -- 動径基底関数カーネル: K(u,v) = exp(-&gamma |u-v|2)。 -b　1でpredictionで確率表示
    m = svm_train(problem, param) #学習
    p_labels, p_acc, p_vals = svm_predict(labels, hist, m)
    return p_labels, m #予測結果 

  def get_hist(self):
    # 名前を取得する
    cand_name = self.con.execute(
      "select filename from imlist").fetchall()
    hist = []
    for cn in cand_name:
        cand_h = self.get_imhistogram(cn)
        hist.append(cand_h.tolist())
    return hist      

  def get_pred_hist(self):
    # 名前を取得する
    cand_name = self.con.execute(
      #"select filename from imlist where filename like '%images1%' or filename like '%images2%'").fetchall()
      "select filename from imlist where filename like '%images2%'").fetchall()
      #"select filename from imlist").fetchall()
      #"select filename from imlist where filename like '%images1%' or filename like '%01nail003%' \
      # or filename like '%02tip003%'").fetchall()
    hist = []
    for cn in cand_name:
        cand_h = self.get_imhistogram(cn)
        hist.append(cand_h.tolist())
    return hist      

def compute_ukbench_score(src,imlist):
  """ 検索結果の上位4件のうち、正解数の平均を返す """

  nbr_images = len(imlist)
  pos = zeros((nbr_images,4))
  # 各画像の検索結果の上位4件を得る
  for i in xrange(nbr_images):
    pos[i] = [w[1]-1 for w in src.query(imlist[i])[:4]]

  # スコアを計算して平均を返す
  score = array([ (pos[i]//4)==(i//4) for i in xrange(nbr_images)])*1.0
  return sum(score) / (nbr_images)

def plot_results(src,res):
  """ 検索結果リスト'res'の画像を表示する """

  figure()
  nbr_results = len(res)
  print nbr_results
  for i in xrange(nbr_results):
    if res[i] == 0: continue
    imname = src.get_filename(res[i])
    subplot(1,nbr_results,i+1)
    imshow(array(Image.open(imname)))
    axis('off')
  show()

class Deleter(object):    
    def __init__(self,db):
        """ データベース名とボキャブラリを用いて初期化する """
        self.con = sqlite.connect(db)

    def __del__(self):
        self.con.close()
        
    def db_commit(self):
        self.con.commit()

    def delete_recode(self, ):
        """ k-meanで取得した内容を更新するためレコードを削除する """
        self.con.execute(u"delete wordid, vcname from imwords ")
        self.con.execute(u"delete histogram, vocname from imhistograms ")
