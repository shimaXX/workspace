# coding: utf-8

from xlrd import open_workbook, XL_CELL_TEXT, cellname
import re, os, sys
from datetime import datetime
from math import ceil, floor
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import lines
from matplotlib import font_manager as fm
from scipy.stats import linregress


class GraphCreator:
    def __init__(self, workbookname, sheetname, col_list):
        self.wb = open_workbook(workbookname) #'vr_bscs_blocks.xls'
        self.sheet = self.wb.sheet_by_name(sheetname)
        print 'Sheet:',self.sheet.name
        print self.sheet.cell(1,1).value
        self.nrows = self.sheet.nrows
        self.ncols = self.sheet.ncols
        
        self.col_list = col_list
        self.result = {}

        self.font_prop = self.set_font()
        self.line_kinds = ["-o", "-^", "-v", "-<", "->", "-s", "-+", "-x", "-D", "-d", "-1", "-2", "-3", "-4", "-h", "-H", "-p", "-|", "-_"]
        self.color_list = ["blue", "green", "cyan", "magenta", "yellow", "black", "#77ff77"]

    def create_data_set(self, plus_row, start_row=5):
        brand_name = None
        for row in xrange(start_row, self.nrows,3): # skip 3 rows
            brand_candidate = unicode(self.sheet.cell(row, self.col_list['brand']).value)
            if brand_candidate!='' and brand_name!=brand_candidate:                
                brand_name = brand_candidate
            title = unicode(self.sheet.cell(row, self.col_list['title']).value)
            if u'　計' in title: continue

            submit_date = unicode(self.sheet.cell(row, self.col_list['submit_date']).value)
            for col in xrange(self.col_list['rate'], self.ncols):
                if self.sheet.cell(row, col).value!='':
                    submit_amaunt = self.sheet.cell(row, col).value
                    if submit_amaunt!=0.0:
                        recognition_rate = self.sheet.cell(row+plus_row, col).value
                        if recognition_rate!='':
                            self.create_brand_data( \
                                    brand_name, title, submit_date, submit_amaunt, recognition_rate)
        
    def create_brand_data(self, brand_name, title, submit_date, submit_amaunt, recognition_rate):
        if brand_name not in self.result:
            self.result[brand_name] = {}
        if  title not in self.result[brand_name]:
            self.result[brand_name][title] = {'submit_date':submit_date,
                                              'submit_amaunt':[submit_amaunt],
                                              'recognition_rate':[recognition_rate]
                                              }
        else:
            self.result[brand_name][title]['submit_amaunt'].append(submit_amaunt)
            self.result[brand_name][title]['recognition_rate'].append(recognition_rate)
    
    def create_graph(self, head, max_amaunt, a=48.021502, b=0.150115):
        for brand, res in self.result.items():
            self.create_brand_graph(brand, res, head, max_amaunt, a, b)
    
    def create_brand_graph(self, brand, results, head,\
                     max_amaunt, a=48.021502, b=0.150115):
        print 'brand:',brand,'drawing...'
        # graph initialize
        plt.rc('font', **{'family': 'serif'})
        
        # canpas
        fig = plt.figure()        
        title = head+'('+brand+')'

        plt.title(title, size=20, fontproperties=self.font_prop)
        plt.xlabel(u"広告出稿額[億円]", fontproperties=self.font_prop)
        plt.ylabel(u"認知率[%]", fontproperties=self.font_prop)
        
        plt.xlim([0,max_amaunt])
        plt.ylim([0,100])
        
        titles = []
        itr = 0
        col_itr = 0
        for title, res in results.items():
            titles.append(title)
            submit_amaunt = np.cumsum(res['submit_amaunt'])
            recognition_rate = res['recognition_rate']
            plt.plot(submit_amaunt, recognition_rate, self.line_kinds[itr], color=self.color_list[col_itr])            
            itr +=1
            col_itr +=1
            if itr==len(self.line_kinds): itr=0
            if col_itr==len(self.color_list): col_itr=0

        itr = 0
        col_itr = 0
        # draw regression line
        for title, res in results.items():
            submit_amaunt = np.cumsum(res['submit_amaunt'])
            recognition_rate = res['recognition_rate']
            self.draw_regression_line(submit_amaunt,recognition_rate,col_itr)         
            itr +=1
            col_itr +=1
            if itr==len(self.line_kinds): itr=0
            if col_itr==len(self.color_list): col_itr=0

                    
        # draw 80% line
        rng = range(max_amaunt+1)
        plt.plot(rng, [80]*(max_amaunt+1), color='red', linestyle="--", linewidth=2)
        
        # draw norm line
        rng = self.drange(0,max_amaunt,0.1)
        plt.plot(rng, self.calculate_norm_value(a, b, rng), color='red',
                linestyle="--", linewidth=2)
        
        # draw legend
        font_prop = self.set_font(size=7)
        plt.legend(titles, loc="lower right", markerscale=1, prop=font_prop)

        
        # save graph file
        filename = os.getcwd()+"/graph_output/"+brand+".png"
        plt.savefig(filename)
        plt.close()
   
    def draw_regression_line(self,submit_amaunt,recognition_rate,col_itr):
        # draw simple linear regression line
        # linregressへのデータはx,yの順に格納
        slope, intercept, r, _, _ = linregress(np.array(submit_amaunt,dtype=np.float64),
                                               np.array(recognition_rate,dtype=np.float64))
        func = lambda x: x * slope + intercept
        front = max(submit_amaunt)
        rea = min(submit_amaunt)
        rng = self.drange(rea, front, 0.1)
        line_value = [func(i) for i in rng]
        plt.plot(rng, line_value, linestyle=":", color=self.color_list[col_itr], linewidth=1.5) #color='red',

    
    def drange(self,begin, end, step):
        rng = []
        n = begin
        while n+step <= end+step:
            rng.append(n)
            n+=step
        return rng
    
    def set_font(self,size='16'):
        font_path = 'C:/font/ipag00303/ipag.ttf'
        font_prop = fm.FontProperties(fname=font_path)
        font_prop.set_style('normal')
        font_prop.set_weight('light')
        font_prop.set_size(size)
        return font_prop

    def calculate_norm_value(self, a, b, rng): # 48.021502, 0.150115
        return [a*x**b for x in rng]
    
    def get_all_submit_amaunt_data(self):
        submit_amaunt_list = []
        recognition_rate_list = []
        for _, dic in gc.result.items():
            for _, t_dic in dic.items():
                submit_amaunt_list += np.cumsum(t_dic['submit_amaunt']).tolist()
                recognition_rate_list += t_dic['recognition_rate']
        return submit_amaunt_list, recognition_rate_list
                                                                
if __name__=='__main__':
    workbookname = u'【Weeklyトラッキング】データベース140704.xlsx'
    sheetname = u'①週別ｶﾚﾝﾀﾞｰ'
    col_list = {'brand':1,'title':3,'submit_date':5,'rate':8} # brand, title_name, submit_date, rate start column
    
    gc = GraphCreator(workbookname, sheetname, col_list)
    plus_row = 2
    gc.create_data_set(plus_row, start_row=5)
    
    submit_amaunt_list, recognition_rate_list \
        = gc.get_all_submit_amaunt_data()

    # create graph    
    head = u'【Ｗｅｅｋｌｙトラッキング調査】投資対効果'
    max_amaunt = 10
    gc.create_graph(head, max_amaunt) #a=48.021502, b=0.150115