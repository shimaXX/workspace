-----------------------------------------
--ãGêﬂïœìÆÇÃé¸ä˙ê´Çí≤Ç◊ÇÈÇΩÇﬂÇ…uidñàÇ…dailyÇ≈ÉAÉNÉeÉBÉrÉeÉBêîÇéÊìæÇ∑ÇÈ
--ZÇÕÉäÉXÉgâªÇµ1ïœêîÇ≤Ç∆Ç…Ç‹Ç∆ÇﬂÇÈ
--DëSÇƒÇÃïœêîÇuidñàÇ…éÊìæÇ∑ÇÈ
-----------------------------------------
--ïœêîÇ÷ÇÃäiî[
%declare TIME_WINDOW  30m

--äOïîUDFÇÃì«Ç›çûÇ›
REGISTER lib/datafu-0.0.4.jar

--UDFÇÃåƒÇ—èoÇµñºÇÃíËã`
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

--ì¸èoóÕÉpÉXÇÃíËã`
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/Mining/GalsterCPM_D_20130328';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--ëŒè€é“ÇÃçiÇËçûÇ›ÇçsÇ§
Edit = FOREACH RowData GENERATE SUBSTRING(time, 0, 10) AS date, uid, cid,
	GetPayment(ap) AS payment, verb, ISOFormat(time) AS ISOtime;
FilData = FILTER Edit BY cid == 2;

----------------------------------------------
--óàìXÇµÇΩÇ±Ç∆ÇÃÇ†ÇÈëSuidÇéÊìæ
Grp = GROUP FilData BY uid;
UUID = FOREACH Grp GENERATE FLATTEN(group) AS uid;

--------------------------------------------------------------
--ÅüÇ±Ç±Ç©ÇÁÇÕDÇÃéÊìæ
--------------------------------------------------------------
--------------------------------
--ïΩãœóàìXä‘äu
VisitIntervalDays = FOREACH Grp {
	ord = ORDER FilData BY date ASC;
	Idate = DISTINCT ord.date;
	GENERATE FLATTEN(group) AS uid, GetAverageInterval(Idate) As AvgDate; 
}

--------------------------------
--ïΩãœçwîÉä‘äu
FilBuyData = FILTER Edit BY verb == 'buy';
GrpBuy = GROUP FilBuyData BY uid;
BuyIntervalDays = FOREACH GrpBuy {
	ord = ORDER FilBuyData BY date ASC;
	Idate = DISTINCT ord.date;
	GENERATE FLATTEN(group) AS uid, GetAverageInterval(Idate) As AvgBuyDate; 
}

--------------------------------
--1çwì¸Ç†ÇΩÇËïΩãœçwîÉã‡äz
Fil = FILTER FilData BY verb=='buy';
GrpBuy = GROUP Fil BY uid;
GetPayment = FOREACH GrpBuy GENERATE FLATTEN(group) AS uid,
			 COUNT(Fil.verb) AS CntBuy, SUM(Fil.payment) AS SumPayment; 
AvePayment = FOREACH GetPayment GENERATE uid, (double)SumPayment/(double)CntBuy AS AvePayment;

--------------------------------
--óàñKì˙êîÇÃÉJÉEÉìÉg
Grp = GROUP FilData BY uid;
GetVdays = FOREACH Grp{
	ud = DISTINCT FilData.date;
	GENERATE FLATTEN(group) AS uid, COUNT(ud) AS CntVdays;
} 

--------------------------------
--1âÒÇ†ÇΩÇËÇÃïΩãœÉZÉbÉVÉáÉìéûä‘
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
--1âÒÇ†ÇΩÇËÇÃïΩãœè§ïiè⁄ç◊â{óóâÒêî
Fil = FILTER FilData BY verb=='article';
GrpArt = GROUP Fil BY uid;
GetVwArt = FOREACH GrpArt GENERATE FLATTEN(group) AS uid, COUNT(Fil.verb) AS CntArt; 

--------------------------------
--1âÒÇ†ÇΩÇËÇÃïΩãœåüçıâÒêî
Fil = FILTER FilData BY verb=='search';
GrpSrch = GROUP Fil BY uid;
GetVwSrch = FOREACH GrpSrch GENERATE FLATTEN(group) AS uid, COUNT(Fil.verb) AS CntSrch; 

---------------------------------
--DÇÃjoin
Joined01 = JOIN UUID BY uid LEFT OUTER,  VisitIntervalDays BY uid USING 'replicated';
D01 = FOREACH Joined01 GENERATE
	UUID::uid AS uid,
	VisitIntervalDays::AvgDate AS AvgDate
;

Joined02 = JOIN D01 BY uid LEFT OUTER,  AvePayment BY uid USING 'replicated';
D02 = FOREACH Joined02 GENERATE
	D01::uid AS uid,
	D01::AvgDate AS AvgDate,
	AvePayment::AvePayment AS AvePayment
;

Joined03 = JOIN D02 BY uid LEFT OUTER,  aveDailySessionTime BY uid USING 'replicated';
D03 = FOREACH Joined03 GENERATE
	D02::uid AS uid,
	D02::AvgDate AS AvgDate,
	D02::AvePayment AS AvePayment,
	aveDailySessionTime::CntSessId AS CntSessId,
	aveDailySessionTime::ave_session_time AS ave_session_time
;

Joined04 = JOIN D03 BY uid LEFT OUTER,  GetVwArt BY uid USING 'replicated';
D04 = FOREACH Joined04 GENERATE
	D03::uid AS uid,
	D03::AvgDate AS AvgDate,
	D03::AvePayment AS AvePayment,
	D03::CntSessId AS CntSessId,
	D03::ave_session_time AS ave_session_time,
	GetVwArt::CntArt AS CntArt
;

Joined05 = JOIN D04 BY uid LEFT OUTER,  BuyIntervalDays BY uid USING 'replicated';
D05 = FOREACH Joined05 GENERATE
	D04::uid AS uid,
	D04::AvgDate AS AvgDate,
	D04::AvePayment AS AvePayment,
	D04::CntSessId AS CntSessId,
	D04::ave_session_time AS ave_session_time,
	D04::CntArt AS CntArt,
	BuyIntervalDays::AvgBuyDate AS AvgBuyDate
;

Joined06 = JOIN D05 BY uid LEFT OUTER,  GetVwSrch BY uid USING 'replicated';
D06 = FOREACH Joined06 GENERATE
	D05::uid AS uid,
	D05::AvgDate AS AvgDate,
	D05::AvePayment AS AvePayment,
	D05::CntSessId AS CntSessId,
	D05::ave_session_time AS ave_session_time,
	D05::CntArt AS CntArt,
	D05::AvgBuyDate AS AvgBuyDate,
	GetVwSrch::CntSrch AS CntSrch
;

Joined07 = JOIN D06 BY uid LEFT OUTER,  GetVdays BY uid USING 'replicated';
D07 = FOREACH Joined07 GENERATE
	D06::uid AS uid,
	D06::AvgDate AS AvgDate,
	D06::AvePayment AS AvePayment,
	D06::CntSessId AS CntSessId,
	D06::ave_session_time AS ave_session_time,
	D06::CntArt AS CntArt,
	D06::AvgBuyDate AS AvgBuyDate,
	D06::CntSrch AS CntSrch,
	GetVdays::CntVdays As CntVdays
;

FilD07 = FILTER D07 BY (int)CntSessId > 1;

ResultD = FOREACH FilD07 GENERATE
	uid AS uid,
	(AvgDate IS NULL ? (DOUBLE)0: (double)AvgDate) AS AvgDate,
	(AvgBuyDate IS NULL ? (DOUBLE)0: (double)AvgBuyDate) AS AvgBuyDate,
	(AvePayment IS NULL ? 0: AvePayment) AS AvePayment,
	(ave_session_time IS NULL ? 0: ave_session_time) AS ave_session_time,
	(CntArt IS NULL ? 0: (double)CntArt/(double)CntSessId) As AvgArt,
	(CntSrch IS NULL ? 0: (double)CntSrch/(double)CntSessId) As AvgSrch,
	(CntSessId IS NULL ? 0: (double)CntSessId/(double)CntVdays) As AvgSess
;

--------------------------------------------------------------------------
--Åüoutput
--------------------------------------------------------------------------
--DÇÃmatrixéÊìæ
STORE ResultD INTO '$PATH_OUTPUT' USING PigStorage();