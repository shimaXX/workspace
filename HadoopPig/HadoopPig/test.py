import org.apache.pig.data.DataType as DataType
import org.apache.pig.impl.logicalLayer.schema.SchemaUtil as SchemaUtil
from org.apache.pig.scripting import *


#@outputSchema("c_region:int,c_channel:chararray,date:chararray,hour:chararray,a_cnt:int,s:chararray")
@outputSchema("s:chararray")
def splitData(input):
    print input.getField(0).schema.getFields()
    data = input.split()
    #data = s.split('\t')
    #print data
    print data
    #region = data[0]
    #channel = data[1]
    #date = data[2]
    #hour = data[3]
    #a_cnt = data[4]
    #tup = ','.join(map(str,data[4:]))
    #return region, channel, date, hour, a_cnt, tup
    return data
