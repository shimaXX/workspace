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
%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/aws/2012-11-0*.gz';
%default PATH_OUTPUT 'works/output/GalsterSession1024';

--(1)�f�[�^�̑Ή��t��
--RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
--  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
--;

--(1)-2�f�[�^�̑Ή��t���@10��
RowData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

RowData = FOREACH RowData GENERATE uid, cid, GetClient(ap) AS client, time ,verb;

FilteredData = FILTER RowData BY (cid == 2) AND (client == 'sp');
    --AND (SUBSTRING(time, 0, 10) >= '2012-10-18') AND (SUBSTRING(time, 0, 10) < '2012-10-25');
EditData = FOREACH FilteredData GENERATE ISOFormat(time) AS time, uid, verb;

Grouped = GROUP EditData BY uid; 

Result = FOREACH Grouped { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

Result02 = FOREACH Result GENERATE uid, verb, time, session_id;

LL = LIMIT Result02 10;
DUMP LL; 

--STORE Result02 INTO '$PATH_OUTPUT' using PigStorage('\t');