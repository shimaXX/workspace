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
%default PATH_OUTPUT_Z01 'works/output/Mining/GalsterCPM_Z01_20130327';
%default PATH_OUTPUT_Z02 'works/output/Mining/GalsterCPM_Z02_20130327';

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

--------------------------------------------------------------
--���Z�b�V�������ő��؂肷�邽�߂̐��l���擾
--------------------------------------------------------------
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

--------------------------------------------------------------------------
--��session�񐔂�1�̃��[�U�����������[�U��Z�l���擾����
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