--UDFの定義
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT 'works/input/aws/2012-11-*.gz';
%default PATH_OUTPUT 'works/output/galsterGetRegisterDate';


--(1)データの対応付け
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time, 0, 10) AS days;

--(3) ci-laboに絞る。
FilteredData = FILTER EditData BY cid == 4;

Grouped = GROUP FilteredData BY (uid); 

Result01 = FOREACH Grouped { 
    day = FilteredData.days; 
    disDay = DISTINCT day;
    GENERATE FLATTEN(group), COUNT(disDay) AS count_day; 
} 

STORE Result01 INTO '$PATH_OUTPUT' using PigStorage('\t');