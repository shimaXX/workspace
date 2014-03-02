--UDF�̒�`
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT 'works/input/log_queue_activities_20120*xx.csv.gz';
%default PATH_OUTPUT 'works/output/galsterGetRegisterDate';
--data/log_queue_activities_20120*xx.csv.gz

--(1)�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE uid, verb, cid, GetClient(ap) AS client, SUBSTRING(time, 0, 10) AS time;

--(3) galster�ɍi��Bsp�ɍi��B
FilteredData = FILTER EditData BY (cid == 2) AND (client == 'sp');

--(4) �s�v�ȗ�iclient, cid�j���폜
EditData = FOREACH FilteredData GENERATE uid, time;

--(5) uid�ŃO���[�v��
Grouped = GROUP EditData BY (uid); 

Result = FOREACH Grouped { 
    row_time = EditData.time; 
    GENERATE FLATTEN(group), MAX(row_time), MIN(row_time); 
} 
STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');