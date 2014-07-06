--変数への格納
%declare TIME_WINDOW  30m

--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCharacterCategory myUDF.GetCharacterCategory();
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT_OCT 'works/input/oct/';
%default PATH_OUTPUT 'works/output/EVA/EvaRegisterDate';

--(1)-2データの対応付け　10月
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowOctData GENERATE uid, verb, cid, GetClient(ap) AS client, SUBSTRING(time, 0, 10) AS time;

--(3) Evaに絞る。spに絞る。
FilteredData = FILTER EditData BY (cid == 3) AND (time > '2012-10-10');

--(4) 不要な列（client, cid）を削除
EditData = FOREACH FilteredData GENERATE uid, time;

--(5) uidでグループ化
Grouped = GROUP EditData BY (uid); 

Result = FOREACH Grouped { 
    row_time = EditData.time; 
    GENERATE FLATTEN(group), MAX(row_time), MIN(row_time); 
} 
STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');