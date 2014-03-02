-----------------------------------------
--���ʐ��_���͂����邽�߂ɕK�v�ȃf�[�^�Z�b�g�̍\�z
--a���_���Ȃɂ��C�x���g������Ă��Ȃ�
--b���_��sprocket�����ƃL�����y�[���𓯎��ɍs�Ă��鎞��
--b���_�ɂ��āAEntry�������[�U��sprocket�Q�����[�U�Ƃ݂Ȃ��A
--Entry���Ă��Ȃ����[�U��sprocket�s�Q�����[�U�Ƃ݂Ȃ�
------�Ώۃ��[�U-----------
--a���_�W�v���ԑO��Entry�t���O���������[�U�݂̂�ΏۂƂ���
--�W�v����]���ϐ���session�񐔁Asession���ԁA���Ԗ������A�N�V������
-----------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-28' --�܂�29������̃f�[�^���擾����
%declare LAST_DATE  '2012-11-05' --�܂�4���܂ł̃f�[�^���擾����
%declare AXSTART_DATE  '2012-10-21' --�܂�22������̃f�[�^���擾����
%declare AXLAST_DATE  '2012-10-29' --�܂�28���܂ł̃f�[�^���擾����

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

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT 'works/output/Ming/TestData';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--�Ώێ҂̍i�荞�݂��s��
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS time, uid, cid, verb, GetClient(ap) AS client;
FilData = FILTER Edit BY cid == 3 AND time < '2012-11-01';

Ouid = FOREACH FilData GENERATE uid;
Grp = GROUP Ouid BY uid; 
Ouid = FOREACH Grp { 
	U = DISTINCT Ouid.uid;
	GENERATE FLATTEN(U) AS uid;
}

Fil = FILTER FilData BY verb=='entry' or verb=='mypage';

Grp = GROUP Fil BY uid;
CntEntry = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(Fil.verb) AS cntV;

--EntryFlag��t���邽�߂Ƀt����uid��entry���[�U����������
Joined = JOIN Ouid BY uid LEFT OUTER, CntEntry BY uid USING 'replicated';

--�K�v�ȕϐ��݂̂ɐ���
Edj = FOREACH Joined GENERATE 
	Ouid::uid AS uid,
	CntEntry::cntV AS cntV
;

--entryFlag��t����
Ed = FOREACH Edj GENERATE uid, (cntV IS NULL ? 0: 1) AS entFlag;

--entry���Ă��Ȃ����[�U�ɍi��
FF = FILTER Ed BY entFlag==0;

--entry���Ă��Ȃ����[�U��uid�����̃e�[�u�����擾
POU = FOREACH FF GENERATE uid;

--���K���1�T�Ԉȏ�o�߂����̐l�Ԃɍi�邽�߂�uid���擾
Filed = FILTER Edit BY cid == 3 AND time < '2012-10-25';
Grp = GROUP FilData BY uid;
UU = FOREACH Grp { 
	U = DISTINCT FilData.uid;
	GENERATE FLATTEN(U) AS uid;
}

--���K���1�T�Ԉȏ�o�߂����̐l�Ԃ݂̂ɍi��
JoinedOU = JOIN UU BY uid, POU BY uid USING 'replicated';

OUR = FOREACH JoinedOU GENERATE UU::uid AS uid;


--------------------------------------
--�C�x���g�O1�T�Ԃ̃f�[�^�擾
FilPre = FILTER Edit BY cid == 3 AND time < '2012-11-01' AND time > '2012-10-24';

Grp = GROUP FilPre BY uid;
CntVerbPre = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPre.verb) AS cntV;

ResultPre = FOREACH CntVerbPre GENERATE uid, cntV, (uid IS NULL ? 0: 0) as Delta;


--------------------------------------
--�C�x���g��1�T�Ԃ̃f�[�^�擾
FilPro = FILTER Edit BY cid == 3 AND time >= '2012-11-01' AND time < '2012-11-08';

Grp = GROUP FilPro BY uid;
CntVerbPro = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPro.verb) AS cntV;

EntryUsr = FILTER FilPro BY verb=='entry';
JoinedPro = JOIN CntVerbPro BY uid LEFT OUTER, EntryUsr BY uid USING 'replicated';

EdPro = FOREACH JoinedPro GENERATE
	CntVerbPro::uid AS uid,
	CntVerbPro::cntV AS cntV,
	EntryUsr::verb AS entFlag
;

ResultPro = FOREACH EdPro GENERATE uid, cntV, (entFlag IS NULL ? 0 : 1) AS Z,  (uid IS NULL ? 1 : 1) AS Delta;


----------------------------------------
--join
JoinedRePre = JOIN OUR BY uid, ResultPre BY uid USING 'replicated';
JoinedRePro = JOIN OUR BY uid, ResultPro BY uid USING 'replicated';

Jpre = FOREACH JoinedRePre GENERATE
	OUR::uid AS uid,
	ResultPre::cntV AS cntVPre,
	ResultPre::Delta AS DeltaPre
;

Jpro = FOREACH JoinedRePro GENERATE
	OUR::uid AS uid,
	ResultPro::cntV AS cntVPro,
	ResultPro::Z AS Z,
	ResultPro::Delta AS DeltaPro
;

JoinedRe = JOIN Jpre BY uid, Jpro BY uid USING 'replicated';

Result = FOREACH JoinedRe GENERATE
	Jpre::uid AS uid,
	Jpre::cntVPre AS cntVPre,
	Jpro::cntVPro AS cntVPro,
	Jpro::Z AS Z,
	Jpre::DeltaPre AS DeltaPre,
	Jpro::DeltaPro AS DeltaPro
;

STORE Result INTO '$PATH_OUTPUT' USING PigStorage('\t'); 