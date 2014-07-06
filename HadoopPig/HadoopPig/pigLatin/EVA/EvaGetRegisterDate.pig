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

--���o�̓p�X�̒�`
%default PATH_INPUT_OCT 'works/input/oct/';
%default PATH_OUTPUT 'works/output/EVA/EvaRegisterDate';

--(1)-2�f�[�^�̑Ή��t���@10��
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowOctData GENERATE uid, verb, cid, GetClient(ap) AS client, SUBSTRING(time, 0, 10) AS time;

--(3) Eva�ɍi��Bsp�ɍi��B
FilteredData = FILTER EditData BY (cid == 3) AND (time > '2012-10-10');

--(4) �s�v�ȗ�iclient, cid�j���폜
EditData = FOREACH FilteredData GENERATE uid, time;

--(5) uid�ŃO���[�v��
Grouped = GROUP EditData BY (uid); 

Result = FOREACH Grouped { 
    row_time = EditData.time; 
    GENERATE FLATTEN(group), MAX(row_time), MIN(row_time); 
} 
STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');