# coding: utf-8

import matplotlib.pyplot as plt
import os, io
import numpy as np
from math import ceil, floor
from scipy.stats import linregress
from matplotlib import lines
from matplotlib import font_manager as fm

class GraphCreater:
    dataset = None
    header = None
    
    def __init__(self):
        self.font_prop = self.set_font()
    
    def create_dataset(self, line):
        """channel_code    date_time    minute    region    wtd    hour    VR_r_households    VR_r_individuals    VR_r_fm_and_m_4to12    VR_r_fm_and_m_13to19    VR_r_m_20to34    VR_r_m_35to49    VR_r_m_over50    VR_r_fm_20to34    VR_r_fm_35to49    VR_r_fm_over50    toshiba_r_households    toshiba_r_individuals    toshiba_r_fm_and_m_4to12    toshiba_r_fm_and_m_13to19    toshiba_r_m_20to34    toshiba_r_m_35to49    toshiba_r_m_over50    toshiba_r_fm_20to34    toshiba_r_fm_35to49    toshiba_r_fm_over50"""
        data = line.strip().split(',')
        if self.dataset is None:
            if not self.isheader(data):
                self.dataset = np.array(data)
        else:
            self.dataset = np.vstack((self.dataset,data))

    def isheader(self, data):
        try:
            int(data[2])
            return False
        except:
            self.header = np.array(data)
            print self.header
            return True

    def save_graph(self, region_list, demogra_list, wtd_list, timeband_list):
        for region in region_list:
            for demogra in demogra_list:
                self.save_demogra_graph(demogra, region)
                print "done save demogra plot"
                for times in timeband_list:
                    self.save_weekend_demogra_graph(region, times, demogra)
                    self.save_weekday_demogra_graph(region, times, demogra)
