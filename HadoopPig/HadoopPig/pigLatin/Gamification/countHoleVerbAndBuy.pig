--UDF�̒�`
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT 'works/input/aws/2012-11-*.gz';
%default PATH_OUTPUT 'works/output/EVA/CorBuyAndVerb';

--(1)�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time, 0, 10) AS time;

--(3) galster�ɍi��Bsp�ɍi��B
FilteredData = FILTER EditData BY cid == 3;

Grouped = GROUP FilteredData BY time;

Result = FOREACH Grouped { 
	verb = FilteredData.verb;
    fil_buy = FILTER FilteredData BY verb == 'buy';
    GENERATE FLATTEN(group) AS time, COUNT(verb) AS cntVerb ,COUNT(fil_buy) AS cntBuy; 
}

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');