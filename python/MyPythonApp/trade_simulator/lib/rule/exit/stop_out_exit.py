# coding: utf-8

from exit import Exit

class StopOutExit(Exit):
    """ストップアウトクラス
    _価格がストップに掛かったら手じまう
    _ストップに掛かった瞬間、即座に手仕舞う
    _寄り付きで掛かったら寄り付きで、
    _場中に掛かったら場中に手仕舞う
    """
    def calculate_indicators(self):
        pass
    
    def check_long(self, trade, index):
        stop = trade.stop
        price = self.stock.prices[index]
        
        if stop < price['low']: return None
        price, time = (price['open'], 'open') if stop >= price['open'] \
                            else (stop, 'in_session')
        self._exit(trade, index, price, time)
    
    def check_short(self, trade, index):
        stop = trade.stop
        price = self.stock.prices[index]
        if stop > price['high']: return None
        price, time = (price['open'], 'open') if stop <= price['open'] \
                            else (stop, 'in_session')
        self._exit(trade, index, price, time)