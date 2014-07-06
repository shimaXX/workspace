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
%default PATH_INPUT 'works/input/log_queue_activities_201208xx.csv.gz';
--%default PATH_INPUT 'works/input/';
%default PATH_OUTPUT 'works/output/networkxGraphMonth8';


--(1)�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;

FilteredData = FILTER RowData BY (cid == 2) AND (uid == 'ngr501796f030bd3');
--	AND (time >= '2012-09-01 00:00:00' AND time < '2012-09-08 00:00:00');
EditData = FOREACH FilteredData GENERATE ISOFormat(time) AS time, GetClient(ap) AS client, uid, verb;

FilteredData = FILTER EditData BY client == 'sp';

Grouped = GROUP FilteredData BY uid; 

Result = FOREACH Grouped { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

Result02 = FOREACH Result GENERATE uid, verb, time, session_id;

Grouped = GROUP Result02 BY uid;

Result03 = FOREACH Grouped { 
    ord02 = ORDER Result02  BY time ASC;
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

Grouped = GROUP Result05 BY (verb, postVerb);

--lastVerb��postVerb�̑g�ݍ��킹�ł܂Ƃ߂�
--�����Result04�ƌ�������
Result06 = FOREACH Grouped { 
    GENERATE FLATTEN(Result05);
} 

JoinedData = JOIN
 Result04 BY (verb, postVerb), 
 Result06 BY (verb, postVerb)
 USING 'replicated'
;

ResultData = FOREACH JoinedData GENERATE $0 AS uid, $1 AS lastVerb, $2 AS postVerb, $5 AS cnt;

STORE ResultData INTO '$PATH_OUTPUT' using PigStorage('\t');