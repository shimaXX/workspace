# coding: utf-8

import sys, os
sys.path.append(os.getcwd())
import sqlite3 as sqlite

from stock import Stock

class DataToStock:
    def __init__(self, data_dir, dbname, date_from=None, date_to=None):
        self.data_dir = data_dir
        self.stocks ={}
        self.date_from = date_from
        self.date_to = date_to
        self.dbname = dbname
        
    def dbclose(self):
        self.con.close()
        
    def generate_stock(self, code):
        dbpath = self.data_dir+'/'+self.dbname
        # check file exist
        if os.path.exists(dbpath):
            self.con = sqlite.connect(dbpath)
            
            # check data exist
            if self.isavailable(code):
                _stock = Stock(code, 't', self.get_unit_nunber(code))
                self.add_price_data_from_db(_stock,code)
            self.dbclose()
        return _stock
    
    def isavailable(self, code):
        res = self.con.execute("select date from price_master where code='%s' limit 1" % \
                               code).fetchone()
        if res is not None: return True
        else: return False
    
    def get_unit_nunber(self, code):
        return self.con.execute("select round_lot from finance_master where code='%s'" % \
                                code ).fetchone()[0]
    
    def add_price_data_from_db(self, _stock, code):
        prices_list = self.get_prices_list(code)
        while 1:
            prices = prices_list.fetchone()
            if prices is None: break
            _stock.add_price(prices)
            _stock.prices.sort(key=lambda x:(x['date']))

    def get_prices_list(self, code):        
        if self.date_from is not None and self.date_to is not None:
            prices_list = self.con.execute("select * from price_master \
                        where date>='%s' and date<='%s' and code='%s'" % 
                        (self.date_from, self.date_to, code))
        elif self.date_from is not None and self.date_to is None:
            prices_list = self.con.execute("select * from price_master \
                        where date>='%s' and code='%s'" % (self.date_from, code))
        elif self.date_from is None and self.date_to is not None:
            prices_list = self.con.execute("select * from price_master \
                        where date<='%s' and code='%s'" % (self.date_to, code))            
        else:
            prices_list = self.con.execute("select * from price_master \
                            where code='%s'" % code)
        return prices_list
            
    def each_stock(self, filename=None):
        if filename is not None:
            print '===selected sebral stocks==='
            with open(filename, 'r') as f:
                for line in f:
                    data = line.strip().split(',')
                    print 'generate stock:', data[1]
                    self.stocks[data[1]] = self.generate_stock(int(data[1]))
            return self.stocks.values()
        else:
            print '===get every stock==='
            db = sqlite.connect( self.data_dir+'brand_info.db' )
            res = db.execute("select code from brand_info_master where enable=1")
            while 1:
                code = res.fetchone()
                if code is None: break
                print 'generate stock:', code[0]
                self.stocks[str(code[0])] = self.generate_stock(code[0])
            return self.stocks.values()
    
if __name__=='__main__':
    data_dir = os.getcwd()+'/../data'
    f_stock_list = 'tosho_stock_list.csv'
    dts = DataToStock(data_dir, '2005-01-01', '2013-01-01') #'2005-01-01', '2013-01-01'
    dts.date_to = None
    stck = dts.generate_stock(2432)
    print stck.code
    print stck.dates()[-1]
    print stck.dates()[0]
    print stck.open_prices()[0]
    
    dts.each_stock(f_stock_list)
    print dts.stocks