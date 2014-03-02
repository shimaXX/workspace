-----------------------------------------
--attribution���͂����邽�߂ɕK�v�ȃf�[�^�Z�b�g�̍\�z
--1:session���ɌJ��Ԃ��A�߂�{�^���Ŗ߂����y�[�W���폜����
--2:verb�̐���Ȃ��ŃJ�E���g���s��
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
define MergeVerbRespectively myUDF.MergeVerbRespectively();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT 'works/output/Mining/Ci-LaboTranseVerb0123';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionize�͐擪��time���K�v
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid, GetMetaInfo(verb,ap) AS verb;

FilData = FILTER Edit BY (cid == 8 OR cid == 7)
					AND SUBSTRING(time,0,10) > '2012-12-15';

Grp = GROUP FilData BY uid;

addSession = FOREACH Grp { 
    ord = ORDER FilData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

Ed = FOREACH addSession GENERATE uid, verb, time, session_id;

Grp = GROUP Ed BY session_id;

MergeVerb = FOREACH Grp { 
    ord = ORDER Ed BY time ASC;
    GENERATE FLATTEN(MergeVerbRespectively(ord));
} 

Grouped = GROUP MergeVerb BY session_id;

Result03 = FOREACH Grouped { 
    ord02 = ORDER MergeVerb  BY time ASC;
    GENERATE FLATTEN(JuxtaposeNextVerb(ord02));
} 

--�����܂łŊe���[�U����lastVerb��postVerb�̐��`�͏I��
Result04 = FILTER Result03 BY postVerb != '';

Grouped = GROUP Result04 BY (verb, postVerb);

Result05 = FOREACH Grouped { 
    cnt = Result04.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS cnt;
} 

STORE Result05 INTO '$PATH_OUTPUT' USING PigStorage('\t'); 