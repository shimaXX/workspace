# coding: utf-8

#import pyximport; pyximport.install()
import io

if __name__=='__main__':
    import CySimulation
    
    period = 1440 # second of a day #86400 #1440 #24
    daybuget = 1000000
    goalcpc = 100
    bidcap = 90
    ctrbin = 0.01
    days = 2
    user_agent_num = 600 # 1000
    bid_agent_num = 100
            
    bid = CySimulation.ComputeBid(period, daybuget, goalcpc, bidcap,ctrbin) #period, daybuget, gcpc, bidcap,ctrbin
    
    with io.open('sin_test','a') as f:
        bid.output(
            f,user_agent_num,bid_agent_num,days)