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
--%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/oct/';
%default PATH_OUTPUT 'works/output/EVA/EvaCountLoginDays1025';

--(1)-2データの対応付け　10月
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

EditData = FOREACH RowOctData GENERATE uid, cid, SUBSTRING(time, 0, 10) AS days, GetClient(ap) AS client;
FilteredData = FILTER EditData BY (cid == 3) AND (days > '2012-10-24');
Grouped = GROUP FilteredData BY (uid); 

Result01 = FOREACH Grouped { 
    day = FilteredData.days; 
    disDay = DISTINCT day;
    GENERATE FLATTEN(group), COUNT(disDay) AS count_day; 
} 

STORE Result01 INTO '$PATH_OUTPUT' using PigStorage('\t');