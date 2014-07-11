# coding: utf-8

"""
全ての銘柄のシミュレーション
使い方： python bin/simulate.py setting_file_name

1銘柄のシミュレーション
使い方： python bin/simulate.py setting_file_name stock_code
"""

import json
import sys, os
sys.path.append(os.getcwd()+'/../lib')
sys.path.append(os.getcwd()+'/../settings')
sys.path.append(os.getcwd()+'/../lib/indicator')

from simulation import Simulation
from trading_system import TradingSystem
from recorder import Recorder
from data_to_stock import DataToStock

from estrangement_settings import get_params

class CustomSimulation(Simulation): #Custom
    def __init__(self, code=None):
        self.code = code
        self.record_every_stock = False
        
    def setting(self, params, fname=None):
        """複数の株だけど、いくつかの株に絞ってシミュレーションする場合は
        _fnameにファイル名を指定
        """
        if 'from' in params:
            self.set_date_from(params['from'])
        if 'to' in params:
            self.set_date_to(params['to'])
        print 'from:', self.date_from
        print 'to:', self.date_to
        if self.code is not None:
            self.simulate_a_stock(self.code) # privateメソッドのため、親クラスのメソッドを直接呼び出す
        else:
            self.simulate_all_stocks(fname)
    
    def set_trading_system(self, params):
        self.trading_system = TradingSystem(params)
        
    def set_date_from(self, date):
        self.date_from = date
        
    def set_date_to(self, date):
        self.date_to = date
        
    def set_data_loader(self, data_loader):
        Simulation.data_loader = data_loader
        
    def set_record_dir(self, record_dir, setting_file_name, system_name, version):
        self.recorder = \
            Recorder(os.path.join(record_dir,system_name,version))
        self.recorder.create_record_folder()
        self.recorder.record_setting(setting_file_name)
        
    def set_record_every_stock(self, true_or_false):
        self.record_every_stock = true_or_false
    
class CustomTradingSystem(TradingSystem):
    def entry(self, rule, params=None):
        self._create_rule(self.entries, rule, params)
        
    def exit(self, rule, params=None):
        self._create_rule(self.exits, rule, params)
        
    def filter(self, rule, params=None):
        self._create_rule(self.filters, rule, params)
        
    def _create_rule(self, rules, rule, params=None):
        if rules is None:
            rules = []
        new_rule = rule(params) if params is not None else rule()
        rules.append(new_rule)
        
        
if __name__=='__main__':
    setting_f_name = os.getcwd()+'/../settings/estrangement_settings.py'
    settings = get_params()

    data_dir = os.getcwd()+'/../data/'
    dbname = 'daily_stock_data.db'

    record_dir = os.getcwd()+'/../check/result'

    sim_params = settings['simulation']
    if 'code' in sim_params or sim_params['code'] is not None:
        sim = CustomSimulation(sim_params['code'])
    else:
        sim = CustomSimulation()
    
    # set stock data
    data = DataToStock(data_dir, dbname)
    sim.set_data_loader(data)

    # set trading system
    t_sys_params = settings['trading_system']['params']
    sim.set_trading_system(t_sys_params)

    # set recorder
    sim.set_record_dir(record_dir,
                       setting_f_name,sim_params['system_name'],
                       sim_params['version'])
    sim.set_record_every_stock(sim_params['every_rec']) # 全て記録するか
    
    # setting simulator
    sim.setting(sim_params['params'],
                settings['trading_system']['stock_list'])