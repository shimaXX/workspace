-----------------------------------------
--�G�ߕϓ��̎������𒲂ׂ邽�߂�uid����daily�ŃA�N�e�B�r�e�B�����擾����
--Z�̓��X�g����1�ϐ����Ƃɂ܂Ƃ߂�
--D�S�Ă̕ϐ���uid���Ɏ擾����
-----------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-12-18'--'2012-12-18'
%declare LAST_DATE  '2013-02-04'--'2013-02-04'
%declare AXSTART_DATE  '2012-10-21'
%declare AXLAST_DATE  '2012-10-29'

--�������߂̃p�����^
%declare BOUND  '13000'
%declare DAYS_BOUND '120' 

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
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

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT_D 'works/output/Mining/GalsterCPM_D_20130322';
%default PATH_OUTPUT_Z01 'works/output/Mining/GalsterCPM_Z01_20130322';
%default PATH_OUTPUT_Z02 'works/output/Mining/GalsterCPM_Z02_20130322';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--�Ώێ҂̍i�荞�݂��s��
Edit = FOREACH RowData GENERATE SUBSTRING(time, 0, 10) AS date, uid, cid,
	GetPayment(ap) AS payment, verb, ISOFormat(time) AS ISOtime;
FilData = FILTER Edit BY cid == 2;

----------------------------------------------
--���X�������Ƃ̂���Suid���擾
Grp = GROUP FilData BY uid;
UUID = FOREACH Grp GENERATE FLATTEN(group) AS uid;

--------------------------------
--�O�񗈓X����̓����̑ΐ��̎擾
GrpDate = GROUP FilData BY (uid, date);
VisitDate = FOREACH GrpDate	GENERATE FLATTEN(group) AS (uid, Vdate);

joinedZ01 = JOIN UUID BY uid LEFT OUTER, VisitDate BY uid USING 'replicated';
ResultZ01 = FOREACH joinedZ01 GENERATE
	UUID::uid AS uid,
	VisitDate::Vdate AS Vdate
;

--------------------------------
--�O��w������̓����̑ΐ��̎擾
--FilBuyData = FILTER Edit BY verb == 'buy';
--GrpDate = GROUP FilBuyData BY (uid, date);
--BuyDate = FOREACH GrpDate GENERATE FLATTEN(group) AS (uid, Bdate);

--joinedZ02 = JOIN UUID BY uid LEFT OUTER, BuyDate BY uid USING 'replicated';
--ResultZ02 = FOREACH joinedZ02 GENERATE
--	UUID::uid AS uid,
--	BuyDate::Bdate AS Bdate
--;

--------------------------------
--�w���z�̎擾
FilBuyData = FILTER Edit BY verb == 'buy';
GrpDate = GROUP FilBuyData BY (uid, date);
NumOfPayment = FOREACH GrpDate GENERATE FLATTEN(group) AS (uid, Bdate), SUM((int)FilBuyData.payment) AS payment;

joinedZ03 = JOIN UUID BY uid LEFT OUTER, BuyDate BY uid USING 'replicated';
ResultZ03 = FOREACH joinedZ03 GENERATE
	UUID::uid AS uid,
	NumOfPayment::Bdate AS Bdate,
	NumOfPayment::payment AS payment
;

--------------------------------
--�C�x���g�̗L���̎擾


--------------------------------
--�l�����̗L��



--------------------------------------------------------------
--�����������D�̎擾
--------------------------------------------------------------
--------------------------------
--���ϗ��X�Ԋu
VisitIntervalDays = FOREACH Grp {
	ord = ORDER FilData BY date ASC;
	Idate = DISTINCT ord.date;
	GENERATE FLATTEN(group) AS uid, GetAverageInterval(Idate) As AvgDate; 
}

--------------------------------
--���ύw���Ԋu
GrpBuy = GROUP FilBuyData BY uid;
BuyIntervalDays = FOREACH GrpBuy {
	ord = ORDER FilBuyData BY date ASC;
	Idate = DISTINCT ord.date;
	GENERATE FLATTEN(group) AS uid, GetAverageInterval(Idate) As AvgBuyDate; 
}

