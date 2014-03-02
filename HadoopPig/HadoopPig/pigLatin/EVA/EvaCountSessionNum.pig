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
%default PATH_INPUT_OCT 'works/input/aws/';
%default PATH_OUTPUT 'works/output/EVA/EvaCountSessionNum1025';

--(1)-2データの対応付け　10月
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowOctData GENERATE ISOFormat(time) AS time, GetClient(ap) AS client, uid, verb, cid;

--(3) Evaに絞る。
FilteredData = FILTER EditData BY (cid == 3) AND (SUBSTRING(time, 0, 10) >= '2012-10-25');

--(4) 不要な列（client, cid）を削除
EditData = FOREACH FilteredData GENERATE time, uid, verb;

--(5) セッションIDを振るためにuidでグループ化
Grouped = GROUP EditData BY uid; 

--(6) セッションIDの生成→{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize = FOREACH Grouped { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) timeを年月日に直して列の並べ替え
EditData = FOREACH Sessionize GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) uidでグループ化
GroupUid = GROUP EditData BY uid;

--(9) session回数をカウント
countSession = FOREACH GroupUid { 
    countS = DISTINCT EditData.session_id; 
    GENERATE FLATTEN(group), (int)COUNT(countS) AS scnt; 
} 

STORE countSession INTO '$PATH_OUTPUT' using PigStorage('\t');