-----------------------------------------
--�Z�b�V�������Ԃ̕��ϒl�����߂�pig script
-----------------------------------------
--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare EXSTART_DATE '2012-11-07' --ci-labo��11/8����̏W�v���s��
%declare EXLAST_DATE  '2012-11-20' --�܂�19���܂ł̃f�[�^���擾����
%declare START_DATE  '2012-11-07' --�܂�08������̃f�[�^���擾����
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

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/ci-labo/';
%default PATH_OUTPUT_TIME 'works/output/Ci-Labo/Ci-LaboSessonTimeFull1203';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionize�͐擪��time���K�v
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid,verb;

--(3) ci-labo�ɍi��
FilteredDataPrior = FILTER Edit BY cid == 4 AND SUBSTRING(time,0,10) > '$EXSTART_DATE';
FilteredDataPost = FILTER Edit BY cid == 4 AND SUBSTRING(time,0,10) > '$START_DATE';

--(4) �s�v�ȗ�icid�j���폜
EditDataPrior = FOREACH FilteredDataPrior GENERATE uid, verb;
EditDataPost = FOREACH FilteredDataPost GENERATE time, uid;

--(5) �W�v�Ώێ҂��i�邽�߂�uid��,verb���̏W�v
Grouped = GROUP EditDataPrior BY uid; 

CntPrior = FOREACH Grouped { 
    verb_count = EditDataPrior.verb; 
    GENERATE FLATTEN(group) AS uid, COUNT(verb_count) AS verbCnt; 
} 

FilteredPrior = FILTER CntPrior BY verbCnt > 0 ;
ResultPrior = FOREACH FilteredPrior GENERATE uid; 

--�Z�b�V�����J�E���g
Grp = GROUP EditDataPost BY uid;

addSession = FOREACH Grp { 
    ord = ORDER EditDataPost BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP EditData BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpUid = GROUP sessionTime BY uid;  

ResultPost = FOREACH grpUid  GENERATE FLATTEN(group) AS uid, AVG(sessionTime.session_time) AS ave_session_time;


--(7) �W�v�Ώێҗp�̃f�[�^�݂̂ɍi��(join)
Joined = join ResultPrior BY uid LEFT OUTER, ResultPost BY uid USING 'replicated';

--(8) �f�[�^�̎�̑I��
Result = FOREACH Joined GENERATE 
	ResultPrior::uid AS uid,
	ResultPost::ave_session_time AS ave_session_time
;

STORE Result INTO '$PATH_OUTPUT_TIME' USING PigStorage('\t'); 