#            for times in timeband_list:
#                self.save_weekend_graph(region, times)
#                self.save_weekday_graph(region, times)

    def save_demogra_graph(self, demogra, region):
        vr = u'VR'+demogra
        toshiba = u'toshiba'+demogra
        try:
            idx = np.where((self.header==vr) | (self.header==toshiba))
            print len(idx)
            raw_slised = self.dataset[self.dataset[:,0]==region]
            col_slised = raw_slised[:, idx]
            res = col_slised[:,0]
            
            # simple linear regression
            self.graph_to_file(res, region, demogra)
        except Exception, e:
            print "error is:", e
            print 'no data:', region , demogra

    def graph_to_file(self, res, region, demogra):
        slope, intercept, r, _, _ = linregress(np.array(res[:,1],dtype=np.float64), np.array(res[:,0],dtype=np.float64))
        
        # graph initialize
        plt.rc('font', **{'family': 'serif'})
        
        # canpas
        fig = plt.figure()

        title = region+self.change_demogra(demogra)
        title += "(r=%.2f)" % r
        
        plt.title(title, size=20, fontproperties=self.font_prop)
        plt.xlabel("Toshiba", fontproperties=self.font_prop)
        plt.ylabel("VR", fontproperties=self.font_prop)
        max_value = max(ceil(float(max(np.array(res[:,1],dtype=np.float)))), ceil(float(max(np.array(res[:,0],dtype=np.float)))))+2
        plt.xlim([0,max_value])
        plt.ylim([0,max_value])
        plt.scatter(res[:,1],res[:,0])
        
        # draw simple linear regression line
        func = lambda x: x * slope + intercept
        rng = range(int(ceil(max_value)))
        line_value = [func(i) for i in rng]
        plt.plot(rng, line_value, color='red', linestyle="--")
        
        # draw center line
        plt.plot(rng, rng, color='black', linestyle="-", linewidth=2.5)
        
        # save graph file
        filename = os.getcwd()+"/output_"+region+demogra
        filename += "(r=%.2f).png" % r
        plt.savefig(filename)
        plt.close()
    
    def set_font(self):
        font_path = 'C:/font/ipag00303/ipag.ttf'
        font_prop = fm.FontProperties(fname=font_path)
        font_prop.set_style('normal')
        font_prop.set_weight('light')
        font_prop.set_size('16')
        return font_prop

    def change_demogra(self, demogra):
        if demogra==u'_r_housefolds':
            return '_世帯'
        elif demogra==u'_r_individuals':
            return '_個人全体'
        elif demogra==u'_r_m_20to34':
            return '_M1'
        elif demogra==u'_r_m_35to49':
            return '_M2'
        elif demogra==u'_r_m_over50':
            return '_M3'
        elif demogra==u'_r_fm_20to34':
            return '_F1'
        elif demogra==u'_r_fm_35to49':
            return '_F2'
        elif demogra==u'_r_fm_over50':
            return '_F3'

    def save_weekend_graph(self, region, times):
        vr = u'VR'+u'_r_individuals'
        toshiba = u'toshiba'+u'_r_individuals'
        try:
            region_slised = self.dataset[self.dataset[:,0]==region]
            wtd_row_idx = np.where((region_slised[:,1]==u'�y') | (region_slised[:,1]==u'��'))[0]
            wtd_slised = region_slised[wtd_row_idx, :]
    
            time_row_idx = np.where( (np.array(wtd_slised[:,2],dtype=np.int)>=int(times[0])) &
                                      (np.array(wtd_slised[:,2],dtype=np.int)<int(times[1])) )[0]
            time_slised = wtd_slised[time_row_idx, :]
    
            col_idx = np.where( (self.header==vr) | (self.header==toshiba) )[0]
            res = time_slised[:,col_idx]
            
            # simple linear regression
            slope, intercept, r, _, _ = linregress(res[:,1], res[:,0])
            
            # graph initialize
            plt.rc('font', **{'family': 'serif'})
            
            # canpas
            fig = plt.figure()
            
            plt.xlabel("Toshiba")
            plt.ylabel("VR")
            max_value = max(ceil(float(max(np.array(res[:,1],dtype=np.float)))), ceil(float(max(np.array(res[:,0],dtype=np.float)))))+2
            plt.xlim([0,max_value])
            plt.ylim([0,max_value])
            plt.scatter(res[:,1],res[:,0])
            
            # draw simple linear regression line
            func = lambda x: x * slope + intercept
            rng = range(max_value)
            line_value = [func(i) for i in rng]
            plt.plot(rng, line_value)
            
            # save graph file
            filename = os.getcwd()+"/output_"+region+"_weekday_"+times[0]+"-"+times[1]
            filename += "(r=%.2f).png" % r
            plt.savefig(filename)
            plt.close()
        except Exception, e:
            print "error is:", e
            print 'no data:', region , times
   
    def save_weekend_demogra_graph(self, region, times, demogra):
        vr = u'VR'+demogra
        toshiba = u'toshiba'+demogra
        try:
            region_slised = self.dataset[self.dataset[:,0]==region]
            wtd_row_idx = np.where((region_slised[:,1]==u'�y') | (region_slised[:,1]==u'��'))[0]
            wtd_slised = region_slised[wtd_row_idx, :]
    
            time_row_idx = np.where( (np.array(wtd_slised[:,2],dtype=np.int)>=int(times[0])) &
                                      (np.array(wtd_slised[:,2],dtype=np.int)<int(times[1])) )[0]
            time_slised = wtd_slised[time_row_idx, :]
    
            col_idx = np.where( (self.header==vr) | (self.header==toshiba) )[0]
            res = time_slised[:,col_idx]
            
            # simple linear regression
            slope, intercept, r, _, _ = linregress(res[:,1], res[:,0])
            
            # graph initialize
            plt.rc('font', **{'family': 'serif'})
            
            # canpas
            fig = plt.figure()
            
            plt.xlabel("Toshiba")
            plt.ylabel("VR")
            max_value = max(ceil(float(max(np.array(res[:,1],dtype=np.float)))), ceil(float(max(np.array(res[:,0],dtype=np.float)))))+2
            plt.xlim([0,max_value])
            plt.ylim([0,max_value])
            plt.scatter(res[:,1],res[:,0])
            
            # draw simple linear regression line
            func = lambda x: x * slope + intercept
            rng = range(max_value)
            line_value = [func(i) for i in rng]
            plt.plot(rng, line_value)
            
            # save graph file
            filename = os.getcwd()+"/output_"+region+"_weekday_"+times[0]+"-"+times[1]
            filename += "(r=%.2f).png" % r
            plt.savefig(filename)
            plt.close()
        except Exception, e:
            print "error is:", e
            print 'no data:', region , times        
   
    def save_weekday_graph(self, region, times):
        vr = u'VR'+u'_r_individuals'
        toshiba = u'toshiba'+u'_r_individuals'
        try:
            region_slised = self.dataset[self.dataset[:,0]==region]
            wtd_row_idx = np.where((region_slised[:,1]!=u'�y') | (region_slised[:,1]!=u'��'))[0]
            wtd_slised = region_slised[wtd_row_idx, :]
    
            time_row_idx = np.where( (np.array(wtd_slised[:,2],dtype=np.int)>=int(times[0])) &
                                      (np.array(wtd_slised[:,2],dtype=np.int)<int(times[1])) )[0]
            time_slised = wtd_slised[time_row_idx, :]
    
            col_idx = np.where( (self.header==vr) | (self.header==toshiba) )[0]
            res = time_slised[:,col_idx]
            
            # simple linear regression
            slope, intercept, r, _, _ = linregress(res[:,1], res[:,0])
            
            # graph initialize
            plt.rc('font', **{'family': 'serif'})
            
            # canpas
            fig = plt.figure()
            
            plt.xlabel("Toshiba")
            plt.ylabel("VR")
            max_value = max(ceil(float(max(np.array(res[:,1],dtype=np.float)))), ceil(float(max(np.array(res[:,0],dtype=np.float)))))+2
            plt.xlim([0,max_value])
            plt.ylim([0,max_value])
            plt.scatter(res[:,1],res[:,0])
            
            # draw simple linear regression line
            func = lambda x: x * slope + intercept
            rng = range(max_value)
            line_value = [func(i) for i in rng]
            plt.plot(rng, line_value)
            
            # save graph file
            filename = os.getcwd()+"/output_"+region+"_weekday_"+times[0]+"-"+times[1]
            filename += "(r=%.2f).png" % r
            plt.savefig(filename)
            plt.close()
        except Exception, e:
            print "error is:", e
            print 'no data:', region , times

    def save_weekday_demogra_graph(self, region, times, demogra):
        vr = u'VR'+demogra
        toshiba = u'toshiba'+demogra
        try:
            region_slised = self.dataset[self.dataset[:,0]==region]
            wtd_row_idx = np.where((region_slised[:,1]!=u'�y') | (region_slised[:,1]!=u'��'))[0]
            wtd_slised = region_slised[wtd_row_idx, :]
    
            time_row_idx = np.where( (np.array(wtd_slised[:,2],dtype=np.int)>=int(times[0])) &
                                      (np.array(wtd_slised[:,2],dtype=np.int)<int(times[1])) )[0]
            time_slised = wtd_slised[time_row_idx, :]
    
            col_idx = np.where( (self.header==vr) | (self.header==toshiba) )[0]
            res = time_slised[:,col_idx]
            
            # simple linear regression
            slope, intercept, r, _, _ = linregress(res[:,1], res[:,0])
            
            # graph initialize
            plt.rc('font', **{'family': 'serif'})
            
            # canpas
            fig = plt.figure()
            
            plt.xlabel("Toshiba")
            plt.ylabel("VR")
            max_value = max(ceil(float(max(np.array(res[:,1],dtype=np.float)))), ceil(float(max(np.array(res[:,0],dtype=np.float)))))+2
            plt.xlim([0,max_value])
            plt.ylim([0,max_value])
            plt.scatter(res[:,1],res[:,0])
            
            # draw simple linear regression line
            func = lambda x: x * slope + intercept
            rng = range(max_value)
            line_value = [func(i) for i in rng]
            plt.plot(rng, line_value)
            
            # save graph file
            filename = os.getcwd()+"/output_"+region+"_weekday_"+times[0]+"-"+times[1]
            filename += "(r=%.2f).png" % r
            plt.savefig(filename)
            plt.close()
        except Exception, e:
            print "error is:", e
            print 'no data:', region , times   
    
if __name__=='__main__':
    basepath = 'C:/Users/shimada/Documents/RW/demogra_graph/'
    fname = basepath+'demogra_data_test.csv'
    
    region_list = (u'関東',u'関西',u'名古屋')
    "'VR_r_m_20to34', u'toshiba_"
    demogra_list = (u'_r_individuals', #u'_r_housefolds',
                    u'_r_m_20to34', u'_r_m_35to49', u'_r_m_over50',
                    u'_r_fm_20to34', u'_r_fm_35to49', u'_r_fm_over50') # VR, toshiba
    wtd_list = ((u'月',u'火',u'水',u'木',u'金'),(u'土',u'日'))
    timeband_list = ((u'5',u'9'), (u'9',u'19'), (u'19',u'23'), (u'23',u'29'))
    gc = GraphCreater()
    
    with io.open(fname, 'r') as f:
        for line in f:
            gc.create_dataset(line)
    print 'done get data'
    
    # create graph
    gc.save_graph(region_list, demogra_list, wtd_list, timeband_list)