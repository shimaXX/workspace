# coding: utf-8

import xlwt
import datetime
ezxf = xlwt.easyxf

def write_xls_test(file_name, data_dict, region_list, headline_row, heading_xfs, data_xfs):
    book = xlwt.Workbook(encoding='utf-8')
    
    for region in region_list:
        sheet_name = region+u'_曜日×時間'
        sheet = book.add_sheet(sheet_name)
        
        data = data_dict[region]
        
        # データ取得期間の書き込み
        sheet.write(0, 0, data[0]) #data[span, [live_data], [reach_data]]
        
        # 見出し書き込み
        sheet.write(headline_row[0], 0, u'■リアルタイム（全機器）')
        sheet.write(headline_row[1], 0, u'■タイムシフト（全機器）')
        
        n_colmun = len(data[1][0][0]) # カラム数の読み込み
        n_row = len(data[1][0]) # 列数の読み込み
        
        # 局の書き込み
        for n_station in range(len(data[1])):
            station_name = unicode(data[1][n_station][0][0])
            if n_station==0:
                sheet.write(headline_row[0]+1, 0, station_name)
                sheet.write(headline_row[1]+1, 0, station_name)
            else:
                sheet.write(headline_row[0]+1, n_colmun*n_station+2, station_name)
                sheet.write(headline_row[1]+1, n_colmun*n_station+2, station_name)
        book.save(file_name)
        
        # dataの書き込み
        for type in xrange(1,len(data)): # type = (0:live, 1:reach)
            for n_station in xrange(len(data[type])):
                for row, d_line in enumerate(data[type][n_station]):
                    w_row = row+headline_row[type-1]+2
                    for col, d_col in enumerate(d_line):
                        if n_station==0:
                            w_col = col
                        else:
                            w_col = n_colmun*n_station+2+col
                        if row==0:
                            sheet.write(w_row, w_col, d_col,heading_xfs[col])
                        else:
                            try:
                                value = float(d_col)
                                sheet.write(w_row, w_col, value,data_xfs[col])
                            except:
                                sheet.write(w_row, w_col, d_col,data_xfs[col])
        book.save(file_name)

def write_xls(file_name, sheet_name, headings, data, heading_xf, data_xfs):
    book = xlwt.Workbook()
    sheet = book.add_sheet(sheet_name)
    rowx = 0
    for colx, value in enumerate(headings):
        sheet.write(rowx, colx, value, heading_xf)
    sheet.set_panes_frozen(True) # frozen headings instead of split panes
    sheet.set_horz_split_pos(rowx+1) # in general, freeze after last heading row
    sheet.set_remove_splits(True) # if user does unfreeze, don't leave a split there
    for row in data:
        rowx += 1
        for colx, value in enumerate(row):
            sheet.write(rowx, colx, value, data_xfs[colx])
    book.save(file_name)


def get_data(live_fname, reach_fname):
    live_data = []
    reach_data = []
    span = None
    
    with open(live_fname, 'r', 10000) as f:
        itr = 0
        for line in f:
            if itr==0:
                span=line.strip()
                itr += 1
                continue
            data = line.strip().split(',')
            if len(data[0])==0: continue
            elif data[1]==u'月':
                live_data.append([])
            live_data[len(live_data)-1].append(data)
            
    with open(reach_fname, 'r', 10000) as f:
        itr = 0
        for line in f:
            if itr==0:
                itr += 1 
                continue
            data = line.strip().split(',')
            if len(data[0])==0:continue
            elif data[1]==u'月':
                reach_data.append([])
            reach_data[len(reach_data)-1].append(data)
    return [span, live_data, reach_data]

if __name__ == '__main__':
    region_list = '宮崎 佐賀 山梨 徳島 福井'.split(' ')
    basepath =('./result_live/', './result_timeshift/',)
    f_name_footer = ('(live).csv','(timeshift).csv',)
    f_name_body = u'_曜日×時間平均視聴率'
    headline_row = (2,31,)
    
    output_file = './excel_data/output.xls'

    data_dict = {}
    for region in region_list: 
        fname = region+f_name_body
        live_fname = basepath[0]+fname+f_name_footer[0]
        reach_fname = basepath[1]+fname+f_name_footer[1]
        data = get_data(live_fname, reach_fname)
        
        data_dict[region] = get_data(live_fname, reach_fname)
    
    head_kinds = 'text text text text text text text text'.split(' ')
    kinds =  'text float float float float float float float'.split(' ')
    
    heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
    kind_to_xf_map = {
        'date': ezxf(num_format_str='yyyy-mm-dd'),
        'int': ezxf(num_format_str='#,##0'),
        'money': ezxf('font: italic on; pattern: pattern solid, fore-colour grey25',
            num_format_str='$#,##0.00'),
        #'price': ezxf(num_format_str='#0.000000'),
        'float': ezxf('borders: top thin, bottom thin, left thin, right thin;',
                        num_format_str='#0.0000'),
        'text': ezxf("borders: top thin, bottom thin, left thin, right thin; \
                pattern: pattern solid, fore-colour gray25;"),
        }
    head_xfs = [kind_to_xf_map[k] for k in head_kinds]
    data_xfs = [kind_to_xf_map[k] for k in kinds]
    #write_xls('xlwt_easyxf_simple_demo.xls', 'Demo', hdngs, data, heading_xf, data_xfs)
    write_xls_test(output_file, data_dict, region_list, headline_row, head_xfs, data_xfs)