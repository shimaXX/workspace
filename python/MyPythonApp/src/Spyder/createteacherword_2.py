# coding: utf-8
'''
Created on 2013/11/24

@author: nahki
'''

import urllib, urllib2
from BeautifulSoup import BeautifulSoup, NavigableString, \
                             Declaration, Comment, BeautifulStoneSoup
import unicodedata
import chardet
from urlparse import urljoin, urlparse
import sqlite3 as sqlite
import pickle
import SeparateWords as spw

import time
import sys
sys.setrecursionlimit(10000) # 10000 is an example, try with different values

# 無視すべき単語のリスト
ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it', '-', '/', '#', "'", '_', ',', '(', ')', '[', ']', '〜', '!', '|', '♪', '...', '>', '<', ':', '!!', '&', '/', '+', '*'])
# ブロックとして認識するタグのリスト
block_tags = frozenset(['p', 'div', 'table', 'dl', 'ul', 'ol', 'form', 'address',
                   'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'fieldset',
                   'hr', 'pre' 'article', 'aside', 'dialog', 'figure',
                   'footer', 'header', 'legend', 'nav', 'section'])

class crawler:
    # データベースの名前でクローラを初期化
    def __init__(self, dbname):
        self.dbname = dbname
        self.con=sqlite.connect(dbname)
        self.con.text_factory = str # utf-8を使用するためにstrを指定
    
    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    # 個々のページをインデックスする
    def addtoindex(self,url,category,wordlist):
        if self.isindexed(url): return
        print 'Indexing: ' + url
                                
        # url毎に単語リストをDBに格納
        self.con.execute( "insert into wordvector values(?,?,?,?)" , \
                            (url, category, pickle.dumps(wordlist), '') )
        self.dbcommit()

    def getNavigableStrings(self,soup):
        # soupがcontentsを含む型かを判定
        if isinstance(soup, NavigableString): # NavigableStringオブジェクトはcontentsとstringを除く全てのメンバ変数を持つ
            if type(soup) not in (Comment, Declaration):
                yield soup
        # contentsを含んでいてprogram codeでなければテキストを取得
        elif soup.name not in ('script', 'style'):
            is_block = soup.name in block_tags # ブロックタグの存在を確認
            if is_block:
                yield u'\n'
            for c in soup.contents:
                for g in self.getNavigableStrings(c): # limit recursion number is 480. if over 480 raise the error.
                    yield replace_str(g)
            if is_block:
                yield u'\n'
    
    # URLが既にインデックスされていたらtureを返す
    def isindexed(self,url):
        u=self.con.execute \
            ("select words from wordvector where url='%s'" % url).fetchone()
        if u!=None:
            return True
        return False    
    
    # ページのリストを受け取り、与えられた深さで幅優先の検索を行い
    # ページをインデクシングする
    def crawl(self,pages,category,depth=2):
        for _ in xrange(depth):
            newpages=set()
            for page in pages:
                try:
                    response=urllib2.urlopen(page).read()
                except:
                    print "Could not open %s" % page
                    continue
                en = chardet.detect(response)['encoding']
                if en=='SHIFT_JIS': en = 'cp932'
                elif en is None: continue
                print "en=", en
                print "page=",page
                soup=BeautifulSoup(response.decode(en, 'ignore'), # 文字コードをサイトに合わせて変換
                        convertEntities = BeautifulStoneSoup.HTML_ENTITIES) # HTML特殊文字の文字変換
                text = u''.join( self.getNavigableStrings(soup) )
                text = normalizeText(text) # 文字列の正規化
                words = spw.separateWords(text) # 単語集合の取得
                self.addtoindex(page,category,words) # url, category, 単語集合をDBに保存
                
                # 深さ2以上の探索を行う場合のためにaタグのURLを取得
                links=soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url=urljoin(page,link['href'])
                        if url.find("'")!=-1: continue
                        url=url.split('#')[0] # フラグメント識別子を取り除く
                        if url[0:4]=='http' and not self.isindexed(url):
                            newpages.add(url)
                pages=newpages

    # データベースのテーブルを作る
    def createindextables(self):
        name = 'wordvector'
        sql="SELECT name FROM sqlite_master WHERE type='table' AND name='MYTABLE';" \
                .replace('MYTABLE', name)
        res = self.con.execute(sql).fetchone()
        if res is None:
            self.con.execute('create table wordvector(url, category, words, hash_vector)')
            self.con.execute('create index urlidx on wordvector(url)')
            self.dbcommit()
        else:
            self.con.execute('drop table wordvector')
            self.con.execute('create table wordvector(url, category, words, hash_vector)')
            self.con.execute('create index urlidx on wordvector(url)')
            self.dbcommit()            

    # google検索して基本wikipediaからデータを引っ張ってくる
    def serch_google(self,query):
        google_url = "http://www.google.co.jp/search?jl=ja&num=50&q="

        # make category
        category = u'/'.join(query)
        print category
        
        # make query
        for s in query: s.replace(u'と', u' or ')

        # mod query
        query = u' '.join(query) + u' wiki' #wikipedia
        query = urllib.quote(query.encode('utf-8'))

        page = google_url + query
        try:
            #response=urllib2.urlopen(page).read()
            opener = urllib2.build_opener()
            opener.addheaders = [\
                    ('Use-Agent', 'Mozilla/5.0 (compatible; googlebot/2.1; \
                      + http://www.google.com/bot.html)')]
            response = opener.open(page).read()
        except:
            print "Could not open %s" % page
            pass
        en = chardet.detect(response)['encoding']
        if en=='SHIFT_JIS': en = 'cp932'
        soup=BeautifulSoup(response.decode(en,'ignore'), # 文字コードをサイトに合わせて変換
                convertEntities = BeautifulStoneSoup.HTML_ENTITIES) # HTML特殊文字の文字変換
        targetlinks = soup.findAll('h3',{'class':'r'})
        links = [link.find('a') for link in targetlinks]
        #links=targetlinks.find('a')
#       newpages=set()
        for link in links:
            if ('href' in dict(link.attrs)):
                url=urljoin(page,link['href'])
                if url.find("'")!=-1: continue
                url=url.split('#')[0] # フラグメント識別子を取り除く
                if '/url?q=' in url:
                    self.crawl([url], category, depth=1)
            time.sleep(10)
#        return newpages

def nonEmptyLines(text):
    """ 不要な空白を取り除き，空行以外を返す """
    for line in text.splitlines():
        line = u' '.join(line.split())
        if line:
            yield line

def normalizeText(text):
    """ 正規化の後で不要な空白・改行を取り除く """
    text = unicodedata.normalize('NFKC', text) # 日本語半角を全角に変換+英数字,記号は半角
    return u'\n'.join(nonEmptyLines(text))

def replace_str(line):
    return line.replace('&amp;','&')

if __name__=='__main__':
    crawler=crawler('test.db')

    fname = 'C:/workspace/python/MyPython/works/input/categorys.txt'
    crawler.createindextables()
    with open(fname, 'r') as f:
        for line in f:
            s = line.strip().split('\t')
            crawler.serch_google(s) # wikipedia内の文字を取得します

#             pagelist = [s[1]]
#             crawler.crawl(pagelista, category, depth=1)