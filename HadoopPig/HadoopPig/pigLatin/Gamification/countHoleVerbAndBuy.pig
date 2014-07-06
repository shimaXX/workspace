--UDFの定義
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT 'works/input/aws/2012-11-*.gz';
%default PATH_OUTPUT 'works/output/EVA/CorBuyAndVerb';

--(1)データの対応付け
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time, 0, 10) AS time;

--(3) galsterに絞る。spに絞る。
FilteredData = FILTER EditData BY cid == 3;

Grouped = GROUP FilteredData BY time;

Result = FOREACH Grouped { 
	verb = FilteredData.verb;
    fil_buy = FILTER FilteredData BY verb == 'buy';
    GENERATE FLATTEN(group) AS time, COUNT(verb) AS cntVerb ,COUNT(fil_buy) AS cntBuy; 
}

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');