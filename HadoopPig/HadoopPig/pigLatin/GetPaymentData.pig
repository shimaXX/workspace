-----------------------------------------
--季節変動の周期性を調べるためにuid毎にdailyでアクティビティ数を取得する
--Zはリスト化し1変数ごとにまとめる
--D全ての変数をuid毎に取得する
-----------------------------------------
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
define GetPayment myUDF.GetPayment();
define GetCategory myUDF.GetCategory();
define GetNewflag myUDF.GetNewflag();
define GetReservationflag myUDF.GetReservationflag(); 
define GetNextDate myUDF.GetNextDate();
define GetSessionTime myUDF.GetSessionTime();
define MergeVerb myUDF.MergeVerb();
define GetIntervalDateInd myUDF.GetIntervalDateIndividuals();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();
define GetAverageInterval myUDF.GetAverageIntervalDays();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT_BUYSPAN 'works/output/Mining/GalsterCPM_BuySpan_20130322';
%default PATH_OUTPUT_PYMENT 'works/output/Mining/GalsterCPM_PAYMENT_20130322';

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
--購買額の取得
FilBuyData = FILTER Edit BY verb == 'buy';
GrpDate = GROUP FilBuyData BY (uid, date);
NumOfPayment = FOREACH GrpDate GENERATE FLATTEN(group) AS (uid, Bdate), SUM(FilBuyData.payment) AS payment;

joinedZ01 = JOIN UUID BY uid LEFT OUTER, NumOfPayment BY uid USING 'replicated';
ResultZ01 = FOREACH joinedZ01 GENERATE
	UUID::uid AS uid,
	NumOfPayment::Bdate AS Bdate,
	NumOfPayment::payment AS payment
;

ResultZ01 = FOREACH ResultZ01 GENERATE
	uid AS uid,
	(Bdate IS NULL ? (chararray)'none' : (chararray)Bdate) AS Bdate,
	(Bdate IS NULL ? (chararray)'none' : (chararray)payment) AS payment
;

--------------------------------------------------------------
--◆ここからはDの取得
--------------------------------------------------------------
--------------------------------
--平均購買間隔
GrpBuy = GROUP FilBuyData BY uid;
BuyIntervalDays = FOREACH GrpBuy {
	ord = ORDER FilBuyData BY date ASC;
	Idate = DISTINCT ord.date;
	GENERATE FLATTEN(group) AS uid, GetAverageInterval(Idate) As AvgBuyDate; 
}

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

--------------------------------
--1回あたりの平均検索回数
Fil = FILTER FilData BY verb=='search';
GrpSrch = GROUP Fil BY uid;
GetVwSrch = FOREACH GrpSrch GENERATE FLATTEN(group) AS uid, COUNT(Fil.verb) AS CntSrch; 

---------------------------------
--Dのjoin
Joined01 = JOIN aveDailySessionTime BY uid LEFT OUTER,  GetVwSrch BY uid USING 'replicated';
D01 = FOREACH Joined01 GENERATE
	aveDailySessionTime::uid AS uid,
	aveDailySessionTime::CntSessId AS CntSessId,
	GetVwSrch::CntSrch AS CntSrch
;

Joined02 = JOIN D01 BY uid LEFT OUTER,  BuyIntervalDays BY uid USING 'replicated';
D02 = FOREACH Joined02 GENERATE
	D01::uid AS uid,
	D01::CntSessId AS CntSessId,
	D01::CntSrch AS CntSrch,
	BuyIntervalDays::AvgBuyDate AS AvgBuyDate
;

FilD02 = FILTER D02 BY (int)CntSessId > 1;

ResultD = FOREACH FilD02 GENERATE
	uid AS uid,
	(CntSrch IS NULL ? 0: (double)CntSrch/(double)CntSessId) As AvgSrch,
	(AvgBuyDate IS NULL ? 999: (double)AvgBuyDate) As AvgBuyDate
;

--------------------------------------------------------------------------
--◆ここまででDの値を取得。以下でsession回数が1のユーザを除いたユーザのZ値を取得する
--------------------------------------------------------------------------
--購入日と額の整形----------------
JoinedZ01 = JOIN ResultZ01 BY uid LEFT OUTER,  aveDailySessionTime BY uid USING 'replicated';
Z01 = FOREACH JoinedZ01 GENERATE
	ResultZ01::uid AS uid,
	ResultZ01::Bdate AS Bdate,
	ResultZ01::payment AS payment,
	aveDailySessionTime::CntSessId AS CntSessId
;

FilZ01 = FILTER Z01 BY (int)CntSessId > 1;
ResultZ01 = FOREACH FilZ01 GENERATE uid,
			(Bdate IS NULL ? (chararray)'none': (chararray)Bdate) AS Bdate,
			(payment IS NULL ? (chararray)'none': (chararray)payment) AS payment
;

--------------------------------------------------------------------------
--◆output
--------------------------------------------------------------------------
--Zのmatrix取得
STORE ResultZ01 INTO '$PATH_OUTPUT_PYMENT' USING PigStorage();

--Dのmatrix取得
STORE ResultD INTO '$PATH_OUTPUT_BUYSPAN' USING PigStorage();