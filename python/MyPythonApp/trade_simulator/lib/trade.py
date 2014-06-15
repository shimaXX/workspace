# coding: utf-8

class Trade:
    first_stop=None
    stop=None
    
    exit_date=None
    exit_price=None
    exit_time=None
    
    def __init__(self, params):
        """ 仕掛ける """
        self.stock_code = params['stock_code']
        self.trade_type = params['trade_type']
        self.entry_date = params['entry_date']
        self.entry_price = params['entry_price']
        self.volume = params['volume'] # 購入株数
        self.entry_time = params['entry_time'] # timeは寄り付き('open')、ザラ場中('in_session')、大引けの3区分('close')
        self.length = 1 # 取引を仕掛けてからの日数
        
    def exit(self, params):
        """ 手仕舞う
        _仕掛けた株数と同数を手仕舞うため、株数は含まない 
        """
        self.exit_date = params['exit_date'] if 'exit_date' in params else params['date']
        self.exit_price = params['exit_price'] if 'exit_price' in params else params['price']
        self.exit_time = params['exit_time'] if 'exit_time' in params else params['time']
        
    def isclosed(self):
        """ whether closed trade """
        if self.exit_date is not None and self.exit_price is not None: return True
        else: return False
        
    def islong(self):
        """ whether buying trade """
        return self.trade_type=='long'
    
    def isshort(self):
        """ whether selling trade """
        return self.trade_type=='short'
    
    def profit(self):
        """ profit and loss value """
        return self.plain_result()*self.volume
    
    def percentage_result(self):
        """ percentage profit and loss value """
        return float(self.plain_result())/self.entry_price*100
        
    def r_value(self):
        """ calculate R value """
        if self.trade_type == 'long':
            return self.entry_price - self.first_stop
        elif self.trade_type == 'short':
            return self.first_stop - self.entry_price
    
    def r_multiple(self):
        """ calcurate R multipe value """
        if self.first_stop is None: return None
        if self.r_value()==0: return None
        if float(self.r_value()) != 0:
            return float(self.plain_result()) / float(self.r_value())
        
    def plain_result(self):
        """  profit and loss value do not multiple number of stocks """
        if self.trade_type == 'long':
            return self.exit_price - self.entry_price
        elif self.trade_type == 'short':
            return self.entry_price - self.exit_price
        
if __name__=='__main__':
    params = {'stock_code':1301, 'trade_type':'long', 'entry_date': '2011-11-14',
              'entry_price':251, 'entry_time':'open', 'volume':100}
    trade = Trade(params)
    
    print trade.stock_code
    print trade.entry_date
    print trade.entry_price
    print trade.islong()
    print trade.isshort()
    print trade.isclosed()
    
    trade.first_stop = 241
    trade.stop = 241
    trade.length = 1
    
    print trade.first_stop
    print trade.stop
    print trade.r_value()
    print trade.length
    
    trade.length+=1
    print trade.length
    
    exit_params = {'date':'2011-11-15', 'price':255, 'time':'in_session'}
    trade.exit(exit_params)
    
    print trade.isclosed()
    print trade.exit_date
    print trade.profit()
    print trade.percentage_result()
    print trade.r_multiple()