--UDF�̒�`
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT 'works/input/log_queue_activities_20120*xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/oct/';
%default PATH_OUTPUT 'works/output/GalsterVerbCount1024';

--(1)�f�[�^�̑Ή��t��
--RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
--  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
--;
--(1)�f�[�^�̑Ή��t���@10��
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowOctData GENERATE uid, verb, cid, GetClient(ap) AS client, SUBSTRING(time, 0,10) AS time;

--(3) galster�ɍi��Bsp�ɍi��B
FilteredData = FILTER EditData BY (cid == 2) AND (SUBSTRING(time, 0, 10) >= '2012-10-18') AND (SUBSTRING(time, 0, 10) < '2012-10-25') AND (client == 'sp');

--(4) �s�v�ȗ�icid�j���폜
EditData = FOREACH FilteredData GENERATE uid, verb;

Grouped = GROUP FilteredData BY (uid, verb); 

Result = FOREACH Grouped { 
    verb_count = FilteredData.verb; 
    GENERATE FLATTEN(group), COUNT(verb_count); 
} 

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');