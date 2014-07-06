------------------------------------
--�e���[�U����verb�̉񐔂��J�E���g����
------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare EXSTART_DATE '2012-11-07' --ci-labo��11/8����̏W�v���s��
%declare EXLAST_DATE  '2012-11-20' --�܂�19���܂ł̃f�[�^���擾����
%declare START_DATE  '2012-11-19' --�܂�20������̃f�[�^���擾����
%declare LAST_DATE  '2012-12-04' --�܂�03���܂ł̃f�[�^���擾����

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategory myUDF.GetCategory();
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT_OCT 'works/input/ci-labo/';
%default PATH_OUTPUT 'works/output/Ci-Labo/Ci-LaboVerbCount1203';

--(1)-2�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time,0,10) AS time;

--(3) ci-labo�ɍi��
FilteredDataPrior = FILTER EditData BY cid == 4 AND time > '$EXSTART_DATE' AND time < '$EXLAST_DATE';
FilteredDataPost = FILTER EditData BY cid == 4 AND time > '$START_DATE' AND time < '$LAST_DATE';

--(4) �s�v�ȗ�icid�j���폜
EditDataPrior = FOREACH FilteredDataPrior GENERATE uid, verb;
EditDataPost = FOREACH FilteredDataPost GENERATE uid, verb;

--(5) �W�v�Ώێ҂��i�邽�߂�uid��,verb���̏W�v
Grouped = GROUP EditDataPrior BY uid; 

CntPrior = FOREACH Grouped { 
    verb_count = EditDataPrior.verb; 
    GENERATE FLATTEN(group) AS uid, COUNT(verb_count) AS verbCnt; 
} 

FilteredPrior = FILTER CntPrior BY verbCnt > 0 ;
ResultPrior = FOREACH FilteredPrior GENERATE uid; 

-----------------------------------------------------------
--(6) �W�v�p��uid��,verb���̏W�v
Grouped = GROUP EditDataPost BY (uid, verb); 

ResultPost = FOREACH Grouped { 
    verb_count = EditDataPost.verb; 
    GENERATE FLATTEN(group) AS (uid,verb), COUNT(verb_count) AS verbCnt; 
} 

--(7) �W�v�Ώێҗp�̃f�[�^�݂̂ɍi��(join)
Joined = join ResultPrior BY uid LEFT OUTER, ResultPost BY uid USING 'replicated';

--(8) �f�[�^�̎�̑I��
Result = FOREACH Joined GENERATE 
	ResultPrior::uid AS uid,
	ResultPost::verb AS verb,
	ResultPost::verbCnt AS verbCnt
;

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');