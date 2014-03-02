----------------------------------------------------
--sprocket導入前の会員のverbの数を導入後の数と比較する
--sprocket導入後にアクションを開始したユーザのみを拾ってくる
----------------------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare OCT_START_DATE  '2012-10-01' --つまり10/1日からのデータを取得する
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
%default PATH_OUTPUT_NEWUSER 'works/output/GAMIFICATION/newUser';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionizeは先頭にtimeが必要
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS days, uid, cid, verb;

--Evaで各月のデータに絞る
Data = FILTER Edit BY cid == 3 AND days > '$OCT_START_DATE';

--各月のデータにmonthのカラムを追加
Data = FOREACH Data GENERATE days, uid, cid, verb, SUBSTRING(days,0,7) AS month;

--------------------------------------------
--各月のUUをカウントする
UUgrp = GROUP Data BY month;
UU = FOREACH UUgrp{
	u = DISTINCT Data.uid;
	GENERATE FLATTEN(group) AS month, (int)COUNT(u) AS MUU; 
}

------------------------------------------------
--既会員数
--既会員と新規会員はloginとentryの両方があるか、無いかで判断
--1 loginのあるユーザのみに絞る（既と新の両者が混在する）
--2 entryのあるユーザのみに絞る（新のみになる）
--3 joinしてカラムが空かどうかで判断

--loginユーザを絞る
Login = FILTER Data BY verb == 'login';

--entryユーザを絞る
Entry = FILTER Data BY verb == 'entry';

----------------
--join
Joined = JOIN Login BY uid LEFT OUTER, Entry BY uid USING 'replicated';

--データの整形
Res = FOREACH Joined GENERATE
	Login::uid AS uid,
	Login::days AS loginDay,
	Login::month  AS month,
	Entry::days  AS entryDay
;

---------------
--entryDayにfilterできないのでflagを立てる
Grp = GROUP Res BY uid;
addFlagRes = FOREACH Grp GENERATE FLATTEN(group) AS uid, FLATTEN(Res.loginDay) AS loginDay, 
					FLATTEN(Res.entryDay) AS entryDay, FLATTEN(Res.month) AS month, (int)COUNT(Res.entryDay) AS entryFlag;


---------------------------------------------------------
--既会員数をカウントする
--UUから既会員数を引いて、会員登録率の分母を作る
FilPrvEntry = FILTER addFlagRes BY entryFlag == 0;

Grp = GROUP FilPrvEntry BY month;
CntPrvEntUU = FOREACH Grp{
	uu = DISTINCT FilPrvEntry.uid;
	GENERATE FLATTEN(group) AS month, (int)COUNT(uu) AS cntPrvEntUU;
}

------------------------------------------------------------
--新規会員数を算出
FilNewEntry = FILTER addFlagRes BY entryFlag != 0;

Grp = GROUP FilNewEntry BY month;
CntNewEntUU = FOREACH Grp{
	uu = DISTINCT FilNewEntry.uid;
	GENERATE FLATTEN(group) AS month, (int)COUNT(uu) AS cntNewEntUU;
}

----------------------------------------------------------
--各月のUUと既会員数、新規会員数をjoinする
--UUと既会員数のjoin :A
--Aと新規会員数ｒのjoin

Joined01 = JOIN UU BY month, CntPrvEntUU BY month USING 'replicated';
Result01 = FOREACH Joined01 GENERATE
	UU::month AS month,
	UU::MUU AS MUU,
	CntPrvEntUU::cntPrvEntUU AS cntPrvEntUU
;

Joined02 = JOIN Result01 BY month, CntNewEntUU BY month USING 'replicated';
Result02 = FOREACH Joined02 GENERATE
	Result01::month AS month,
	Result01::MUU AS MUU,
	Result01::cntPrvEntUU AS cntPrvEntUU,
	CntNewEntUU::cntNewEntUU AS cntNewEntUU
;

LL = LIMIT Result02 10;
DUMP LL;

--STORE Result INTO '$PATH_OUTPUT_NEWUSER' USING PigStorage('\t'); 