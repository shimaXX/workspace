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
%default PATH_OUTPUT_OLDUSER 'works/output/GAMIFICATION/test';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

EditData = FOREACH RowData GENERATE
	uid, cid, verb, SUBSTRING(time, 0, 10) AS days;

FilteredData = FILTER EditData BY (cid == 3) AND (days > '$EXSTART_DATE') AND uid == 'eva506a48daae05e';

---------------------------------
--�A�N�e�B�r�e�B���̎擾_try
GrpVerb = GROUP FilteredData BY (days);

ResultVerb = FOREACH GrpVerb { 
    cntVerb = FilteredData.verb;
    GENERATE FLATTEN(group) AS days, COUNT(cntVerb) AS cntDailyVerb; 
} 

STORE ResultVerb INTO '$PATH_OUTPUT_OLDUSER' USING PigStorage('\t');