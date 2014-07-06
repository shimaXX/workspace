-----------------------------------------
--attribution分析をするために必要なデータセットの構築
--1:buyまでのノードに絞る
--2:1について、buyより後のノードは除く
--3:1について、繰り返し/後戻りしているノードは削除し、マージする（UDFによる）
--4:各パスの長さ（深さ）を求めて、長さの分散を求める
--5:各パスの各ノードの共起数を計算（後でノード間の距離を計算するのに使用する）
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
define MergeVerb myUDF.MergeVerb();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT_BUYSES 'works/output/Mining/Ci-LaboSessionBuy0123';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionizeは先頭にtimeが必要
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid, GetMetaInfo(verb,ap) AS verb, GetClient(ap) AS client;

FilData = FILTER Edit BY (cid == 7 OR cid == 8) AND time > '2012-12-15';

Grp = GROUP FilData BY uid;

addSession = FOREACH Grp { 
    ord = ORDER FilData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, verb, time, session_id;

FilBuy = FILTER EditData BY verb == 'buy';

joinedBuySession = JOIN FilBuy BY session_id LEFT OUTER, EditData BY session_id; 

Ed = FOREACH joinedBuySession GENERATE
	$6 AS time,
	$7 AS session_id,
	$5 AS verb,
	$2 AS buyTime
;

FilData = FILTER Ed BY time <= buyTime;

Ed = FOREACH FilData GENERATE time, session_id, verb;

Grp = GROUP Ed BY session_id;

MergeVerb = FOREACH Grp { 
    ord = ORDER Ed BY time ASC;
    GENERATE MergeVerb(ord);
} 

STORE MergeVerb INTO '$PATH_OUTPUT_BUYSES' USING PigStorage('\t'); 