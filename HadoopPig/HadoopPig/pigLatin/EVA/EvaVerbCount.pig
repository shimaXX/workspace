--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE '2012-10-31'

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategory myUDF.GetCategory();
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT_OCT 'works/input/aws/';
%default PATH_OUTPUT 'works/output/EVA/EvaVerbCount1212';

--(1)-2�f�[�^�̑Ή��t���@10��
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowOctData GENERATE uid, verb, cid, SUBSTRING(time,0,10) AS time;

--(3) EVA�ɍi��
FilteredData = FILTER EditData BY cid == 3 AND time > '2012-11-12'; --'$START_DATE';

--(4) �s�v�ȗ�icid�j���폜
EditData = FOREACH FilteredData GENERATE uid, verb;

--(5) uid��,verb���̏W�v
Grouped = GROUP EditData BY (uid, verb); 

Result = FOREACH Grouped { 
    verb_count = EditData.verb; 
    GENERATE FLATTEN(group), COUNT(verb_count) AS verbCnt; 
} 

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');