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
--%default PATH_INPUT_TYPE 'works/input/typeonlyPU.csv';
--%default PATH_INPUT_ORIG 'works/input/log_queue_activities_20120*xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/oct/';
%default PATH_OUTPUT 'works/output/Transe1025';


--(1)-2�f�[�^�̑Ή��t���@10��
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(1)-3�f�[�^�̑Ή��t���@type��uid�݂̂̃f�[�^
--RowTypeData = LOAD '$PATH_INPUT_TYPE' USING PigStorage(',') AS (
--  uid:chararray,type:chararray)
--;

--(2)input data�̕ϐ��̑I��
OctData = FOREACH RowOctData GENERATE ISOFormat(time) AS time , uid, verb, cid, GetClient(ap) AS client;

--(3)�t�B���^�[����
FilOctData = FILTER OctData BY (cid == 2) AND (SUBSTRING(time, 0, 10) >= '2012-10-18') AND (SUBSTRING(time, 0, 10) < '2012-10-25') AND (client == 'sp');
--FilTypeData = FILTER RowTypeData BY type != '';

--(4) �f�[�^��union
--FiledData = UNION FilSepData , FilOctData;

--(5) ���ɂȂ�f�[�^��Type�f�[�^��join
--JoinedData = JOIN FiledData BY uid LEFT OUTER, FilTypeData By uid;

--(6) join��̕ϐ��̑I��
--PicOutData = FOREACH JoinedData GENERATE 
--	FiledData::time AS time,
--	FiledData::uid AS uid,
--	FiledData::verb AS verb,
--	FilTypeData::type AS type
--;

--(7) join���ꂽ�f�[�^��type���U���Ă��Ȃ����[�U���폜�F
--�w������������Asession�񐔂�2��ȏ゠��A�w�肵��4�̍s���񐔂ɍ�����������́i15��ȏ�̍w���҂ُ͈�l�Ƃ��ď������j
--FixedData = FILTER PicOutData BY type != '';
--FixedData = FILTER PicOutData BY type == 'new';
--FixedData = FILTER PicOutData BY type == 'search';
--FixedData = FILTER PicOutData BY type == 'comment';
--FixedData = FILTER PicOutData BY type == 'category';


--(8) �O���[�v��(time,type,verb)
Grouped = GROUP FilOctData BY (uid); 

Result = FOREACH Grouped { 
    ord = ORDER FilOctData  BY time ASC;
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

Grouped = GROUP Result04 BY (verb, postVerb);

Result05 = FOREACH Grouped { 
    cnt = Result04.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS cnt;
} 

STORE Result05 INTO '$PATH_OUTPUT' using PigStorage('\t');