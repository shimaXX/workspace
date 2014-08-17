# coding: utf-8

from xlrd import open_workbook, XL_CELL_TEXT, cellname
import re
from datetime import datetime

wtdlist = ('月', '火', '水', '木', '金', '土', '日')

wb = open_workbook('vr_bscs_attribution.xls') #'vr_bscs_blocks.xls'
#wb = open_workbook('test.xls')
outfile = open('bscs_rate_attribution', 'w', 1000)

for s in wb.sheets():
    print 'Sheet:',s.name
    channel = s.cell(0,0).value
    # date -> 2014-02-01
    ymd = s.cell(0,26).value
    s_date, others = ymd.strip().split('（')
    tdatetime = datetime.strptime(s_date, '%Y年%m月%d日')
    
    # get week day
    wtd = wtdlist[tdatetime.weekday()]
    
    # get tuned date
    ymd = tdatetime.strftime('%Y-%m-%d')
    
    region = u'関東'
     
    for row in xrange(4,s.nrows):
        if s.cell(row,1).value==u'': continue
        
        start_time = ''
        minute = ''
        region = ''
        title = ''
        rate = ''
        
        values = []
#        for col in range(s.ncols):
#        if s.cell(1,col).value==u'放送開始':
        start_time = unicode( int(s.cell(row,1).value) )
        start_time = start_time if len(start_time)==4 else '0'+start_time
        start_time = start_time[:2]+':'+start_time[2:]
#        if s.cell(1,col).value==u'放送分数':
        minute = unicode( int(s.cell(row,2).value) )
#        if s.cell(1,col).value==u'番 組 名':
        title = s.cell(row,3).value
        
        house_rate = unicode(s.cell(row,4).value)
        indiv_rate = unicode(s.cell(row,5).value)
        fm_4to12_rate = unicode(s.cell(row,6).value)
        fm_13to19_rate = unicode(s.cell(row,7).value)
        m_20to34_rate = unicode(s.cell(row,9).value)
        m_35to49_rate = unicode(s.cell(row,10).value)
        m_over50_rate = unicode(s.cell(row,11).value)
        f_20to34_rate = unicode(s.cell(row,21).value)
        f_35to49_rate = unicode(s.cell(row,22).value)
        f_over50_rate = unicode(s.cell(row,23).value)
        
        values = [u'関東', ymd, wtd, title, channel, start_time, minute, 
                  house_rate, indiv_rate, fm_4to12_rate, fm_13to19_rate,
                  m_20to34_rate, m_35to49_rate, m_over50_rate,
                  f_20to34_rate, f_35to49_rate, f_over50_rate]
        str = u','.join(values)
        print str
        outfile.write(str+'\n')