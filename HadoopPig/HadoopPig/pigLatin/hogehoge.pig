-----------------------------------------
--attribution���͂����邽�߂ɕK�v�ȃf�[�^�Z�b�g�̍\�z
--1:buy�܂ł̃m�[�h�ɍi��
--2:1�ɂ��āAbuy����̃m�[�h�͏���
--3:1�ɂ��āA�J��Ԃ�/��߂肵�Ă���m�[�h�͍폜���A�}�[�W����iUDF�ɂ��j
--4:�e�p�X�̒����i�[���j�����߂āA�����̕��U�����߂�
--5:�e�p�X�̊e�m�[�h�̋��N�����v�Z�i��Ńm�[�h�Ԃ̋������v�Z����̂Ɏg�p����j
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
%default PATH_INPUT_AWS 'works/input/aws/2012-12-15*';
%default PATH_OUTPUT_BUYSES 'works/output/GAMIFICATION/EvaTest0128';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionize�͐擪��time���K�v
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid, verb;

Fil = FILTER Edit BY uid == 'eva506ae557ab30b' AND time <= '2012-12-15T10:20:25Z' AND time >= '2012-12-15T09:30:00Z' AND cid == 3;

DUMP Fil;
