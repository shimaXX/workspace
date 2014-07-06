-----------------------------------------
--エンゲージメント算出に利用するための値を取得
-----------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE_a  '2012-12-18'
%declare LAST_DATE_a  '2012-12-24'
%declare START_DATE_b  '2012-12-25'
%declare LAST_DATE_b  '2012-12-31'
%declare START_DATE_c  '2013-01-01'
%declare LAST_DATE_c  '2013-01-07'
%declare START_DATE_d  '2013-01-08'
%declare LAST_DATE_d  '2013-01-14'
%declare START_DATE_e  '2013-01-15'
%declare LAST_DATE_e  '2013-01-21'
%declare START_DATE_f  '2013-01-22'
%declare LAST_DATE_f  '2013-01-28'
%declare START_DATE_LONG  '2012-12-18'
%declare LAST_DATE_LONG  '2013-01-14'

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
define GetIntervalDate myUDF.GetIntervalDate('$LAST_DATE_a');
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/Minig/Ci-LaboEngage_PV';
%default PATH_OUTPUT_TOTAL 'works/output/Minig/Ci-LaboEngage_PV_TOTAL';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--対象者の絞り込みを行う
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid,
	GetPayment(ap) AS payment,  GetMetaInfo(verb, ap) AS meta;


--1week目
FilData = FILTER Edit BY (cid == 8 OR cid == 7) AND SUBSTRING(time,0,10)>= '$START_DATE_a' AND SUBSTRING(time,0,10)<= '$LAST_DATE_a';

Grp = GROUP FilData BY uid;
Result01 = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilData.meta) AS pv;


--2week目
FilData = FILTER Edit BY (cid == 8 OR cid == 7) AND SUBSTRING(time,0,10)>= '$START_DATE_b' AND SUBSTRING(time,0,10)<= '$LAST_DATE_b';

Grp = GROUP FilData BY uid;
Result02 = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilData.meta) AS pv;


--3week目
FilData = FILTER Edit BY (cid == 8 OR cid == 7) AND SUBSTRING(time,0,10)>= '$START_DATE_c' AND SUBSTRING(time,0,10)<= '$LAST_DATE_c';

Grp = GROUP FilData BY uid;
Result03 = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilData.meta) AS pv;


--4week目
FilData = FILTER Edit BY (cid == 8 OR cid == 7) AND SUBSTRING(time,0,10)>= '$START_DATE_d' AND SUBSTRING(time,0,10)<= '$LAST_DATE_d';

Grp = GROUP FilData BY uid;
Result04 = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilData.meta) AS pv;


--5week目
FilData = FILTER Edit BY (cid == 8 OR cid == 7) AND SUBSTRING(time,0,10)>= '$START_DATE_e' AND SUBSTRING(time,0,10)<= '$LAST_DATE_e';

Grp = GROUP FilData BY uid;
Result05 = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilData.meta) AS pv;


--6week目
FilData = FILTER Edit BY (cid == 8 OR cid == 7) AND SUBSTRING(time,0,10)>= '$START_DATE_f' AND SUBSTRING(time,0,10)<= '$LAST_DATE_f';

Grp = GROUP FilData BY uid;
Result06 = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilData.meta) AS pv;


--長期
FilData = FILTER Edit BY (cid == 8 OR cid == 7) AND SUBSTRING(time,0,10)>= '$START_DATE_LONG' AND SUBSTRING(time,0,10)<= '$LAST_DATE_LONG';

Grp = GROUP FilData BY uid;
Result07 = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilData.meta) AS pv;


--join
join01 = JOIN Result01 BY uid LEFT OUTER, Result02 BY uid;
Res01 = FOREACH join01 GENERATE 
	Result01::uid AS uid,
	Result01::pv AS pv01,
	Result02::pv AS pv02
;

join02 = JOIN Res01 BY uid LEFT OUTER, Result03 BY uid;
Res02 = FOREACH join02 GENERATE 
	Res01::uid AS uid,
	Res01::pv01 AS pv01,
	Res01::pv02 AS pv02,
	Result03::pv AS pv03
;

join03 = JOIN Res02 BY uid LEFT OUTER, Result04 BY uid;
Res03 = FOREACH join03 GENERATE 
	Res02::uid AS uid,
	Res02::pv01 AS pv01,
	Res02::pv02 AS pv02,
	Res02::pv03 AS pv03,
	Result04::pv AS pv04
;

join04 = JOIN Res03 BY uid LEFT OUTER, Result05 BY uid;
Res04 = FOREACH join04 GENERATE 
	Res03::uid AS uid,
	Res03::pv01 AS pv01,
	Res03::pv02 AS pv02,
	Res03::pv03 AS pv03,
	Res03::pv04 AS pv04,
	Result05::pv AS pv05
;

join05 = JOIN Res04 BY uid LEFT OUTER, Result06 BY uid;
Res05 = FOREACH join05 GENERATE 
	Res04::uid AS uid,
	Res04::pv01 AS pv01,
	Res04::pv02 AS pv02,
	Res04::pv03 AS pv03,
	Res04::pv04 AS pv04,
	Res04::pv05 AS pv05,
	Result06::pv AS pv06
;

join06 = JOIN Res05 BY uid LEFT OUTER, Result07 BY uid;
Res05 = FOREACH join06 GENERATE 
	Res05::uid AS uid,
	Res05::pv01 AS pv01,
	Res05::pv02 AS pv02,
	Res05::pv03 AS pv03,
	Res05::pv04 AS pv04,
	Res05::pv05 AS pv05,
	Res05::pv06 AS pv06,
	Result07::pv AS pv07
;

Result = FOREACH Res05 GENERATE uid,
	(pv01 IS NULL ? 0: pv01) AS pv01,
	(pv02 IS NULL ? 0: pv02) AS pv02,
	(pv03 IS NULL ? 0: pv03) AS pv03,
	(pv04 IS NULL ? 0: pv04) AS pv04,
	(pv05 IS NULL ? 0: pv05) AS pv05,
	(pv06 IS NULL ? 0: pv06) AS pv06,
	(pv07 IS NULL ? 0: pv07) AS pv07
;

Grp = GROUP Result all;
ResultTotal = FOREACH Grp GENERATE 
	SUM(Result.pv01),
	SUM(Result.pv02),
	SUM(Result.pv03),
	SUM(Result.pv04),
	SUM(Result.pv05),
	SUM(Result.pv06),
	SUM(Result.pv07)
;

STORE Result INTO '$PATH_OUTPUT' USING PigStorage();
STORE ResultTotal INTO '$PATH_OUTPUT_TOTAL' USING PigStorage();