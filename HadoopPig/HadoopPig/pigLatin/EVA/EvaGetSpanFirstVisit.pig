----------------------------------------------------
--sprocket導入前の会員のverbの数を導入後の数と比較する
--sprocket導入後にアクションを開始したユーザのみを拾ってくる
----------------------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare OCT_START_DATE  '2012-09-30' --つまり10/1日からのデータを取得する
%declare NOV_START_DATE  '2012-10-31' --つまり11/1日からのデータを取得する
%declare DEC_START_DATE  '2012-11-30' --つまり12/1日からのデータを取得する

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
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/EVA/EvaSpanFirstVisit1217';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionizeは先頭にtimeが必要
Edit = FOREACH RowData GENERATE time, uid, cid, verb, SUBSTRING(time,0,7) AS month;

--データに絞る
FilData = FILTER Edit BY cid == 3 AND time > '$OCT_START_DATE';

--不要なカラムを削除
EditData = FOREACH FilData GENERATE uid, time, verb, month;


--------------------------------------------
--entryのあるユーザに絞る（joinの大元）
entryUser = FILTER EditData BY verb == 'entry';
entryUser = FOREACH entryUser GENERATE uid, time;


--------------------------------------------
--verbの最小日時を求める
Grp = GROUP EditData BY uid;
minActTime = FOREACH Grp GENERATE FLATTEN(group) AS uid, MIN(EditData.time) AS minTime; 


--------------------------------------------
--buyの最小日時
onlyBuy = FILTER EditData BY verb == 'buy';
Grp = GROUP onlyBuy BY uid;
minBuyTime = FOREACH Grp GENERATE FLATTEN(group) AS uid, MIN(onlyBuy.time) AS buyTime; 


--------------------------------------------
--mail_magagin_regの最小日時
onlyMail = FILTER EditData BY verb == 'mail_magazine_reg';
Grp = GROUP onlyMail BY uid;
minMailTime = FOREACH Grp GENERATE FLATTEN(group) AS uid, MIN(onlyMail.time) AS mailTime; 


--------------------------------------------
--join
--entryとverbMin
Joined01 = JOIN entryUser BY uid , minActTime BY uid;
Result01 = FOREACH Joined01 GENERATE
	entryUser::uid AS uid,
	entryUser::time AS time,
	minActTime::minTime AS minActTime
;

--result01と最小購買日
Joined02 = JOIN Result01 BY uid , minBuyTime BY uid;
Result02 = FOREACH Joined02 GENERATE
	Result01::uid AS uid,
	Result01::time AS time,
	Result01::minActTime AS minActTime,
	minBuyTime::buyTime AS buyTime
;

--result01とメルマガ登録日
Joined03 = JOIN Result02 BY uid , minMailTime BY uid;
Result03 = FOREACH Joined03 GENERATE
	Result02::uid AS uid,
	Result02::minActTime AS minActTime,
	Result02::time AS entryTime,
	Result02::buyTime AS buyTime,
	minMailTime::mailTime AS mailTime
;

STORE Result03 INTO '$PATH_OUTPUT' USING PigStorage('\t'); 