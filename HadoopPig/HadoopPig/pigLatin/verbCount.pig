--UDFの定義
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT 'works/input/log_queue_activities_20120*xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/oct/';
%default PATH_OUTPUT 'works/output/GalsterVerbCount1024';

--(1)データの対応付け
--RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
--  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
--;
--(1)データの対応付け　10月
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowOctData GENERATE uid, verb, cid, GetClient(ap) AS client, SUBSTRING(time, 0,10) AS time;

--(3) galsterに絞る。spに絞る。
FilteredData = FILTER EditData BY (cid == 2) AND (SUBSTRING(time, 0, 10) >= '2012-10-18') AND (SUBSTRING(time, 0, 10) < '2012-10-25') AND (client == 'sp');

--(4) 不要な列（cid）を削除
EditData = FOREACH FilteredData GENERATE uid, verb;

Grouped = GROUP FilteredData BY (uid, verb); 

Result = FOREACH Grouped { 
    verb_count = FilteredData.verb; 
    GENERATE FLATTEN(group), COUNT(verb_count); 
} 

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');