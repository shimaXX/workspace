# coding: utf-8
'''
Created on 2013/11/24

@author: nahki
'''

import urllib2
from BeautifulSoup import *
from urlparse import urljoin
import sqlite3 as sqlite
import SeparateWords


# 無視すべき単語のリスト
ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


class crawler:
    # データベースの名前でクローラを初期化
    def __init__(self, dbname):
        self.con=sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    # エントリIDを取得。
    # それが存在しない場合は追加をするための補助関数
    def getentryid(self,table,field,value,createnew=True):
        cur=self.con.execute(
                "select rowid from %s where %s='%s'" % (table,field,value))
        res=cur.fetchone()
        if res==None:
            cur=self.con.execute(
                    "insert into %s (%s) values ('%s')" % (table,field,value))
            return cur.lastrowid
        else:
            return res[0]

    # 個々のページをインデックスする
    def addtoindex(self,url,soup):
        if self.isindexed(url): return
        print 'Indexing' + url
        
        # 個々の単語を取得する
        text=self.gettextonly(soup)
        words=SeparateWords.separateWords(text)
                
        # URL idを取得する
        urlid=self.getentryid('urllist','url',url)
        
        # それぞれの単語と、このurlリンク
        for i in xrange(len(words)):
            word=words[i]
            if word in ignorewords: continue
            wordid=self.getentryid('wordlist','word',word)
            self.con.execute("insert into wordlocation(urlid,wordid,location) \
              values (%d,%d,%d)" % (urlid,wordid,i))
    
    # HTMLのページからタグのない状態でテキストを抽出する
    def gettextonly(self,soup):
        v=soup.string
        if v==None:
            c=soup.contents
            resulttext=''
            for t in c:
                subtext=self.gettextonly(t)
                resulttext+=subtext+'\n'
            return resulttext
        else:
            return v.strip()

    # 空白以外の文字で単語を分割する
    def separatewords(self,text):
        return None
    
    # URLが既にインデックスされていたらtureを返す
    def isindexed(self,url):
        u=self.con.execute \
            ("select rowid from urllist where url='%s'" % url).fetchone()
        if u!=None:
            # URLが実際にクロールされているかどうかチェックする
            v=self.con.execute(
                'select * from wordlocation where urlid=%d' % u[0]).fetchone()
            if v!=None: return True
        return False
    
    # 2つのページの間にリンクを付け加える
    def addlinkref(self,urlFrom,urlTo,linkText):
        words=SeparateWords.separateWords(linkText)
        fromid=self.getentryid('urllist','url',urlFrom)
        toid=self.getentryid('urllist','url',urlTo)
        if fromid==toid: return
        cur=self.con.execute("insert into link(fromid,toid) values(%d,%d)" % (fromid,toid))
        linkid=cur.lastrowid
        for word in words:
            if word in ignorewords: continue
            wordid=self.getentryid('wordlist','word',word)
            self.con.execute("insert into linkwords(linkid,wordid) values (%d,%d)" % \
            (linkid,wordid))
    
    # ページのリストを受け取り、与えられた深さで幅優先の検索を行い
    # ページをインデクシングする
    def crawl(self,pages,depth=2):
        for i in xrange(depth):
            newpages=set()
            for page in pages:
                try:
                    c=urllib2.urlopen(page)
                except:
                    print "Could not open %s" % page
                    continue
                soup=BeautifulSoup(c.read())
                self.addtoindex(page,soup)
                
                links=soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url=urljoin(page,link['href'])
                        if url.find("'")!=-1: continue
                        url=url.split('#')[0] # フラグメント識別子を取り除く
                        if url[0:4]=='http' and not self.isindexed(url):
                            newpages.add(url)
                        linkText=self.gettextonly(link)
                        self.addlinkref(page,url,linkText)
        
                    self.dbcommit()
                pages=newpages

    # データベースのテーブルを作る
    def createindextables(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid,wordid,location)')
        self.con.execute('create table link(fromid integer, toid integer)')
        self.con.execute('create table linkwords(wordid,linkid)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.dbcommit()

if __name__=='__main__':
    pagelist=['http://www.fullspeed.co.jp/']
    crawler=crawler('spyder.db')
#    crawler.createindextables()
    crawler.crawl(pagelist,depth=3)
    
