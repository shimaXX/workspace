# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../lib/')
sys.path.append(os.getcwd()+'/../lib/rule/')
sys.path.append(os.getcwd()+'/../lib/rule/entry/')
sys.path.append(os.getcwd()+'/../lib/rule/exit/')
sys.path.append(os.getcwd()+'/../lib/rule/filter/')
sys.path.append(os.getcwd()+'/../lib/rule/stop/')
from pprint import pprint as p
#p(sys.path)
from stock import Stock
import rule, entry, exit, filter, stop
from tick import Tick

class MyEntry(entry.Entry):
    def check_long(self, index):
        if (index % 2)==0:
            return self.enter_long(index, 100, 'close')
    def check_short(self,index):
        if (index % 2)==1:
            return self.enter_short(index, 100, 'short')

class MyExit(exit.Exit):
    def check_long(self,trade,index):
        if (index % 2)==1:
            self._exit(trade, index, 105, 'close')
    def check_short(self, trade, index):
        if (index % 2)==0:
            self._exit(trade, index, 95, 'close')
        
class MyStop(stop.Stop):
    def stop_price_long(self,position,index):
        return Tick.down(position.entry_price, 5)
    def stop_price_short(self, position, index):
        return Tick.up(position.entry_price, 5)
        
class MyFilter(filter.Filter):
    def filter(self,index):
        rest = index % 4
        if rest==0:
            return 'long_only'
        elif rest==1:
            return 'short_only'
        elif rest==2:
            return 'no_entry'
        elif rest==3:
            return 'long_and_short'
        
if __name__=='__main__':
    _stock = Stock(1301, 't', 100) 
    entry = MyEntry()
    entry.stock = _stock
    p( entry.check_long_entry(0) )
    p( entry.check_long_entry(1) )
    print
    p(entry.check_short_entry(0))
    p(entry.check_short_entry(1))

    print 
    my_exit = MyExit()
    my_exit.stock = _stock
    trade1 = entry.check_long(0)
    my_exit.check_exit(trade1,1)
    p( trade1.entry_price )
    p( trade1.exit_price )
    print
    
    stop = MyStop()
    trade3 = entry.check_long(0)
    print stop.get_stop(trade3, 0)
    trade4 = entry.check_short(1)
    print stop.get_stop(trade4, 1)
    print 
    
    filter = MyFilter()
    print filter.get_filter(0)
    print filter.get_filter(1)
    print filter.get_filter(2)
    print filter.get_filter(3)