--------------------------------
--1�w�������蕽�ύw�����z
Fil = FILTER FilData BY verb=='buy';
GrpBuy = GROUP Fil BY uid;
GetPayment = FOREACH GrpBuy GENERATE FLATTEN(group) AS uid,
			 COUNT(Fil.verb) AS CntBuy, SUM(Fil.payment) AS SumPayment; 
AvePayment = FOREACH GetPayment GENERATE uid, (double)SumPayment/(double)CntBuy AS AvePayment;

--------------------------------
--1�񂠂���̕��σZ�b�V��������
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
--1�񂠂���̕��Ϗ��i�ڍ׉{����
Fil = FILTER FilData BY verb=='article';
GrpArt = GROUP Fil BY uid;
GetVwArt = FOREACH GrpArt GENERATE FLATTEN(group) AS uid, COUNT(Fil.verb) AS CntArt; 

--------------------------------
--1�񂠂���̕��ό�����
Fil = FILTER FilData BY verb=='search';
GrpSrch = GROUP Fil BY uid;
GetVwSrch = FOREACH GrpSrch GENERATE FLATTEN(group) AS uid, COUNT(Fil.verb) AS CntSrch; 

---------------------------------
--D��join
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

FilD06 = FILTER D06 BY (int)CntSessId > 1;

ResultD = FOREACH FilD06 GENERATE
	uid AS uid,
	(AvgDate IS NULL ? (DOUBLE)0: (double)AvgDate) AS AvgDate,
	(AvgBuyDate IS NULL ? (DOUBLE)0: (double)AvgBuyDate) AS AvgBuyDate,
	(AvePayment IS NULL ? 0: AvePayment) AS AvePayment,
	(ave_session_time IS NULL ? 0: ave_session_time) AS ave_session_time,
	(CntArt IS NULL ? 0: (double)CntArt/(double)CntSessId) As AvgArt,
	(CntSrch IS NULL ? 0: (double)CntSrch/(double)CntSessId) As AvgSrch	
;

--------------------------------------------------------------------------
--�������܂ł�D�̒l���擾�B�ȉ���session�񐔂�1�̃��[�U�����������[�U��Z�l���擾����
--------------------------------------------------------------------------
--�K����̐��`----------------
JoinedZ01 = JOIN ResultZ01 BY uid LEFT OUTER,  aveDailySessionTime BY uid USING 'replicated';
Z01 = FOREACH JoinedZ01 GENERATE
	ResultZ01::uid AS uid,
	ResultZ01::Vdate AS Vdate,
	aveDailySessionTime::CntSessId AS CntSessId
;

FilZ01 = FILTER Z01 BY (int)CntSessId > 1;
ResultZ01 = FOREACH FilZ01 GENERATE uid, Vdate;

--�w�����̐��`----------------
--JoinedZ02 = JOIN ResultZ02 BY uid LEFT OUTER,  aveDailySessionTime BY uid USING 'replicated';
--Z02 = FOREACH JoinedZ02 GENERATE
--	ResultZ02::uid AS uid,
--	ResultZ02::Bdate AS Bdate,
--	aveDailySessionTime::CntSessId AS CntSessId
--;

--FilZ02 = FILTER Z02 BY (int)CntSessId > 1;
--ResultZ02 = FOREACH FilZ02 GENERATE uid, (Bdate IS NULL ? (chararray)'none': (chararray)Bdate) AS Bdate;

--�w�����Ɗz�̐��`----------------
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
--��output
--------------------------------------------------------------------------
--Z��matrix�擾
STORE ResultZ01 INTO '$PATH_OUTPUT_Z01' USING PigStorage();
STORE ResultZ02 INTO '$PATH_OUTPUT_Z02' USING PigStorage();

--D��matrix�擾
STORE ResultD INTO '$PATH_OUTPUT_D' USING PigStorage();