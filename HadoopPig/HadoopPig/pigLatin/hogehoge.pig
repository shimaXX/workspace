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

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/aws/2012-12-15*';
%default PATH_OUTPUT_BUYSES 'works/output/GAMIFICATION/EvaTest0128';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionizeは先頭にtimeが必要
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid, verb;

Fil = FILTER Edit BY uid == 'eva506ae557ab30b' AND time <= '2012-12-15T10:20:25Z' AND time >= '2012-12-15T09:30:00Z' AND cid == 3;

DUMP Fil;
