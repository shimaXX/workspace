--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT_TYPE 'works/input/EVAtypeonlyPU.csv';
%default PATH_INPUT_OCT 'works/input/aws/2012-11-*gz';
%default PATH_OUTPUT 'works/output/EVA/Transe1114Search';


--(1)-2�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(1)-3�f�[�^�̑Ή��t���@type��uid�݂̂̃f�[�^
RowTypeData = LOAD '$PATH_INPUT_TYPE' USING PigStorage(',') AS (
  uid:chararray,type:chararray)
;

--(2)input data�̕ϐ��̑I��
EditData = FOREACH RowData GENERATE ISOFormat(time) AS time , uid, verb, cid, GetClient(ap) AS client;

--(3)�t�B���^�[����
FilData = FILTER EditData BY (cid == 3) AND (SUBSTRING(time, 0, 10) > '2012-10-31');
FilTypeData = FILTER RowTypeData BY type != '';

--(4) �f�[�^��union
--FiledData = UNION FilSepData , FilOctData;

--(5) ���ɂȂ�f�[�^��Type�f�[�^��join
JoinedData = JOIN FilData BY uid LEFT OUTER, FilTypeData By uid;

--(6) join��̕ϐ��̑I��
PicOutData = FOREACH JoinedData GENERATE 
	FilData::time AS time,
	FilData::uid AS uid,
	FilData::verb AS verb,
	FilTypeData::type AS type
;

--(7) join���ꂽ�f�[�^��type���U���Ă��Ȃ����[�U���폜�F
--�w������������A�s���񐔂�2��ȏ゠��A�w�肵��4�̍s���񐔂ɍ������������
--FixedData = FILTER PicOutData BY type != '';
--FixedData = FILTER PicOutData BY type == 'new';
FixedData = FILTER PicOutData BY type == 'search';
--FixedData = FILTER PicOutData BY type == 'comment';
--FixedData = FILTER PicOutData BY type == 'category';


--(8) �O���[�v��(time,type,verb)
Grouped = GROUP FixedData BY (uid); 

Result = FOREACH Grouped { 
    ord = ORDER FixedData BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

Result02 = FOREACH Result GENERATE uid AS uid, verb AS verb, time AS time, session_id AS session_id;

Grouped = GROUP Result02 BY session_id;

Result03 = FOREACH Grouped { 
    ord02 = ORDER Result02  BY time ASC;
    GENERATE FLATTEN(JuxtaposeNextVerb(ord02));
} 

--�����܂łŊe���[�U����lastVerb��postVerb�̐��`�͏I��
Result04 = FILTER Result03 BY postVerb != '';

--------------------------------------------------
Grouped = GROUP Result04 BY (verb, postVerb);

Result05 = FOREACH Grouped { 
    cnt = Result04.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS cnt;
} 

STORE Result05 INTO '$PATH_OUTPUT' using PigStorage('\t');