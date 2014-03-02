-----------------------------------------
--login���������߂�pig script
-----------------------------------------
--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare EXSTART_DATE '2012-11-07' --ci-labo��11/8����̏W�v���s��
%declare EXLAST_DATE  '2012-11-20' --�܂�19���܂ł̃f�[�^���擾����
%declare START_DATE  '2012-11-19' --�܂�20������̃f�[�^���擾����
%declare LAST_DATE  '2012-12-04' --�܂�03���܂ł̃f�[�^���擾����

--UDF�̒�`
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT 'works/input/ci-labo/';
%default PATH_OUTPUT 'works/output/Ci-Labo/Ci-LaboCountLoginDays1203';

--(1)�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time, 0, 10) AS days;

--(3) galster�ɍi��Bsp�ɍi��B
FilteredDataPrior = FILTER EditData BY cid == 4 AND days > '$EXSTART_DATE' AND days < '$EXLAST_DATE';
FilteredDataPost = FILTER EditData BY cid == 4 AND days > '$START_DATE' AND days < '$LAST_DATE';

--(4) �s�v�ȗ�icid�j���폜
EditDataPrior = FOREACH FilteredDataPrior GENERATE uid, verb;
EditDataPost = FOREACH FilteredDataPost GENERATE days, uid;

--(5) �W�v�Ώێ҂��i�邽�߂�uid��,verb���̏W�v
Grouped = GROUP EditDataPrior BY uid; 

CntPrior = FOREACH Grouped { 
    verb_count = EditDataPrior.verb; 
    GENERATE FLATTEN(group) AS uid, COUNT(verb_count) AS verbCnt; 
} 

FilteredPrior = FILTER CntPrior BY verbCnt > 0 ;
ResultPrior = FOREACH FilteredPrior GENERATE uid; 

--���O�C�������̃J�E���g
Grouped = GROUP EditDataPost BY (uid); 

ResultPost = FOREACH Grouped { 
    day = EditDataPost.days; 
    disDay = DISTINCT day;
    GENERATE FLATTEN(group) AS uid, COUNT(disDay) AS count_day; 
} 

--(7) �W�v�Ώێҗp�̃f�[�^�݂̂ɍi��(join)
Joined = join ResultPrior BY uid LEFT OUTER, ResultPost BY uid USING 'replicated';

--(8) �f�[�^�̎�̑I��
Result = FOREACH Joined GENERATE 
	ResultPrior::uid AS uid,
	ResultPost::count_day AS count_day
;

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');