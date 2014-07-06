# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../lib/')
sys.path.append(os.getcwd()+'/../lib/indicator')
sys.path.append(os.getcwd()+'/../lib/rule/entry')
sys.path.append(os.getcwd()+'/../lib/rule/')
from data_to_stock import DataToStock
from estrangement_entry import EstrangementEntry

data_dir = os.getcwd()+'/../data/'
dbname = 'daily_stock_data.db'
tts = DataToStock(data_dir, dbname, '2014-01-01', '2014-02-01')

stock = tts.generate_stock(8604)
print stock.open_prices()

est_entry = EstrangementEntry({'span':10, 'rate':5})
est_entry.stock = stock
est_entry.calculate_indicators()

real_signals = [float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),'flat','flat','flat','flat','flat','long','flat','flat','flat','flat']

for i,real_signal in enumerate(real_signals):
    trade = est_entry.check_long_entry(i+1) if est_entry.check_long_entry(i+1) is not None \
                else est_entry.check_short_entry(i+1)
    signal = trade.trade_type if trade is not None else float('nan')
    print signal, real_signal
    if real_signal is not signal:
        print 'fail in data %d' % i
        
print est_entry.check_long_entry(15)
print est_entry.check_short_entry(14)