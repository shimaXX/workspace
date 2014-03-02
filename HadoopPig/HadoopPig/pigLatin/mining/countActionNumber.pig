------------------------------------
--1�Z�b�V����������̍s���񐔂̕��ς��Z�o������
------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-09' --�܂�08������̃f�[�^���擾����


--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategory myUDF.GetCategory();
define GetClient myUDF.GetClient();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();
define GetRewards myUDF.GetRewards();
define CountBadges myUDF.CountBadges();

--���o�̓p�X�̒�`
%default PATH_INPUT_OCT 'works/input/aws/';
%default PATH_OUTPUT 'works/output/TEST/EvaSeqBadg1209';

--(1)-2�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray,f6,rb:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, verb, cid, SUBSTRING(time,0,10) AS days, GetMetaInfo(verb, ap) AS meta, GetRewards(rb) AS badges;

--(3) ci-labo�ɍi��
FilteredData = FILTER EditData BY cid == 3 AND days > '$START_DATE';

--(4) �s�v�ȗ�icid�j���폜
EditData = FOREACH FilteredData GENERATE time, uid, meta, badges;


-----------------------------------------------------------
--(5) �Z�b�V����ID��U��
Grp = GROUP EditData BY uid;

addSession = FOREACH Grp { 
    ord = ORDER EditData BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

Grp = GROUP addSession BY (uid,session_id);

Result = FOREACH Grp {
	cnt = addSession.meta;
	t = addSession.time;
	badges = addSession.badges;
	GENERATE FLATTEN(group) AS (uid, session_id), (int)COUNT(cnt) AS actionCnt, MIN(t) AS minTime , CountBadges(badges) AS badges;
}

-------------------------------------------------
--session�񐔂�50�ȏ゠��uid���i����join�̑匳�ɂ���
Grp = GROUP addSession BY uid;

cntSession = FOREACH Grp {
	cnt = DISTINCT addSession.session_id;
	GENERATE FLATTEN(group) AS uid ,COUNT(cnt) AS sessionCnt;
}

Fil = FILTER cntSession BY sessionCnt >= 50;

UID = FOREACH Fil GENERATE uid;

Joined = JOIN UID BY uid LEFT OUTER, Result BY uid;

Outp = FOREACH Joined GENERATE
	$1 AS uid,
	$2 AS session_id,
	$3 AS actionCnt,
	$4 AS minTime,
	$5 AS badges
;

--LL = LIMIT Outp 10;
--DUMP LL;

Out = ORDER Outp BY minTime;

STORE Out INTO '$PATH_OUTPUT' USING PigStorage();