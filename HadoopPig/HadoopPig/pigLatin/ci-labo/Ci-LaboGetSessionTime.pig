-----------------------------------------
--セッション時間の平均値を求めるpig script
-----------------------------------------
--変数への格納
%declare TIME_WINDOW  30m
%declare EXSTART_DATE '2012-11-07' --ci-laboは11/8からの集計を行う
%declare EXLAST_DATE  '2012-11-20' --つまり19日までのデータを取得する
%declare START_DATE  '2012-11-07' --つまり08日からのデータを取得する
%declare LAST_DATE  '2012-12-04' --つまり03日までのデータを取得する

--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCharacterCategory myUDF.GetCharacterCategory();
define GetClient myUDF.GetClient();
define GetPayment myUDF.GetPayment();
define GetCategory myUDF.GetCategory();
define GetNewflag myUDF.GetNewflag();
define GetReservationflag myUDF.GetReservationflag(); 
define GetNextDate myUDF.GetNextDate();
define GetSessionTime myUDF.GetSessionTime();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/ci-labo/';
%default PATH_OUTPUT_TIME 'works/output/Ci-Labo/Ci-LaboSessonTimeFull1203';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionizeは先頭にtimeが必要
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid,verb;

--(3) ci-laboに絞る
FilteredDataPrior = FILTER Edit BY cid == 4 AND SUBSTRING(time,0,10) > '$EXSTART_DATE';
FilteredDataPost = FILTER Edit BY cid == 4 AND SUBSTRING(time,0,10) > '$START_DATE';

--(4) 不要な列（cid）を削除
EditDataPrior = FOREACH FilteredDataPrior GENERATE uid, verb;
EditDataPost = FOREACH FilteredDataPost GENERATE time, uid;

--(5) 集計対象者を絞るためのuid毎,verb毎の集計
Grouped = GROUP EditDataPrior BY uid; 

CntPrior = FOREACH Grouped { 
    verb_count = EditDataPrior.verb; 
    GENERATE FLATTEN(group) AS uid, COUNT(verb_count) AS verbCnt; 
} 

FilteredPrior = FILTER CntPrior BY verbCnt > 0 ;
ResultPrior = FOREACH FilteredPrior GENERATE uid; 

--セッションカウント
Grp = GROUP EditDataPost BY uid;

addSession = FOREACH Grp { 
    ord = ORDER EditDataPost BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP EditData BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpUid = GROUP sessionTime BY uid;  

ResultPost = FOREACH grpUid  GENERATE FLATTEN(group) AS uid, AVG(sessionTime.session_time) AS ave_session_time;


--(7) 集計対象者用のデータのみに絞る(join)
Joined = join ResultPrior BY uid LEFT OUTER, ResultPost BY uid USING 'replicated';

--(8) データの取捨選択
Result = FOREACH Joined GENERATE 
	ResultPrior::uid AS uid,
	ResultPost::ave_session_time AS ave_session_time
;

STORE Result INTO '$PATH_OUTPUT_TIME' USING PigStorage('\t'); 