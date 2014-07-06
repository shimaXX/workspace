--UDF�̒�`
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT 'works/input/aws/2012-11-*.gz';
%default PATH_OUTPUT 'works/output/galsterGetRegisterDate';


--(1)�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time, 0, 10) AS days;

--(3) ci-labo�ɍi��B
FilteredData = FILTER EditData BY cid == 4;

Grouped = GROUP FilteredData BY (uid); 

Result01 = FOREACH Grouped { 
    day = FilteredData.days; 
    disDay = DISTINCT day;
    GENERATE FLATTEN(group), COUNT(disDay) AS count_day; 
} 

STORE Result01 INTO '$PATH_OUTPUT' using PigStorage('\t');