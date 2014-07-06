# coding: utf-8

class Indicator:
    def __init__(self, stock):
        self.stock = stock
        
    def each(self):
        for ind in self.indicator:
            yield ind
    
    def get_indicator_value(self,index):
        """ 要素がnanの時は no_value をthrowする """
        if isinstance(index,int) and \
            self.indicator[index] != self.indicator[index] or index <0:
            raise 'no_value'
        else:
            return self.indicator[index]
    
    def calculate(self):
        self.indicator = self.calculate_indicator()
        
    def calculate_indicator(self):
        pass
    
if __name__=='__main__':
    class MyIndicator(Indicator):
        def calculate_indicator(self):
            return [float('nan'),float('nan'),3,5,8,4]
    mi = MyIndicator(None)
    mi.calculate()
    for n in mi.each():
        print n
    
    #try: print mi.get_indicator_value[0]
    #except: pass
    
    for n in xrange(5):
        try: print mi.get_indicator_value(n)
        except: pass
        
    print mi.indicator[0:3]