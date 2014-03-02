--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCharacterCategory myUDF.GetCharacterCategory();
define GetClient myUDF.GetClient();
define GetAverageInterval myUDF.GetAverageIntervalDays();

--���o�̓p�X�̒�`
--%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT 'works/input/log_queue_activities_20120*xx.csv.gz';
--%default PATH_INPUT_OCT 'works/input/oct/';
%default PATH_OUTPUT 'works/output/TEST/testGetInterval';

--(1)-2�f�[�^�̑Ή��t���@10��
--RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
--  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
--;

--(1)�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;

RowData = FOREACH RowData GENERATE uid, cid, SUBSTRING(time,0,10) AS time, GetClient(ap) AS client;

RowData = FILTER RowData BY cid == 2 AND client == 'sp'; 

Grouped = GROUP RowData BY (uid,time);

EE = FOREACH Grouped {
	GENERATE FLATTEN(group); 
}

Grouped = GROUP EE BY uid;

FF = FOREACH Grouped {
	ord = ORDER EE BY time ASC;
	Itime = DISTINCT ord.time;
	GENERATE FLATTEN(group), GetAverageInterval(Itime); 
}

STORE FF INTO '$PATH_OUTPUT' USING PigStorage('\t'); 