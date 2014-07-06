# coding: utf-8

from math import floor

class Tick:
    #@statickmethod
    @classmethod
    def size(self,price):
        """ 呼値単位 """
        if price<=3000: return 1
        elif 3000<price<=5000: return 5
        elif 5000<price<=30000: return 10
        elif 30000<price<=50000: return 50
        elif 50000<price<=300000: return 100
        elif 300000<price<=500000: return 500
        elif 500000<price<=3000000: return 1000
        elif 3000000<price<=5000000: return 5000
        elif 5000000<price<=30000000: return 10000
        elif 30000000<price<=50000000: return 50000
        elif 50000000<price: return 100000
    
    @classmethod    
    def ceil(self,price):
        """半端な数を上の呼値に切り上げ
        _半端でなければ何もしない
        """
        tick_size = self.size(price)
        if price % tick_size == 0:
            return price
        else:
            return self.truncate(price) + tick_size
        
    @classmethod
    def truncate(self,price):
        """半端な数を下の呼値に切り下げ
        _半端でなければ何もしない
        """
        return floor( price-(price % self.size(price)) )
    
    @classmethod
    def round(self,price):
        """上か下、どちらか近い法に丸める
        _半端でなければ何もしない
        """
        tick_size = self.size(price)
        if price % tick_size*2>=tick_size:
            return self.ceil(price)
        else:
            return self.truncate(price)
    
    @classmethod
    def up(self, price, tick=1):
        """何ティックか足す
        """
        price+=tick*self.size(price)
        return self.ceil(price)
    
    @classmethod
    def down(self, price, tick=1):
        """何ティックか引く
        """
        price = self.truncate(price)
        price -= tick*self.size(price)
        return price
    
if __name__=='__main__':
    tck = Tick()
    print tck.size(100)
    print tck.size(2999)
    print tck.size(3000)
    print tck.size(3001)
    print tck.size(4000)
    print tck.size(5100)
    print tck.size(300000)
    print tck.size(300500)
    print 
    print tck.truncate(99.99)
    print tck.truncate(30040)
    print tck.truncate(300600)
    print
    print tck.ceil(99.99)
    print tck.ceil(50040)
    print tck.ceil(300600)
    print 
    print tck.round(99.99)
    print tck.round(99.49)
    print tck.round(30040)
    print tck.round(300200)
    print
    print tck.up(100)
    print tck.up(100,3)
    print tck.up(29990,1)
    print tck.up(299900,2)
    print tck.up(30000)
    print
    print tck.down(100)
    print tck.down(100,3)
    print tck.down(30050,1)
    print tck.down(300500,2)
    print tck.down(300000)
    print tck.down(30010)