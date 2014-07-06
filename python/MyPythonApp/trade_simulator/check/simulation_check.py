# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../lib')
sys.path.append(os.getcwd()+'/../lib/rule')
sys.path.append(os.getcwd()+'/../lib/rule/entry')
sys.path.append(os.getcwd()+'/../lib/rule/exit')
sys.path.append(os.getcwd()+'/../lib/rule/filter')
sys.path.append(os.getcwd()+'/../lib/rule/stop')
sys.path.append(os.getcwd()+'/../lib/indicator')


from trading_system import TradingSystem
from data_to_stock import DataToStock
from estrangement_entry import EstrangementEntry
from estrangement_exit import EstrangementExit
from stop_out_exit import StopOutExit
from average_true_range_stop import AverageTrueRangeStop
from moving_average_direction_filter import MovingAverageDirectionFilter
from recorder import Recorder
from simulation import Simulation


data_dir = os.getcwd()+'/../data/'
dbname = 'daily_stock_data.db'
data = DataToStock(data_dir, dbname)
estrangement_system = TradingSystem({'entries':EstrangementEntry({'span':20, 'rate':5}),
                                'exits':[StopOutExit(), EstrangementExit({'span':20, 'rate':3.5})], # stop_out_exitは最後につける(損切りの手仕舞いだから)
                                'stops':AverageTrueRangeStop({'span':20}),
                                'filters':MovingAverageDirectionFilter({'span':30})
                                })

recorder = Recorder()
recorder.record_dir = 'result/estrangement/test_simulation'

simulation = \
    Simulation({'trading_system':estrangement_system,
                'data_loader': data,
                'recorder':recorder})
    
recorder.create_record_folder()

#simulation.simulate_a_stock(8604) # code.csv
simulation.simulate_all_stocks(os.getcwd()+'/../data/test_stock.csv') # _stats_for_each_stock.csv