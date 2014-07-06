--UDF�̒�`
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT 'works/input/aws/2012-11-*.gz';
%default PATH_OUTPUT 'works/output/EVA/EvaUU';
--data/log_queue_activities_20120*xx.csv.gz

--(1)�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time, 0, 10) AS time;

--(3) galster�ɍi��Bsp�ɍi��B
FilteredData = FILTER EditData BY (cid == 3);

Grouped = GROUP FilteredData BY (time);

Result = FOREACH Grouped { 
    uid_count = DISTINCT FilteredData.uid;
    fil_login = FILTER FilteredData BY verb == 'login';
    login_count = DISTINCT fil_login.uid;
    GENERATE FLATTEN(group), COUNT(uid_count) AS UU ,COUNT(login_count) AS loginUU; 
} 
STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');