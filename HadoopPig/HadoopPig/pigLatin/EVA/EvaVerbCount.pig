--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE '2012-10-31'

--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategory myUDF.GetCategory();
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT_OCT 'works/input/aws/';
%default PATH_OUTPUT 'works/output/EVA/EvaVerbCount1212';

--(1)-2データの対応付け　10月
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowOctData GENERATE uid, verb, cid, SUBSTRING(time,0,10) AS time;

--(3) EVAに絞る
FilteredData = FILTER EditData BY cid == 3 AND time > '2012-11-12'; --'$START_DATE';

--(4) 不要な列（cid）を削除
EditData = FOREACH FilteredData GENERATE uid, verb;

--(5) uid毎,verb毎の集計
Grouped = GROUP EditData BY (uid, verb); 

Result = FOREACH Grouped { 
    verb_count = EditData.verb; 
    GENERATE FLATTEN(group), COUNT(verb_count) AS verbCnt; 
} 

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');