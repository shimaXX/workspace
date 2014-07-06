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
define GetCharacterCategory myUDF.GetCharacterCategory();
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT 'works/input/ci-labo/';
%default PATH_OUTPUT 'works/output/Ci-Labo/Ci-LaboCountSessionNum1203';

--(1)-2�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, verb, cid;

--(3) ci-labo�ɍi��B
FilteredDataPrior = FILTER Edit BY cid == 4 AND SUBSTRING(time, 0, 10) > '$EXSTART_DATE' AND SUBSTRING(time, 0, 10) < '$EXLAST_DATE';
FilteredDataPost = FILTER Edit BY cid == 4 AND SUBSTRING(time, 0, 10) > '$START_DATE' AND SUBSTRING(time, 0, 10) < '$LAST_DATE';

-------------------------------------------------
-- �W�v�Ώێ҂��i�邽�߂�uid��,verb���̏W�v
Grouped = GROUP FilteredDataPrior BY uid; 

CntPrior = FOREACH Grouped { 
    verb_count = FilteredDataPrior.verb; 
    GENERATE FLATTEN(group) AS uid, COUNT(verb_count) AS verbCnt; 
} 

FilteredPrior = FILTER CntPrior BY verbCnt > 0 ;
ResultPrior = FOREACH FilteredPrior GENERATE uid; 


------------------------------------------------------------
--(4) �s�v�ȗ�iclient, cid�j���폜
EditData = FOREACH FilteredDataPost GENERATE time, uid, verb;

--(5) �Z�b�V����ID��U�邽�߂�uid�ŃO���[�v��
Grouped = GROUP EditData BY uid; 

--(6) �Z�b�V����ID�̐�����{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize = FOREACH Grouped { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) time��N�����ɒ����ė�̕��בւ�
EditData = FOREACH Sessionize GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) uid�ŃO���[�v��
GroupUid = GROUP EditData BY uid;

--(9) session�񐔂��J�E���g
ResultPost = FOREACH GroupUid { 
    countS = DISTINCT EditData.session_id; 
    GENERATE FLATTEN(group) AS uid, (int)COUNT(countS) AS scnt; 
} 

-----------------------------------------------------------
--join
-- �W�v�Ώێҗp�̃f�[�^�݂̂ɍi��(join)
Joined = join ResultPrior BY uid LEFT OUTER, ResultPost BY uid USING 'replicated';

-- �f�[�^�̎�̑I��
Result = FOREACH Joined GENERATE 
	ResultPrior::uid AS uid,
	ResultPost::scnt AS scnt
;

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');