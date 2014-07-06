# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../lib')
sys.path.append(os.getcwd()+'/../lib/rule')
sys.path.append(os.getcwd()+'/../lib/rule/entry')
sys.path.append(os.getcwd()+'/../lib/rule/exit')
sys.path.append(os.getcwd()+'/../lib/rule/stop')
sys.path.append(os.getcwd()+'/../lib/rule/filter')
sys.path.append(os.getcwd()+'/../lib/indicator')

import sqlite3 as sqlite

from trading_system import TradingSystem
from data_to_stock import DataToStock
from estrangement_entry import EstrangementEntry
from estrangement_exit import EstrangementExit
from stop_out_exit import StopOutExit
from average_true_range_stop import AverageTrueRangeStop
from moving_average_direction_filter import MovingAverageDirectionFilter
from recorder import Recorder


data_dir = os.getcwd()+'/../data/'
dbname = 'daily_stock_data.db'
data = DataToStock(data_dir, dbname, '2010-01-01', '2011-08-31')
trading_system = TradingSystem({'entries':EstrangementEntry({'span':20, 'rate':5}),
                                'exits':[StopOutExit(), EstrangementExit({'span':20, 'rate':3.5})], # stop_out_exitは最後につける(損切りの手仕舞いだから)
                                'stops':AverageTrueRangeStop({'span':20}),
                                'filters':MovingAverageDirectionFilter({'span':30})
                                })

def simulate(code):
    stock = data.generate_stock(code)
    trading_system.set_stock(stock)
    trading_system.calculate_indicators()
    trade = None
    trades = []
    
    print "prices len",len(stock.prices)
    for i in xrange(len(stock.prices)): # 時系列データの数分だけ回す
        # check entry
        if trade is not None:
            trading_system.set_stop(trade, i)
            trade.length += 1
        else:
            trade = trading_system.check_entry(i)
            if trade is not None:
                trade.volume = stock.unit
                print "trade",trade
                print "entry",trade.entry_date
                print "entry_price",trade.entry_price
                print "trade_type", trade.trade_type
                print "volume",trade.volume

        # check exit
        if trade is not None:
            trading_system.check_exit(trade, i)
            if trade.isclosed():
                trades.append(trade)
                print "exit",trade.exit_date
                print "exit_price",trade.exit_price
                trade = None
    return trades


con = sqlite.connect(os.getcwd()+'/../data/daily_stock_data.db')

recorder = Recorder()
recorder.record_dir = 'result/test'
recorder.create_record_folder()
recorder.record_setting(__file__) # 現在実行中のソースファイル名

results = [ simulate(code) for code in (7203,4063, 8604) ] 
results = [trades for trades in results if len(trades)!=0]

for trades in results: recorder.record_a_stock(trades) 
recorder.record_stats_for_each_stock(results)
recorder.record_stats(results)