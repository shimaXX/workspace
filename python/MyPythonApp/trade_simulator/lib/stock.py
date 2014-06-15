# coding: utf-8

class Stock:
    """ this class make sense just stock """
    prices = []
    price_hash = {}
    
    def __init__(self,code, market, unit):
        self.code = code
        self.market = market
        self.unit = unit # share unit number
    
    def get_data(self, label):
        if label=='date': return self.dates()
        if label=='open': return self.open_prices()
        if label=='high': return self.high_prices()
        if label=='low': return self.low_prices()
        if label=='close': return self.close_prices()
        if label=='volume': return self.volume()
    
    def dates(self):
        self._get_dates()
        return self.price_hash['date']
        
    def open_prices(self):
        self._get_open_prices()
        return self.price_hash['open']

    def high_prices(self):
        self._get_high_prices()
        return self.price_hash['high']

    def low_prices(self):
        self._get_low_prices()
        return self.price_hash['low']

    def close_prices(self):
        self._get_close_prices()
        return self.price_hash['close']

    def volume(self):
        self._get_volume()
        return self.price_hash['volume'] 
    
    def add_price(self, (code,date, _open, high, low, close, volume,)):
        """ add one day stack value """
        value_dict = {'date':date, 'open':_open, 'high':high, 'low':low,
                      'close':close, 'volume':volume}
        self.prices.append(value_dict)
    
    def _get_dates(self):
        self._map_prices('date')

    def _get_open_prices(self):
        self._map_prices('open')

    def _get_high_prices(self):
        self._map_prices('high')

    def _get_low_prices(self):
        self._map_prices('low')

    def _get_close_prices(self):
        self._map_prices('close')

    def _get_volumes(self):
        self._map_prices('volume')
    
    def _map_prices(self, price_name):
        if price_name not in self.price_hash:
            self.price_hash[price_name] = \
                            map((lambda x: x[price_name]),self.prices)
        
if __name__=='__main__':
    stock = Stock(8604, 't', 100)
    
    stock.add_price(("2011-07-01", 402, 402,395,397,17495700,))
    stock.add_price(("2011-07-04", 402, 404,400,403,18819300))
    stock.add_price(("2011-07-05", 402, 408,399,401,20678000))

    print stock.prices[0]['date']
    print stock.prices[1]['open']
    print stock.prices[2]['high']
    stock.get_dates()
    stock.get_open_prices()
    print stock.price_hash['open']
    print stock.price_hash['date']