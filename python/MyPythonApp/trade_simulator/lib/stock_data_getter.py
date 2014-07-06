# coding: utf-8

from datetime import datetime
import jsm
import sqlite3 as sqlite
import os

class StockDataGetter:
    data_dir = os.getcwd()+'/../data/'
       
    def __init__(self, dbname, brand_info_db):
        dbpath = self.data_dir+dbname
        self.con = sqlite.connect( dbpath )
        self.con.text_factory = str
        if not self.isexist('price_master'):
            self.createtables()
        self.brand_info_db = brand_info_db

    def __del__(self):
        self.con.close()
        
    def dbcommit(self):
        self.con.commit()
    
    def get_price_data(self,code):
        """ get new stack price data """
        table_name = 'price_master'

        q = jsm.Quotes()
        if self.isindexed(code):
            print 'Ticker symbol:'+ str(code) + ' is ' + "updating data..."
            try:
                self.update_price_data(q, code)
                self.brand_info_db.execute("update brand_info_master set enable=1 where code=%s" % code)
            except Exception, e:
                print "error:",e
                self.get_histrical_data(q, code)
        else: 
            self.get_histrical_data(q, code)
        print "processing is complete\n"
    
    def update_price_data(self, q, code):
        db_laste_date = self.get_latest_date(code)
        start_date = datetime.strptime(db_laste_date, '%Y-%m-%d')
        end_date = datetime.today()
        
        print "start date:",datetime.date(start_date)
        print "end date:",datetime.date(end_date)
        if datetime.date(start_date)!=datetime.date(end_date):
            prices_list = q.get_historical_prices(code, jsm.DAILY, start_date, end_date)
            self.addtoindex_prices(code, prices_list)
            self.update_finace_data(code, q.get_finance(code))
        
    def get_histrical_data(self, q, code):
        print 'Ticker symbol:'+ str(code) + ' is ' + "getting data at first time..."
        print "crawling yahoo finance(to have many time)..."            
        try:
            prices_list = q.get_historical_prices(code, jsm.DAILY, all=True)
            self.addtoindex_prices(code, prices_list)
            self.addtoindex_finance(code, q.get_finance(code))
            self.brand_info_db.execute("update brand_info_master set enable=1 where code=%s" % code)
        except Exception, e:
            print "error:", e
            self.brand_info_db.execute("update brand_info_master set enable=0 where code=%s" % code)
    
    def get_latest_date(self, code):
        res = self.con.execute("select date from price_master where code='%s' \
                                order by date DESC limit 1" % code ).fetchone()[0]
        return res
        
    def addtoindex_prices(self, code, prices_list):
        """ store price data to db """
        for prices in prices_list:            
            date = prices.date.strftime('%Y-%m-%d')
            print "indexing",date
            
            if self.isindexed(code,date): break
            else: 
                # close value of jsm is already adjusted
                self.con.execute( "insert into price_master values(?,?,?,?,?,?,?)", \
                                  (code, date, prices.open, prices.high, prices.low, \
                                   prices.close, prices.volume) )
        self.dbcommit()
    
    def addtoindex_finance(self, code, fnc_data):
        self.con.execute( "insert into finance_master values(?,?,?,?,?,?,?,?,?,?,?,?,?)", \
                (code, \
                 fnc_data.market_cap, fnc_data.shares_issued,fnc_data.dividend_yield, \
                 fnc_data.dividend_one, fnc_data.per, fnc_data.pbr, fnc_data.eps, \
                 fnc_data.bps, fnc_data.price_min, fnc_data.round_lot, \
                 fnc_data.years_high, fnc_data.years_low))
        self.dbcommit()
    
    def isindexed(self, code, date=None):
        if date is not None:
            u = self.con.execute \
                ("select date from price_master where code='%s' and date='%s'" % \
                  (code, date)).fetchone()
        else:
            u = self.con.execute \
                ("select date from price_master where code='%s'" % code).fetchone()
        if u!=None: return True
        else: return False
    
    def update_finace_data(self, code, fnc_data):
        self.con.execute("update finance_master set market_cap=%s, shares_issued=%s, \
                dividend_yield=%s, dividend_one=%s, per=%s, pbr=%s, eps=%s, \
                bps=%s, price_min=%s, round_lot=%s, years_high=%s, years_low=%s \
                where code='%s'" % \
                (fnc_data.market_cap, fnc_data.shares_issued,fnc_data.dividend_yield, \
                 fnc_data.dividend_one, fnc_data.per, fnc_data.pbr, fnc_data.eps, \
                 fnc_data.bps, fnc_data.price_min, fnc_data.round_lot, \
                 fnc_data.years_high, fnc_data.years_low, code))
        self.dbcommit()
    
    def createtables(self):
        tnlist = ['price_master' ,'finance_master']

        for table_name in tnlist:
            if self.isexist(table_name): #tableの存在確認
                self.con.execute('drop table %s' % (table_name))

        self.con.execute('create table price_master(code, date, open, high, low, close, volume)')
        self.con.execute('create table finance_master( \
                code, market_cap, shares_issued,dividend_yield,dividend_one, \
                per,pbr,eps,bps,price_min,round_lot,years_high,years_low)')
        # 時価総額, 発行済株式数,配当利回り,1株配当,株価収益率,純資産倍率,1株利益,
        # 1株純資産,最低購入代金,単元株数,年初来高値,年初来安値

        self.con.execute('create index dateidx on price_master(date)')
        self.dbcommit()
        
    def isexist(self, table_name):
        sql="SELECT name FROM sqlite_master WHERE type='table' AND name='MYTABLE';" \
                .replace('MYTABLE', table_name)
        res = self.con.execute(sql).fetchone()
        if res is not None: return True
        else: return False
        
if __name__=='__main__':
    branddbname = os.getcwd()+'/../data/brand_info.db'
    brand_info_db = sqlite.connect(branddbname)
    sdg = StockDataGetter('daily_stock_data.db', brand_info_db)
    
    brands_info =  brand_info_db.execute("select code, market from brand_info_master where enable=1")
    
    while 1:
        res = brands_info.fetchone()
        if res is None: break
        sdg.get_price_data(res[0]) # code
        brand_info_db.commit()