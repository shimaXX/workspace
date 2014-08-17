# coding: utf-8

import sqlite3 as sqlite
import io, os, re, time
from BeautifulSoup import BeautifulSoup, NavigableString, \
                             Declaration, Comment, BeautifulStoneSoup
import unicodedata
import chardet
from urlparse import urljoin, urlparse
import pickle
import urllib2
from separatewords import MecabTokenize

# ブロックとして認識するタグのリスト
block_tags = frozenset(['p', 'div', 'table', 'dl', 'ul', 'ol', 'form', 'address',
                   'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'fieldset',
                   'hr', 'pre' 'article', 'aside', 'dialog', 'figure',
                   'footer', 'header', 'legend', 'nav', 'section'])
init_male_score = 0.6

class CreateDB:
    def __init__(self,db,use=1):
        self.con = sqlite.connect(db)
        self.con.text_factory = str # utf-8を使用するためにstrを指定
        if use==1:
            self.create_tables()
    
    def __del__(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()

    def addtoindex(self, bloger, gender, url, article, wordlist, create_time):
        print 'indexing:', article
        # tweet毎に単語リストをDBに格納
        
        if wordlist is None: wordlist = ['－']
        self.con.execute( "insert into blog_master values(?,?,?,?,?,?)", \
                            (bloger, gender, url, article, pickle.dumps(wordlist), create_time ))
        if gender=='male':
            # 単語ごとにカウント
            for word in wordlist:
                res = self.con.execute("select word, word_cnt from male_words where word='%s'" % word).fetchone()
                if res is None:
                    self.con.execute( "insert into male_words values(?,?)", (word, 1) )                
                else:
                    new_cnt = int(res[1])+1
                    self.con.execute( "update male_words set word_cnt=%d where word='%s'" % (new_cnt, word) )
        else:
            # 単語ごとにカウント
            for word in wordlist:
                res = self.con.execute("select word, word_cnt from female_words where word='%s'" % word).fetchone()
                if res is None:
                    self.con.execute( "insert into female_words values(?,?)", (word, 1) )                
                else:
                    new_cnt = int(res[1])+1
                    self.con.execute( "update female_words set word_cnt=%d where word='%s'" % (new_cnt, word) )
        self.con.execute("insert into male_score values(?,?)", (word, init_male_score))
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

    def crawl(self, page, bloger, gender, depth=2):
        #for _ in xrange(depth):
        itr = 0
        while 1:
            if page is None or itr>=100: break
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
            try:
                article = soup.findAll('div', {'class':'articleText'})[0]
            except:
                article = soup.findAll('div',{'class':'subContentsInner'})[0]
            
            text = u''.join( self.getNavigableStrings(article) )
            text = normalizeText(text) # 文字列の正規化
            text= re.sub(ur'[\n\r]', '',text)
            
#            tl = len(unicode(text))-3
#            wordlist= [unicode(text)[i:i+3] for i in xrange(tl)]
            wordlist = MecabTokenize.tokenize(text) # 単語集合の取得
            
            try:
                date_tag = soup.findAll('span',{'class':'articleTime'})[0]
                create_time = date_tag.find('time').string[:10]
            except:
                create_time = soup.findAll('span',{'class':'date'})[0].string
            
            self.addtoindex(bloger, gender, page, text, wordlist, create_time) # url, category, 単語集合をDBに保存
            
            time.sleep(5)
            # 次へのリンクがある場合は次のページを取得
            try:
                link = soup.findAll('a', {'class':'pagingNext'})[0]
                url = self.get_url(page, link)
                if not url: continue
                page = url
                itr+=1
            except:
                try:
                    link = soup.findAll('a',{'class':'nextPage'})[0]
                    url = self.get_url(page, link)
                    if not url: continue
                    page = url
                    itr+=1
                except:
                    print "this blog haven't next article"
                    break
    
    def get_url(self, page, link):
        if ('href' in dict(link.attrs)):
            url=urljoin(page,link['href'])
            if url.find("'")!=-1: return False
            url=url.split('#')[0] # フラグメント識別子を取り除く
            if url[0:4]=='http' and not self.isindexed(url):
                return url
            
    def search_ameblo_top50(self):
        pagelist = ("http://official.ameba.jp/ranking/day/accessRankingType1-1.html", # 男性タレントtop50
                    "http://official.ameba.jp/ranking/day/accessRankingType2-1.html") # 女性タレントtop50
        genders = ('male','female')
        for i, page in enumerate(pagelist):
            gender = genders[i]
            try:
                response=urllib2.urlopen(page).read()
            except:
                print "Could not open %s" % page
                pass
            en = chardet.detect(response)['encoding']
            if en=='SHIFT_JIS': en = 'cp932'
            soup=BeautifulSoup(response.decode(en,'ignore'), # 文字コードをサイトに合わせて変換
                    convertEntities = BeautifulStoneSoup.HTML_ENTITIES) # HTML特殊文字の文字変換

            # get bloger
            bloger_tag = soup.findAll('dd', {'class':'name'})
            blogers = [bloger.find('a').string for bloger in bloger_tag]
            
            # get link
            targetlinks = soup.findAll('cite')
            links = [link.find('a') for link in targetlinks]
            
            for j, link in enumerate(links):
                if ('href' in dict(link.attrs)):
                    url=urljoin(page,link['href'])
                    if url.find("'")!=-1: continue
                    url=url.split('#')[0] # フラグメント識別子を取り除く
                    if url[0:4]=='http' and not self.isindexed(url):
                        self.crawl(url, blogers[j], gender, depth=1)

    # URLが既にインデックスされていたらtureを返す
    def isindexed(self,url):
        u=self.con.execute \
            ("select url from blog_master where url='%s'" % url).fetchone()
        if u!=None: return True
        return False   
       
    def create_tables(self):
        """ データベースのテーブルを作る """
        tnlist = ['blog_master','male_words', 'female_words', 'male_score']
        for table_name in tnlist:
            sql="SELECT name FROM sqlite_master WHERE type='table' AND name='MYTABLE';" \
                    .replace('MYTABLE', table_name)
            res = self.con.execute(sql).fetchone()
            if res is not None: # tableの存在確認
                self.con.execute('drop table %s' % (table_name))

        self.con.execute('create table blog_master(bloger, gender, url, article, wordlist, create_time)')
        self.con.execute('create table male_words(word, word_cnt)')
        self.con.execute('create table female_words(word, word_cnt)')
        self.con.execute('create table male_score(word, male_score)')
        
        self.con.execute('create index urlidx on blog_master(url)')
        self.con.execute('create index male_wordsidx on male_words(word)')
        self.con.execute('create index female_wordsidx on female_words(word)')
        self.con.execute('create index wordidx on male_score(word)')

        self.dbcommit()

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
    dbname='amebablog.db' # test.db
    cdb = CreateDB(dbname,use=1)
    cdb.search_ameblo_top50()