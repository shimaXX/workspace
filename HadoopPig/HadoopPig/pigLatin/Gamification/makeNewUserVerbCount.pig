----------------------------------------------------
--sprocket�����O�̉����verb�̐��𓱓���̐��Ɣ�r����
--sprocket������ɃA�N�V�������J�n�������[�U�݂̂��E���Ă���
----------------------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-31' --�܂�11/1������̃f�[�^���擾����
%declare EXSTART_DATE  '2012-10-09' --�܂�10/9������̃f�[�^���擾����

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

--���o�̓p�X�̒�`
--%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT_NEWUSER 'works/output/GAMIFICATION/newUser';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionize�͐擪��time���K�v
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS days, uid, cid, verb;

--Eva��11/1����̃f�[�^�ɍi��
FilData = FILTER Edit BY cid == 3 AND days > '$EXSTART_DATE';

--���ꂼ���user�̍s�����̍ŏ��l�����߂邽�߂�uid�ŃO���[�v��
Grp = GROUP FilData BY uid;

--���ꂼ���user�̍s�����̍ŏ��l�����߂�
getMinDate = FOREACH Grp {
	date = FilData.days;
	GENERATE FLATTEN(group) AS uid, MIN(date) AS minDate;
}

---------------------------------
--join���̃f�[�^�����i���ʂ�verb���J�E���g����j
Grp = GROUP FilData BY (uid, days, verb);

getData = FOREACH Grp {
	verb = FilData.verb;
	GENERATE FLATTEN(group) AS (uid, days, verb), COUNT(verb) AS cntVerb;
}

-----------------------------------------------------------
--EVA�̂݁A11/1�ȍ~��DAU���擾
FilData = FILTER Edit BY cid == 3 AND days > '$EXSTART_DATE';  

joined = JOIN FilData BY uid LEFT OUTER , getMinDate BY uid USING 'replicated'; 

TMP = FOREACH joined GENERATE 
	FilData::uid AS uid,
	FilData::days AS days,
	getMinDate::minDate AS minDate
;

FilData = FILTER TMP BY minDate > '$START_DATE';

Grp = GROUP FilData BY (days);

--join����e�[�u��
ResultDAU = FOREACH Grp { 
    UU = DISTINCT FilData.uid;
    GENERATE FLATTEN(group) AS days, COUNT(UU) AS DAU; 
} 

------------------------------------
--���������join����
joinedData = JOIN getData BY uid, getMinDate BY uid USING 'replicated';

TMP = FOREACH joinedData GENERATE
	getData::uid AS uid,
	getData::days AS days,
	getData::verb AS verb,
	getData::cntVerb AS cntVerb,
	getMinDate::minDate AS minDate
;

FilData = FILTER TMP BY minDate > '$START_DATE';

Prior = FOREACH FilData GENERATE uid, days, verb, cntVerb;

Grp  = GROUP Prior BY (days,verb);

--date,verb���̏W�v���s��
ResultVerb = FOREACH Grp {
	sVerb = Prior.cntVerb;
	GENERATE FLATTEN(group) AS (days, verb), FLATTEN(SUM(sVerb)) AS sumVerb;
}

---------------------------------
--DAU��join�����ϒl�����߂�
joined = JOIN ResultVerb BY days ,ResultDAU BY days USING 'replicated';

--�K�v��column�����擾
Prior = FOREACH joined GENERATE
	ResultVerb::days AS days,
	ResultVerb::verb AS verb,
	ResultVerb::sumVerb AS sumVerb,
	ResultDAU::DAU AS DAU
;

--calculate average count of verbs
Result = FOREACH Prior GENERATE days, verb, sumVerb, DAU,(double)((double)sumVerb/(double)DAU) AS avgVerb;

STORE Result INTO '$PATH_OUTPUT_NEWUSER' USING PigStorage('\t'); 