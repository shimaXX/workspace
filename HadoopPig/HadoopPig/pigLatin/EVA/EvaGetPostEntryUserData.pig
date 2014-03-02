------------------------------------------------
--Eva�̃����[�X�ɍ��킹��11/1�̑O���T�Ԃ�
--10/23�ȑO�ɍs������������A���A11/1�܂�entry���Ă��Ȃ����[�U��
--11/1�ȍ~�ɉ���o�^���Ă��郆�[�U
--��11/1�̑O��1�T�Ԃ̍s���f�[�^�𒲂ׂ�
------------------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m

%declare START_DATE  '2012-10-31' --�܂�11/1������̃f�[�^���擾����
%declare LAST_DATE  '2012-11-08' --�܂�7���܂ł̃f�[�^���擾����
%declare EXSTART_DATE  '2012-10-24' --�܂�10/25������̃f�[�^���擾����
%declare EXLAST_DATE  '2012-11-01' --�܂�10/31���܂ł̃f�[�^���擾����

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

--���o�̓p�X�̒�`
%default PATH_INPUT_UID 'works/input/EvaEntryUser.txt';
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/GAMIFICATION/EVA/GetEntryPostVerb1107';
%default PATH_OUTPUT_ACTION 'works/output/GAMIFICATION/Action1107';
%default PATH_OUTPUT_UNI_ACT 'works/output/GAMIFICATION/UniAct1107';

---------------------------------------
--sprocket�f�[�^�̎擾
RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

---------------------------------------
--�O��uid�f�[�^�̎擾
RowUidData = LOAD '$PATH_INPUT_UID' USING PigStorage() AS (
  uid:chararray)
;

--------------------------------------------
--sprocket�f�[�^�����H��uid����verb���J�E���g����
--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time, 0, 10) AS time;

--(3) EVA�ɍi��
FilteredData = FILTER EditData BY cid == 3 AND time > '$START_DATE' AND time < '$LAST_DATE';

--(4) �s�v�ȗ�icid�j���폜
EditData = FOREACH FilteredData GENERATE uid, verb;

--(5) uid��,verb���̏W�v
Grouped = GROUP FilteredData BY (uid, verb); 

Result = FOREACH Grouped { 
    verb_count = FilteredData.verb; 
    GENERATE FLATTEN(group) AS (uid,verb), COUNT(verb_count) AS verbCnt; 
} 

--�O��uid��join���A�Y�����[�U�݂̂ɍi��
joined = JOIN RowUidData BY uid LEFT OUTER, Result BY uid USING 'replicated' ; 

ResultFinal = FOREACH joined GENERATE 
	Result::uid AS uid,
	Result::verb AS verb,
	Result::verbCnt AS verbCnt
;

STORE ResultFinal INTO '$PATH_OUTPUT' using PigStorage('\t');