# coding: utf-8

import time

@outputSchema("y:bag{t:tuple(len:int,word:chararray)}") 
def collectBag(bag):
    outBag = []
    for word in bag:
        tup=(len(bag), word[1])
        outBag.append(tup)
    return outBag

@outputSchema("datediff:int")
def DateDiff(a,b):
    a_time = time.mktime(time.strptime(a,'%Y-%m-%d'))
    b_time = time.mktime(time.strptime(b,'%Y-%m-%d'))
    return int( (a_time - b_time) / 86400 )

@outputSchema("c_region:int,c_channel:chararray,date:chararray,hour:chararray,a_cnt:int,t:tuple")
def splitData(string):
    outBag = []
    data = string.split('\t')
    region = data[0]
    channel = data[1]
    date = data[2]
    hour = data[3]
    a_cnt = data[4]
    tup = data[4:]
    return outBag