--UDFの定義
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT 'works/input/log_queue_activities_20120*xx.csv.gz';
%default PATH_OUTPUT 'works/output/galsterGetRegisterDate';
--data/log_queue_activities_20120*xx.csv.gz

--(1)データの対応付け
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowData GENERATE uid, verb, cid, GetClient(ap) AS client, SUBSTRING(time, 0, 10) AS time;

--(3) galsterに絞る。spに絞る。
FilteredData = FILTER EditData BY (cid == 2) AND (client == 'sp');

--(4) 不要な列（client, cid）を削除
EditData = FOREACH FilteredData GENERATE uid, time;

--(5) uidでグループ化
Grouped = GROUP EditData BY (uid); 

Result = FOREACH Grouped { 
    row_time = EditData.time; 
    GENERATE FLATTEN(group), MAX(row_time), MIN(row_time); 
} 
STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');