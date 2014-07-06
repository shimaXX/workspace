# coding: utf-8

from itertools import chain
import numpy as np

class TradingSystem:
    """トレーディングシステムの各ルールの管理をするクラス"""
    def __init__(self, rules={}):
        self.entries = np.array([rules['entries']]).flatten().tolist()
        self.exits = np.array([rules['exits']]).flatten().tolist()
        self.stops = np.array([rules['stops']]).flatten().tolist()
        self.filters = np.array([rules['filters']]).flatten().tolist()
        
    def set_stock(self,stock):
        for rule in self._each_rules():
            rule.stock = stock
            
    def calculate_indicators(self):
        for rule in self._each_rules():
            try:
                rule.calculate_indicators()
            except Exception, e:
                import sys,traceback
                info = sys.exc_info()
                tbinfo = traceback.format_tb( info[2] )
                for tbi in tbinfo: print tbi
                print '  %s' % str( info[1] )
        
    def check_entry(self, index):
        """フィルターを適用して仕掛をテェックする"""
        trade = self.entry_through_filter(index)
        if trade is None: return None
        return self.trade_with_first_stop(trade, index)
    
    def set_stop(self, position, index):
        """ストップを設定する"""
        position.stop = self.tightest_stop(position, index)

    def check_exit(self, trade, index):
        """各種手仕舞いルールを順にチェックし、
        _最初に手仕舞いが発生した時点で手仕舞う
        _中には、手仕舞いを制限するルールもある
        """
        for exit_rule in self.exits:
            exit_filter = exit_rule.check_exit(trade, index)
            if exit_filter=='no_exit': return
            if trade.isclosed(): return
    
    def _each_rules(self):
        for rule in list(chain.from_iterable([self.entries, self.exits, self.stops, self.filters])):
            yield rule
            
    def entry_through_filter(self, index):
        signal = self.filter_signal(index)
        if signal=='no_entry': return None
        elif signal=='long_and_short':
            return self.check_long_entry(index) if self.check_long_entry(index) is not None else self.check_short_entry(index)
        elif signal=='long_only': return self.check_long_entry(index)
        elif signal=='short_only':
            return self.check_short_entry(index)
        
    def filter_signal(self, index):
        """全てのフィルターをチェックして、仕掛られる条件を絞る"""
        filters = [ filter.get_filter(index) for filter in self.filters]
        if None in filters or \
            'no_entry' in filters or ('long_only' in filters and 'short_only' in filters):
            return 'no_entry'
        elif 'long_only' in filters:
            return 'long_only'
        elif 'short_only' in filters:
            return 'short_only'
        else:
            return 'long_and_short'
    
    def check_long_entry(self, index):
        """各仕掛ルールを順にチェックし、
        _最初に買い仕掛が生じた時点で新規買いトレードを返す
        _仕掛がなければNoneを返す
        """
        return self.check_entry_rule('long', index)
        
    def check_short_entry(self, index):
        """各仕掛ルールを順にチェックし、
        _最初に売り仕掛けが生じた時点で新規売りトレードを返す
        _仕掛がなければNoneを返す
        """
        return self.check_entry_rule('short', index)
        
    def check_entry_rule(self, long_short, index):
        for entry in self.entries:
            if long_short=='long': return entry.check_long_entry(index)
            elif long_short=='short': return entry.check_short_entry(index)
        return  None
    
    def tightest_stop(self, position, index):
        """最もきついストップの値段を求める"""
        stops = [position.stop] if position.stop is not None else []
        for stop in self.stops:
            stop_price = stop.get_stop(position, index)
            if not self.isnan(stop_price):
                stops.append(stop_price)
        if position.islong():
            return max(stops)
        elif position.isshort():
            return min(stops)
    
    def isnan(self, value):
        if value != value: return True
        else: return False
    
    def trade_with_first_stop(self, trade, index):
        """仕掛の際の初期ストップを設定する"""
        if self.stops is None or len(self.stops)==0:
            return trade
        stop = self.tightest_stop(trade, index)
        # まだひとつもストップがなければ仕掛ない
        if stop is None: return None
        trade.first_stop = stop
        trade.stop = stop
        return trade