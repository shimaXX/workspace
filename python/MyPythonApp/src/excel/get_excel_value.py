# coding: utf-8

from xlrd import open_workbook, XL_CELL_TEXT, cellname
import re, codecs
from datetime import datetime

def calculate(ifname, ofname):
    wtdlist = ('月', '火', '水', '木', '金', '土', '日')
    
    wb = open_workbook(ifname) #'vr_bscs_blocks.xls'
    #wb = open_workbook('test.xls')
    outfile = codecs.open(ofname, 'w', 'shift-jis','ignore')
    
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
         
        for row in xrange(4,s.nrows):
            if s.cell(row,1).value==u'': continue
            
            start_time = u''
            minute = u''
            region = u''
            title = u''
            rate = u''
            
            values = []
    #        for col in range(s.ncols):
    #        if s.cell(1,col).value==u'放送開始':
            start_time = unicode( int(s.cell(row,1).value) )
            start_time = start_time if len(start_time)==4 else u'0'+start_time
            start_time = start_time[:2]+u':'+start_time[2:]
    #        if s.cell(1,col).value==u'放送分数':
            minute = unicode( int(s.cell(row,2).value) )
    #        if s.cell(1,col).value==u'番 組 名':
            title = s.cell(row,3).value
            
            for col in xrange(6,9):
                region = s.cell(2,col).value
                region = re.sub(ur'\n',u'',region).strip()
                region = u'関西' if region==u'近畿' else region
                region = u'名古屋' if region==u'中部' else region
                
                rate = unicode(s.cell(row,col).value)
                
                values = [region, ymd, wtd,title, channel,start_time,minute, rate]
                str = u','.join(values)
                print str
                outfile.write(str+u'\n')