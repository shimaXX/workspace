# coding: utf-8

from trading_system import TradingSystem
from recorder import Recorder

class Simulation:
    data_loader = None
    recorder = None
    date_from = None
    date_to = None
    
    def __init__(self, params={}):
        self.trading_system = params['trading_system'] if 'trading_system' in params else None
        self.data_loader = params['data_loader'] if 'data_loader' in params else None
        self.recorder = params['recorder'] if 'recorder' in params else None
        self.date_from = params['from'] if 'from' in params else None
        self.date_to = params['to'] if 'to' in params else None
        if 'record_every_stock' in params:
            self.record_every_stock = \
                False if params['record_every_stock']==False else True
        else: self.record_every_stock = True
        
    def simulate_a_stock(self, code):
        """1銘柄のシミュレーション"""
        self._set_dates_to_data_loader()
        stock = self.data_loader.generate_stock(code)
        self.simulate(stock)
        if len(self.trades)!=0:
            self.recorder.record_a_stock(self.trades)
            
    def simulate_all_stocks(self, filename=None):
        """すべての銘柄のシミュレーションを行う"""
        results=[]
        self._set_dates_to_data_loader()
        for stock in self.data_loader.each_stock(filename):
            self.simulate(stock)
            print 'calculating',stock.code
            if len(self.trades)==0: continue
            if self.record_every_stock:
                self.recorder.record_a_stock(self.trades)
            results.append(self.trades)
            self.recorder.record_stats_for_each_stock(results)
            self.recorder.record_stats(results)
            
    def _set_dates_to_data_loader(self):
        self.data_loader.date_from = self.date_from
        self.data_loader.date_to = self.date_to
        
    def simulate(self, stock):
        self.trading_system.set_stock(stock)
        self.trading_system.calculate_indicators()
        self.trades = []
        self.position = None
        self.unit = stock.unit        
        for index in xrange(len(stock.prices)):
            self.index = index
            self.before_open()
            self.at_open()
            self.in_session()
            self.at_close()
    
    def before_open(self):
        self.signal = None
        if self.position is None: return
        self.position.exit_date = None
        self.position.exit_price = None
        self.trading_system.set_stop(self.position, self.index)
        self.position.length += 1
        
    def at_open(self):
        self.take_position('open')
        self.close_position('open')
    
    def in_session(self):
        self.take_position('in_session')
        self.close_position('in_session')
        
    def at_close(self):
        self.take_position('close')
        self.close_position('close')
        
    def take_position(self, entry_time):
        if self.position is not None: return
        if self.signal is None:
            self.signal = self.trading_system.check_entry(self.index)
        if self.signal is None: return
        if self.signal.entry_time==entry_time:
            self.position = self.signal
            self.position.volume = self.unit
            self.signal = None
    
    def close_position(self, exit_time):
        if self.position is None: return None
        if not self.position.isclosed():
            self.trading_system.check_exit(self.position, self.index)
        if not self.position.isclosed(): return # 手仕舞いされていればデータを格納
        if self.position.exit_time==exit_time:
            self.trades.append(self.position) # position=trade instance
            self.position = None