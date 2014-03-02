-----------------------------------------
--季節変動の周期性を調べるためにuid毎にdailyでアクティビティ数を取得する
--Zはリスト化し1変数ごとにまとめる
--D全ての変数をuid毎に取得する
-----------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-12-18'--'2012-12-18'
%declare LAST_DATE  '2013-02-04'--'2013-02-04'
%declare AXSTART_DATE  '2012-10-21'
%declare AXLAST_DATE  '2012-10-29'

--条件決めのパラメタ
%declare BOUND  '13000'
%declare DAYS_BOUND '120' 

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
define GetIntervalDate myUDF.GetIntervalDate('$LAST_DATE');
define GetIntervalDateInd myUDF.GetIntervalDateIndividuals();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();
define GetAverageInterval myUDF.GetAverageIntervalDays();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT_Z01 'works/output/Mining/GalsterCPM_Z01_20130327';
%default PATH_OUTPUT_Z02 'works/output/Mining/GalsterCPM_Z02_20130327';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--対象者の絞り込みを行う
Edit = FOREACH RowData GENERATE SUBSTRING(time, 0, 10) AS date, uid, cid,
	GetPayment(ap) AS payment, verb, ISOFormat(time) AS ISOtime;
FilData = FILTER Edit BY cid == 2;

----------------------------------------------
--来店したことのある全uidを取得
Grp = GROUP FilData BY uid;
UUID = FOREACH Grp GENERATE FLATTEN(group) AS uid;

--------------------------------
--前回来店からの日数の対数の取得
GrpDate = GROUP FilData BY (uid, date);
VisitDate = FOREACH GrpDate	GENERATE FLATTEN(group) AS (uid, Vdate);

joinedZ01 = JOIN UUID BY uid LEFT OUTER, VisitDate BY uid USING 'replicated';
ResultZ01 = FOREACH joinedZ01 GENERATE
	UUID::uid AS uid,
	VisitDate::Vdate AS Vdate
;

--------------------------------
--購買額の取得
FilBuyData = FILTER Edit BY verb == 'buy';
GrpDate = GROUP FilBuyData BY (uid, date);
NumOfPayment = FOREACH GrpDate GENERATE FLATTEN(group) AS (uid, Bdate), SUM((int)FilBuyData.payment) AS payment;

joinedZ03 = JOIN UUID BY uid LEFT OUTER, BuyDate BY uid USING 'replicated';
ResultZ03 = FOREACH joinedZ03 GENERATE
	UUID::uid AS uid,
	NumOfPayment::Bdate AS Bdate,
	NumOfPayment::payment AS payment
;

--------------------------------------------------------------
--◆セッション数で足切りするための数値を取得
--------------------------------------------------------------
--------------------------------
--1回あたりの平均セッション時間
EdSess = FOREACH FilData GENERATE ISOtime, uid, cid;

Grp = GROUP EdSess BY uid;

addSession = FOREACH Grp { 
    ord = ORDER EdSess  BY ISOtime ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, SUBSTRING(ISOtime, 0, 10) AS date, ISOtime, session_id;

Grp = GROUP EditData BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER EditData  BY ISOtime ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.ISOtime)) AS session_time;
} 

sessionTime = FOREACH sessionTime GENERATE uid ,session_id, (session_time IS NULL ? 0: session_time) AS session_time;

GrpUid = GROUP sessionTime BY uid;  

aveDailySessionTime = FOREACH GrpUid{
	dis = DISTINCT sessionTime.session_id;
	GENERATE FLATTEN(group) AS uid,
 			COUNT(dis) AS CntSessId,
			AVG(sessionTime.session_time) AS ave_session_time;
}

--------------------------------------------------------------------------
--◆session回数が1のユーザを除いたユーザのZ値を取得する
--------------------------------------------------------------------------
--訪問日の整形----------------
JoinedZ01 = JOIN ResultZ01 BY uid LEFT OUTER,  aveDailySessionTime BY uid USING 'replicated';
Z01 = FOREACH JoinedZ01 GENERATE
	ResultZ01::uid AS uid,
	ResultZ01::Vdate AS Vdate,
	aveDailySessionTime::CntSessId AS CntSessId
;

FilZ01 = FILTER Z01 BY (int)CntSessId > 1;
ResultZ01 = FOREACH FilZ01 GENERATE uid, Vdate;

--購入日と額の整形----------------
JoinedZ03 = JOIN ResultZ03 BY uid LEFT OUTER,  aveDailySessionTime BY uid USING 'replicated';
Z03 = FOREACH JoinedZ03 GENERATE
	ResultZ03::uid AS uid,
	ResultZ03::Bdate AS Bdate,
	ResultZ03::payment AS payment,
	aveDailySessionTime::CntSessId AS CntSessId
;

FilZ03 = FILTER Z03 BY (int)CntSessId > 1;
ResultZ03 = FOREACH FilZ02 GENERATE uid,
			(Bdate IS NULL ? (chararray)'none': (chararray)Bdate) AS Bdate,
			(payment IS NULL ? (chararray)'none': (chararray)payment) AS payment,
;

--------------------------------------------------------------------------
--◆output
--------------------------------------------------------------------------
--Zのmatrix取得
STORE ResultZ01 INTO '$PATH_OUTPUT_Z01' USING PigStorage();
STORE ResultZ02 INTO '$PATH_OUTPUT_Z02' USING PigStorage();