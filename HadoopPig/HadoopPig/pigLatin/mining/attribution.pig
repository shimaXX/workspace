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
%default PATH_INPUT_AWS 'works/input/aws/2012-12-1*';
%default PATH_OUTPUT_BUYSES 'works/output/GAMIFICATION/EvaTest0128';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionize�͐擪��time���K�v
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid, verb,GetClient(ap) AS client;

FilData = FILTER Edit BY cid == 3 AND time > '2012-11-12';

Grp = GROUP FilData BY uid;

addSession = FOREACH Grp { 
    ord = ORDER FilData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, verb, time, session_id;

FilBuy = FILTER EditData BY verb == 'buy';

joinedBuySession = JOIN FilBuy BY session_id LEFT OUTER, EditData BY session_id; 

Ed = FOREACH joinedBuySession GENERATE
	$0 AS uid,
	$6 AS time,
	$7 AS session_id,
	$5 AS verb,
	$2 AS buyTime
;

FilData = FILTER Ed BY time <= buyTime;

Ed = FOREACH FilData GENERATE time, session_id, verb, uid, buyTime;

Grp = GROUP Ed BY (uid, session_id);
MergeVerb = FOREACH Grp { 
    ord = ORDER Ed BY time ASC;
    GENERATE FLATTEN(group) AS (uid, session_id), MIN(Ed.buyTime) AS buyTime, MergeVerb(ord) AS verb;
} 

Result = FOREACH MergeVerb GENERATE uid, buyTime, verb;

STORE MergeVerb INTO '$PATH_OUTPUT_BUYSES' USING PigStorage('\t'); 