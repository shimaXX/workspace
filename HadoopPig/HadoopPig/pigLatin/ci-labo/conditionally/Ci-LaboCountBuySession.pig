-----------------------------------------
-- ci-laboは購入アイテム数だけbuyがverbとして入るため、buyのあるセッションをカウントする
-----------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare EXSTART_DATE '2012-11-07' --ci-laboは11/8からの集計を行う
%declare EXLAST_DATE  '2012-11-20' --つまり19日までのデータを取得する
%declare START_DATE  '2012-11-19' --つまり20日からのデータを取得する
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
define MergeVerb myUDF.MergeVerb();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/ci-labo/';
%default PATH_OUTPUT_BUYSES 'works/output/Ci-Labo/sessionBuy1203';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionizeは先頭にtimeが必要
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid, verb;

-- データを絞る
FilteredDataPrior = FILTER Edit BY cid == 4 AND SUBSTRING(time, 0, 10) > '$EXSTART_DATE' AND SUBSTRING(time, 0, 10) < '$EXLAST_DATE';
FilteredDataPost = FILTER Edit BY cid == 4 AND SUBSTRING(time, 0, 10) > '$START_DATE' AND SUBSTRING(time, 0, 10) < '$LAST_DATE';

-------------------------------------------------
-- 集計対象者を絞るためのuid毎,verb毎の集計
Grouped = GROUP FilteredDataPrior BY uid; 

CntPrior = FOREACH Grouped { 
    verb_count = FilteredDataPrior.verb; 
    GENERATE FLATTEN(group) AS uid, COUNT(verb_count) AS verbCnt; 
} 

FilteredPrior = FILTER CntPrior BY verbCnt > 0 ;
ResultPrior = FOREACH FilteredPrior GENERATE uid; 


--------------------------------------------
--ここからはsession
Grp = GROUP FilteredDataPost BY uid;

addSession = FOREACH Grp { 
    ord = ORDER FilteredDataPost  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, verb, time, session_id;

FilBuy = FILTER EditData BY verb == 'buy';

Grp = GROUP FilBuy BY uid;

ResultPost = FOREACH Grp { 
    cnt = DISTINCT FilBuy.session_id;
    GENERATE FLATTEN(group) AS uid, COUNT(cnt) AS buyCnt;
} 


--------------------------------------------
--join
-- 集計対象者用のデータのみに絞る(join)
Joined = join ResultPrior BY uid LEFT OUTER, ResultPost BY uid USING 'replicated';

-- データの取捨選択
Result = FOREACH Joined GENERATE 
	ResultPrior::uid AS uid,
	ResultPost::buyCnt AS buyCnt
;

STORE Result INTO '$PATH_OUTPUT_BUYSES' USING PigStorage('\t'); 