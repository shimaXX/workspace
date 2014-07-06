----------------------------------------------------
--sprocket�����O�̉����verb�̐��𓱓���̐��Ɣ�r����
--sprocket�����O�ɉ�����������[�U�̂ݎ���Ă���
----------------------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-31' --�܂�11/1������̃f�[�^���擾����
%declare LAST_DATE  '2012-11-05' --�܂�4���܂ł̃f�[�^���擾����
%declare EXSTART_DATE  '2012-10-09' --�܂�10������̃f�[�^���擾����
%declare EXLAST_DATE  '2012-10-25' --�܂�24���܂ł̃f�[�^���擾����

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
%default PATH_OUTPUT_OLDUSER 'works/output/GAMIFICATION/oldUserTEST';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionize�͐擪��time���K�v
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS days, uid, cid, verb;

-----------------------------------------------------
--�܂���join�̌��ƂȂ�e�[�u�����쐬����
--EVA�̂݁A10/10�ȍ~�A10/31�܂łɉ���ɍi��ilogin, entry, mypage�j
FilData = FILTER Edit BY cid == 3 AND days > '$EXSTART_DATE' AND days < '$EXLAST_DATE'
	AND (verb == 'login' OR verb == 'entry' OR verb == 'mypage');  

Grp = GROUP FilData BY (uid);

--join�̌��ƂȂ�uid�e�[�u��
ResultOrg = FOREACH Grp { 
    GENERATE FLATTEN(group) AS uid; 
} 

-----------------------------------------------------------
--EVA�̂݁A10/10�ȍ~�̉���̃A�N�e�B�r�e�B���擾
FilData = FILTER Edit BY cid == 3 AND days > '$EXSTART_DATE';  

Grp = GROUP FilData BY (uid, days,verb);

--join����e�[�u��
ResultEX = FOREACH Grp { 
    cntVerb = FilData.verb;
    GENERATE FLATTEN(group) AS (uid, days, verb), COUNT(cntVerb) AS cntVerb; 
} 

-----------------------------------------------------------
--EVA�̂݁A10/10�ȍ~�̉����DAU���擾
joinedData = JOIN ResultOrg BY uid LEFT OUTER , FilData BY uid USING 'replicated';

TMP = FOREACH joinedData GENERATE 
	FilData::uid AS uid,
	FilData::days AS days	
;

Grp = GROUP TMP BY (days);

--join����e�[�u��
ResultDAU = FOREACH Grp { 
    UU = DISTINCT TMP.uid;
    GENERATE FLATTEN(group) AS days, COUNT(UU) AS DAU; 
} 

----------------------------------------------------
--���������join
joined = JOIN ResultOrg BY uid LEFT OUTER,ResultEX BY uid USING 'replicated';

--�K�v��column�����擾
Prior = FOREACH joined GENERATE
	ResultEX::uid AS uid,
	ResultEX::days AS days,
	ResultEX::verb AS verb,
	ResultEX::cntVerb AS cntVerb
;

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

STORE Result INTO '$PATH_OUTPUT_OLDUSER' USING PigStorage('\t');