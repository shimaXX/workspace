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
%default PATH_INPUT 'works/input/log_queue_activities_20120*xx.csv.gz';
%default PATH_OUTPUT 'works/output/TEST/getTranceVerbCount_comment';


--(1)�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;

--(1)-2�f�[�^�̑Ή��t���@type��uid�݂̂̃f�[�^
RowTypeData = LOAD '$PATH_INPUT_TYPE' USING PigStorage(',') AS (
  uid:chararray,type:chararray)
;

--(2) RowData�̍Ē�`
RowData = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid, verb, GetClient(ap) AS client;

--(3) �t�B���^�[����
FiledData = FILTER RowData BY (cid == 2) AND (client == 'sp');
FilTypeData = FILTER RowTypeData BY type != '';

--(4) ���ɂȂ�f�[�^��Type�f�[�^��join
JoinedData = JOIN FiledData BY uid LEFT OUTER, FilTypeData By uid USING 'replicated';

--(5) join��̕ϐ��̑I��
PicOutData = FOREACH JoinedData GENERATE 
	FiledData::time AS time,
	FiledData::uid AS uid,
	FiledData::verb AS verb,
	FilTypeData::type AS type
;

--(6) join���ꂽ�f�[�^��type���U���Ă��Ȃ����[�U���폜�F
--�w������������Asession�񐔂�2��ȏ゠��A�w�肵��4�̍s���񐔂ɍ�����������́i15��ȏ�̍w���҂ُ͈�l�Ƃ��ď������j
FixedData = FILTER PicOutData BY type != '';
--FixedData = FILTER PicOutData BY type == 'new';
--FixedData = FILTER PicOutData BY type == 'search';
FixedData = FILTER PicOutData BY type == 'comment';
--FixedData = FILTER PicOutData BY type == 'category';

--(7) �s�v�ȃf�[�^���폜
EditData = FOREACH FixedData GENERATE time, uid, verb;

Grouped = GROUP EditData BY uid; 

Result = FOREACH Grouped { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

Result02 = FOREACH Result GENERATE uid, verb, time, session_id;

----------------------------------------
--���������buy���܂�session�݂̂̍i��
FilterBuy = FILTER Result02 BY verb == 'buy';

GroupedSession = GROUP FilterBuy BY session_id;

CountBuy = FOREACH GroupedSession { 
    filBuy = FilterBuy.verb;
    GENERATE FLATTEN(group) AS session_id, COUNT(filBuy) AS cntBuy;
} 

--�匳��join
JoinedData = JOIN Result02 BY session_id LEFT OUTER ,CountBuy BY session_id  USING 'replicated';

EditData = FOREACH JoinedData GENERATE
	$0 AS uid,
	$1 AS verb,
	$2 AS time,
	$3 AS session_id,
	$5 AS cntBuy
;

Fil = FILTER EditData BY (chararray)cntBuy !=''; 

EditData = FOREACH Fil GENERATE $0 AS uid, $1 AS verb, $2 AS time, $3 AS session_id;

Grouped = GROUP EditData BY uid;

-------------------------
--��������͘A������verb���l��
Result03 = FOREACH Grouped { 
    ord02 = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(JuxtaposeNextVerb(ord02));
} 

--�����܂łŊe���[�U����lastVerb��postVerb�̐��`�͏I��
Result04 = FILTER Result03 BY postVerb != '' AND postVerb != verb;

--------------------------------------------------
--��������d�݂�join�̂��߂̏����ɓ���
Grouped = GROUP Result04 BY (verb, postVerb);

Result05 = FOREACH Grouped { 
    cnt = Result04.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS cnt;
} 

--Grouped = GROUP Result05 BY (verb, postVerb);

--lastVerb��postVerb�̑g�ݍ��킹�ł܂Ƃ߂�
--�����Result04�ƌ�������
--Result06 = FOREACH Grouped { 
--    GENERATE FLATTEN(Result05);
--} 

--JoinedData = JOIN
-- Result04 BY (verb, postVerb), 
-- Result06 BY (verb, postVerb)
-- USING 'replicated'
--;

--ResultData = FOREACH JoinedData GENERATE $0 AS uid, $1 AS lastVerb, $2 AS postVerb, $5 AS cnt;

--STORE ResultData INTO '$PATH_OUTPUT' using PigStorage('\t');
STORE Result05 INTO '$PATH_OUTPUT' using PigStorage('\t');