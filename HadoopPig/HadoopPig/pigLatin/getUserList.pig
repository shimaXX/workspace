--UDFの定義
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT 'works/input/log_queue_activities_20120*xx.csv.gz';
%default PATH_OUTPUT 'works/output/galstergetUser';
--data/log_queue_activities_20120*xx.csv.gz

RowData = LOAD '$PATH_INPUT' USING PigStorage() 
    AS (f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray); 

ThinData = FOREACH RowData GENERATE cid, uid, GetClient(ap) AS client;
FilteredData = FILTER ThinData BY cid == 2 AND (client == 'sp');
Grouped = GROUP FilteredData BY (uid); 
ResultGroup = FOREACH Grouped { 
    GENERATE FLATTEN(group); 
}
STORE ResultGroup INTO '$PATH_OUTPUT' using PigStorage('\t');