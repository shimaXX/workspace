--変数への格納
%declare TIME_WINDOW  30m

--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();

--入出力パスの定義
%default PATH_INPUT 'works/input/log_queue_activities_201209xx.csv.gz';
--%default PATH_INPUT 'works/input/';
%default PATH_OUTPUT 'works/output/testLowGraph09-01_09-08';


--(1)データの対応付け
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;

FilteredData = FILTER RowData BY (cid == 2) AND (uid == 'ngr50177d3130208')
	AND (time >= '2012-09-01 00:00:00' AND time < '2012-09-08 00:00:00');
EditData = FOREACH FilteredData GENERATE ISOFormat(time) AS time, uid, verb;

Grouped = GROUP EditData BY uid; 

Result = FOREACH Grouped { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

Result02 = FOREACH Result GENERATE uid, verb, time, session_id;

Grouped = GROUP Result02 BY uid;

Result03 = FOREACH Grouped { 
    ord02 = ORDER Result02  BY time ASC;
    GENERATE FLATTEN(JuxtaposeNextVerb(ord02));
} 

Result04 = FILTER Result03 BY postVerb != '' AND postVerb != verb;

STORE Result04 INTO '$PATH_OUTPUT' using PigStorage('\t');
--STORE LL INTO '$PATH_OUTPUT' using PigStorage('\t');