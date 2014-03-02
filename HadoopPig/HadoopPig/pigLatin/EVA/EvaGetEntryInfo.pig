----------------------------------------------------
--sprocket�����O�̉����verb�̐��𓱓���̐��Ɣ�r����
--sprocket������ɃA�N�V�������J�n�������[�U�݂̂��E���Ă���
----------------------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare OCT_START_DATE  '2012-10-01' --�܂�10/1������̃f�[�^���擾����
%declare NOV_START_DATE  '2012-10-31' --�܂�11/1������̃f�[�^���擾����
%declare DEC_START_DATE  '2012-11-30' --�܂�12/1������̃f�[�^���擾����

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
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT_NEWUSER 'works/output/GAMIFICATION/newUser';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionize�͐擪��time���K�v
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS days, uid, cid, verb;

--Eva�Ŋe���̃f�[�^�ɍi��
Data = FILTER Edit BY cid == 3 AND days > '$OCT_START_DATE';

--�e���̃f�[�^��month�̃J������ǉ�
Data = FOREACH Data GENERATE days, uid, cid, verb, SUBSTRING(days,0,7) AS month;

--------------------------------------------
--�e����UU���J�E���g����
UUgrp = GROUP Data BY month;
UU = FOREACH UUgrp{
	u = DISTINCT Data.uid;
	GENERATE FLATTEN(group) AS month, (int)COUNT(u) AS MUU; 
}

------------------------------------------------
--�������
--������ƐV�K�����login��entry�̗��������邩�A�������Ŕ��f
--1 login�̂��郆�[�U�݂̂ɍi��i���ƐV�̗��҂����݂���j
--2 entry�̂��郆�[�U�݂̂ɍi��i�V�݂̂ɂȂ�j
--3 join���ăJ�������󂩂ǂ����Ŕ��f

--login���[�U���i��
Login = FILTER Data BY verb == 'login';

--entry���[�U���i��
Entry = FILTER Data BY verb == 'entry';

----------------
--join
Joined = JOIN Login BY uid LEFT OUTER, Entry BY uid USING 'replicated';

--�f�[�^�̐��`
Res = FOREACH Joined GENERATE
	Login::uid AS uid,
	Login::days AS loginDay,
	Login::month  AS month,
	Entry::days  AS entryDay
;

---------------
--entryDay��filter�ł��Ȃ��̂�flag�𗧂Ă�
Grp = GROUP Res BY uid;
addFlagRes = FOREACH Grp GENERATE FLATTEN(group) AS uid, FLATTEN(Res.loginDay) AS loginDay, 
					FLATTEN(Res.entryDay) AS entryDay, FLATTEN(Res.month) AS month, (int)COUNT(Res.entryDay) AS entryFlag;


---------------------------------------------------------
--����������J�E���g����
--UU�����������������āA����o�^���̕�������
FilPrvEntry = FILTER addFlagRes BY entryFlag == 0;

Grp = GROUP FilPrvEntry BY month;
CntPrvEntUU = FOREACH Grp{
	uu = DISTINCT FilPrvEntry.uid;
	GENERATE FLATTEN(group) AS month, (int)COUNT(uu) AS cntPrvEntUU;
}

------------------------------------------------------------
--�V�K��������Z�o
FilNewEntry = FILTER addFlagRes BY entryFlag != 0;

Grp = GROUP FilNewEntry BY month;
CntNewEntUU = FOREACH Grp{
	uu = DISTINCT FilNewEntry.uid;
	GENERATE FLATTEN(group) AS month, (int)COUNT(uu) AS cntNewEntUU;
}

----------------------------------------------------------
--�e����UU�Ɗ�������A�V�K�������join����
--UU�Ɗ��������join :A
--A�ƐV�K���������join

Joined01 = JOIN UU BY month, CntPrvEntUU BY month USING 'replicated';
Result01 = FOREACH Joined01 GENERATE
	UU::month AS month,
	UU::MUU AS MUU,
	CntPrvEntUU::cntPrvEntUU AS cntPrvEntUU
;

Joined02 = JOIN Result01 BY month, CntNewEntUU BY month USING 'replicated';
Result02 = FOREACH Joined02 GENERATE
	Result01::month AS month,
	Result01::MUU AS MUU,
	Result01::cntPrvEntUU AS cntPrvEntUU,
	CntNewEntUU::cntNewEntUU AS cntNewEntUU
;

LL = LIMIT Result02 10;
DUMP LL;

--STORE Result INTO '$PATH_OUTPUT_NEWUSER' USING PigStorage('\t'); 