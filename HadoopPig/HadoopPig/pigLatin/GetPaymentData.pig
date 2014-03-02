-----------------------------------------
--�G�ߕϓ��̎������𒲂ׂ邽�߂�uid����daily�ŃA�N�e�B�r�e�B�����擾����
--Z�̓��X�g����1�ϐ����Ƃɂ܂Ƃ߂�
--D�S�Ă̕ϐ���uid���Ɏ擾����
-----------------------------------------
--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m

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
define GetIntervalDateInd myUDF.GetIntervalDateIndividuals();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();
define GetAverageInterval myUDF.GetAverageIntervalDays();

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT_BUYSPAN 'works/output/Mining/GalsterCPM_BuySpan_20130322';
%default PATH_OUTPUT_PYMENT 'works/output/Mining/GalsterCPM_PAYMENT_20130322';

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
--�w���z�̎擾
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
--�����������D�̎擾
--------------------------------------------------------------
--------------------------------
--���ύw���Ԋu
GrpBuy = GROUP FilBuyData BY uid;
BuyIntervalDays = FOREACH GrpBuy {
	ord = ORDER FilBuyData BY date ASC;
	Idate = DISTINCT ord.date;
	GENERATE FLATTEN(group) AS uid, GetAverageInterval(Idate) As AvgBuyDate; 
}

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
--1�񂠂���̕��ό�����
Fil = FILTER FilData BY verb=='search';
GrpSrch = GROUP Fil BY uid;
GetVwSrch = FOREACH GrpSrch GENERATE FLATTEN(group) AS uid, COUNT(Fil.verb) AS CntSrch; 

---------------------------------
--D��join
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
--�������܂ł�D�̒l���擾�B�ȉ���session�񐔂�1�̃��[�U�����������[�U��Z�l���擾����
--------------------------------------------------------------------------
--�w�����Ɗz�̐��`----------------
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
--��output
--------------------------------------------------------------------------
--Z��matrix�擾
STORE ResultZ01 INTO '$PATH_OUTPUT_PYMENT' USING PigStorage();

--D��matrix�擾
STORE ResultD INTO '$PATH_OUTPUT_BUYSPAN' USING PigStorage();