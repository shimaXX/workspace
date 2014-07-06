# coding: utf-8

import shutil, os, sys
import inspect

from trade import Trade
from stats import Stats


class Recorder:
    def __init__(self, record_dir=None):
        self.record_dir = record_dir
        
    def record_a_stock(self, trades):
        """1銘柄の取引を記録する"""
        code = trades[0].stock_code
        file_name = self.record_dir+'/'+str(code)+'.csv'
        with open(file_name, 'w') as f:
            s = ','.join( self._items_for_a_stock().values() )
            f.write(s+'\n')
            for trade in trades:
                one_trade = []
                for attr in self._items_for_a_stock():
                    if inspect.ismethod(getattr(trade, attr)):
                        tmp = str( getattr(trade, attr)() ) if getattr(trade, attr)() is not None else '-'
                        one_trade.append(tmp)
                    else:
                        tmp = str( getattr(trade, attr) ) if getattr(trade, attr) is not None else '-'
                        one_trade.append(tmp)
                s = ','.join(one_trade)
                f.write(s+'\n')
            
    def record_stats_for_each_stock(self, results):
        """銘柄ごとの統計の一覧表の作成"""
        file_name = self.record_dir+'/_stats_for_each_stock.csv'
        with open(file_name, 'w') as f:
            values = self._stats_items().values()
            values.insert(0, 'コード')
            s = ','.join(values)
            f.write(s+'\n')
            if len(results)==0: return
            for trades in results:
                result = self.stats_array(trades)
                result.insert(0, str(trades[0].stock_code))
                f.write(','.join(result)+'\n')
            
    def record_stats(self, results):
        """すべてのトレードの統計"""
        file_name = self.record_dir+'/_stats.csv'
        with open(file_name, 'w') as f:
            s = ','.join( self._stats_items().values() )
            f.write(s+'\n')
            trades = [ results[i][j] for i in xrange(len(results)) for j in xrange(len(results[i]))]
            s = ','.join( self.stats_array(trades) )
            f.write(s+'\n')
            
    def record_setting(self, file_name):
        """設定ファイルをコピーする"""
        shutil.copyfile(file_name, self.record_dir+'/_setting.py')
        
    def create_record_folder(self):
        if not os.path.exists(self.record_dir):
            os.makedirs(self.record_dir)
    
    def _items_for_a_stock(self):
        return {'trade_type': '取引種別',
                'entry_date': '入日付',
                'entry_price': '入値',
                'volume': '数量',
                'first_stop': '初期ストップ',
                'exit_date': '出日付',
                'exit_price': '出値',
                'profit': '損益（円）',
                'r_multiple': 'R倍数',
                'percentage_result': '%損益',
                'length': '期間'
                }
        
    def _stats_items(self):
        return {'sum_profit':'純損益',
                'wins':'勝ち数', 'losses':'負け数',
                'draws':'分け数',
                'winning_rate':'勝率',
                'average_profit':'平均損益',
                'profit_factor':'PF',
                'sum_r':'総R倍数', 'average_r':'平均R倍数',
                'sum_percentage':'純損益率',
                'average_percentage':'平均損益率',
                'average_length':'平均期間'
                }
        
    def stats_array(self, trades):
        stats = Stats(trades)
        return [str( getattr(stats, stats_name)() ) if getattr(stats, stats_name)() is not None else '-' \
            for stats_name in self._stats_items().keys()]