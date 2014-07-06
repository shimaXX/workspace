# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../lib/rule/')
sys.path.append(os.getcwd()+'/../lib/rule/entry')
sys.path.append(os.getcwd()+'/../lib/rule/exit')
sys.path.append(os.getcwd()+'/../lib/rule/filter')
sys.path.append(os.getcwd()+'/../lib/rule/stop')

from estrangement_entry import EstrangementEntry
from stop_out_exit import StopOutExit
from estrangement_exit import EstrangementExit
from average_true_range_stop import AverageTrueRangeStop
from moving_average_direction_filter import MovingAverageDirectionFilter

def get_params():
	"""
	_バージョン管理について
	_1) 日付の範囲や銘柄リスト、取引市場など、データ周りの設定変更があった場合：一番右の桁を増やす
	_2) ルールのパラメタを変更した場合：真ん中の桁のを増やす
	_3) ルールの数や種類を変更した場合（フィルータを増やした、exitルールを取り替えた）：左の桁を増やす
	"""
	return \
	{	"simulation":
		{
			"system_name":"estrangement",	
			"version":"0.0.0",
			"params":{
				"from":"2010-10-01",
				"to":"2012-12-28"
			},
			"code": None,
			"every_rec":True
		},
		"trading_system":
		{
			"params":
			{"entries":EstrangementEntry({"span":20, "rate":5}), 
			"exits":[StopOutExit(),EstrangementExit({"span":20, "rate":3})],
			"stops":AverageTrueRangeStop({"span":20, "ration":1}),
			"filters":MovingAverageDirectionFilter({"span":40})
			},
			"stock_list":os.getcwd()+'/../data/test_stock.csv'
		}
	}