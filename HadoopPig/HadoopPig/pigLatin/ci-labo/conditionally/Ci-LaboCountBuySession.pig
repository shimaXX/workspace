-----------------------------------------
-- ci-labo�͍w���A�C�e��������buy��verb�Ƃ��ē��邽�߁Abuy�̂���Z�b�V�������J�E���g����
-----------------------------------------

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
define GetPayment myUDF.GetPayment();
define GetCategory myUDF.GetCategory();
define GetNewflag myUDF.GetNewflag();
define GetReservationflag myUDF.GetReservationflag(); 
define GetNextDate myUDF.GetNextDate();
define GetSessionTime myUDF.GetSessionTime();
define MergeVerb myUDF.MergeVerb();

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/ci-labo/';
%default PATH_OUTPUT_BUYSES 'works/output/Ci-Labo/sessionBuy1203';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionize�͐擪��time���K�v
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid, verb;

-- �f�[�^���i��
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


--------------------------------------------
--���������session
Grp = GROUP FilteredDataPost BY uid;

addSession = FOREACH Grp { 
    ord = ORDER FilteredDataPost  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, verb, time, session_id;

FilBuy = FILTER EditData BY verb == 'buy';

Grp = GROUP FilBuy BY uid;

ResultPost = FOREACH Grp { 
    cnt = DISTINCT FilBuy.session_id;
    GENERATE FLATTEN(group) AS uid, COUNT(cnt) AS buyCnt;
} 


--------------------------------------------
--join
-- �W�v�Ώێҗp�̃f�[�^�݂̂ɍi��(join)
Joined = join ResultPrior BY uid LEFT OUTER, ResultPost BY uid USING 'replicated';

-- �f�[�^�̎�̑I��
Result = FOREACH Joined GENERATE 
	ResultPrior::uid AS uid,
	ResultPost::buyCnt AS buyCnt
;

STORE Result INTO '$PATH_OUTPUT_BUYSES' USING PigStorage('\t'); 