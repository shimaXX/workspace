# coding: utf-8

import jsm
import sqlite3 as sqlite

class BrandInfoCreator:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)
        self.create_tables()

    def __del__(self):
        self.con.close()
        
    def dbcommit(self):
        self.con.commit()

    def get_brand_info(self, classify_list):    
        q=jsm.Quotes()
        
        print "getting brand info..."
        for classify in classify_list:
            print "classify:",classify
            brands_info = q.get_brand(classify)
            
            for b_info in brands_info:
                self.addtoindex(classify, b_info)
        self.dbcommit()
    
    def addtoindex(self, classify, b_info):
        print b_info
        print "indexing:"+b_info.name+" ..."
        self.con.execute("insert into brand_info_master values(?,?,?,?,?)", \
                         (classify, b_info.ccode, b_info.market, b_info.name, b_info.info))
    
    def create_tables(self):
        tablename = 'brand_info_master'
        if self.isexist(tablename):
            self.con.execute("drop table %s" % tablename)
        self.con.execute("create table brand_info_master(classify, code, market, name, info)")
        self.con.execute("create index marketidx on brand_info_master(market)")
        self.dbcommit()
        
    def isexist(self, tablename):
        sql = "select name from sqlite_master where type='table' and name='MYTABLE';" \
                .replace('MYTABLE', tablename)
        res = self.con.execute(sql).fetchone()
        if res is not None: return True
        else: return False
        
if __name__=='__main__':
    dbname = 'brand_info.db'
    classify_list = ('0050','1050','2050','3050','3100','3150','3200','3250','3300','3350','3400','3450','3500','3550','3600','3650','3700','3750','3800','4050','5050','5100','5150','5200','5250','6050','6100','7050','7100','7150','7200','8050','9050')
    
    bic = BrandInfoCreator(dbname)
    bic.get_brand_info(classify_list)