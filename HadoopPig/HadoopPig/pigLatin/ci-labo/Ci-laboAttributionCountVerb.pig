-----------------------------------------
--attribution分析をするために必要なデータセットの構築
--1:session毎に繰り返し、戻るボタンで戻ったページを削除する
--2:verbの数珠つなぎでカウントを行う
-----------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-28' --つまり29日からのデータを取得する
%declare LAST_DATE  '2012-11-05' --つまり4日までのデータを取得する
%declare AXSTART_DATE  '2012-10-21' --つまり22日からのデータを取得する
%declare AXLAST_DATE  '2012-10-29' --つまり28日までのデータを取得する

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
define MergeVerbRespectively myUDF.MergeVerbRespectively();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT 'works/output/Mining/Ci-LaboTranseVerb0123';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionizeは先頭にtimeが必要
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid, GetMetaInfo(verb,ap) AS verb;

FilData = FILTER Edit BY (cid == 8 OR cid == 7)
					AND SUBSTRING(time,0,10) > '2012-12-15';

Grp = GROUP FilData BY uid;

addSession = FOREACH Grp { 
    ord = ORDER FilData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

Ed = FOREACH addSession GENERATE uid, verb, time, session_id;

Grp = GROUP Ed BY session_id;

MergeVerb = FOREACH Grp { 
    ord = ORDER Ed BY time ASC;
    GENERATE FLATTEN(MergeVerbRespectively(ord));
} 

Grouped = GROUP MergeVerb BY session_id;

Result03 = FOREACH Grouped { 
    ord02 = ORDER MergeVerb  BY time ASC;
    GENERATE FLATTEN(JuxtaposeNextVerb(ord02));
} 

--ここまでで各ユーザ毎のlastVerbとpostVerbの整形は終了
Result04 = FILTER Result03 BY postVerb != '';

Grouped = GROUP Result04 BY (verb, postVerb);

Result05 = FOREACH Grouped { 
    cnt = Result04.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS cnt;
} 

STORE Result05 INTO '$PATH_OUTPUT' USING PigStorage('\t'); 