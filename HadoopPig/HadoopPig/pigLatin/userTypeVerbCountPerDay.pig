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
%default PATH_INPUT_TYPE 'works/input/typeonlyPU.csv';
%default PATH_INPUT_ORIG 'works/input/log_queue_activities_20120*xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/oct/2012-10-22';
%default PATH_OUTPUT 'works/output/Result_rev2';


--(1)-1�f�[�^�̑Ή��t���@9�����܂�
RowSepData = LOAD '$PATH_INPUT_ORIG' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;

--(1)-2�f�[�^�̑Ή��t���@10��
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(1)-3�f�[�^�̑Ή��t���@type��uid�݂̂̃f�[�^
RowTypeData = LOAD '$PATH_INPUT_TYPE' USING PigStorage(',') AS (
  uid:chararray,type:chararray)
;

--(2)input data�̕ϐ��̑I��
SepData = FOREACH RowSepData GENERATE ISOFormat(time) AS time , uid, verb, cid, GetClient(ap) AS client;  
OctData = FOREACH RowOctData GENERATE ISOFormat(time) AS time , uid, verb, cid, GetClient(ap) AS client;

--(3)�t�B���^�[����
FilSepData = FILTER SepData BY (cid == 2) AND (client == 'sp');
FilOctData = FILTER OctData BY (cid == 2) AND (client == 'sp');
FilTypeData = FILTER RowTypeData BY type != '';

--(4) �f�[�^��union
FiledData = UNION FilSepData , FilOctData;

--(5) ���ɂȂ�f�[�^��Type�f�[�^��join
JoinedData = JOIN FiledData BY uid LEFT OUTER, FilTypeData By uid;

--(6) join��̕ϐ��̑I��
PicOutData = FOREACH JoinedData GENERATE 
	FiledData::time AS time,
	FiledData::uid AS uid,
	FiledData::verb AS verb,
	FilTypeData::type AS type
;

--(7) join���ꂽ�f�[�^��type���U���Ă��Ȃ����[�U���폜�F
--�w������������Asession�񐔂�2��ȏ゠��A�w�肵��4�̍s���񐔂ɍ�����������́i15��ȏ�̍w���҂ُ͈�l�Ƃ��ď������j
FixedData = FILTER PicOutData BY type != '';

--(7)-1 �f�[�^�̐��`
FixedData = FOREACH FixedData GENERATE SUBSTRING(time,0,10) AS time, uid, verb, type;

--(8) �O���[�v��(time,type,verb)
Grouped = GROUP FixedData BY (time, type, verb); 

--(9) �W�v����
ResultCnt = FOREACH Grouped {  
    cnt = FixedData.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS count;
} 

DESCRIBE ResultCnt;

--(10) �O���[�v��(time,type)
Grouped = GROUP FixedData BY (time, type); 

--(11) �W�v����
ResultUU = FOREACH Grouped {  
    cnt = DISTINCT FixedData.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS count;
} 

--(12) daily��seg����UU�f�[�^��join
JoinedData = JOIN ResultCnt BY (time, type) LEFT OUTER, ResultUU By (time, type);

DESCRIBE JoinedData;

--(13) join��̕ϐ��̑I��
ResultAll = FOREACH JoinedData GENERATE 
	ResultCnt::group::time AS time,
	ResultCnt::group::type AS type,
	ResultCnt::group::verb AS verb,
	ResultCnt::count AS cnt,
	ResultUU::count AS UU
;

STORE ResultAll INTO '$PATH_OUTPUT' using PigStorage('\t');