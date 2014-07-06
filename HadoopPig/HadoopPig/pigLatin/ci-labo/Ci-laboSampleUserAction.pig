------------------------------------
--�T���v�������������[�U�̂��̌�̍s���g���b�L���O
------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-11-07' --�܂�08������̃f�[�^���擾����


--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategory myUDF.GetCategory();
define GetClient myUDF.GetClient();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--���o�̓p�X�̒�`
%default PATH_INPUT_OCT 'works/input/ci-labo/';
%default PATH_OUTPUT 'works/output/Ci-Labo/Ci-LaboTrack1203';

--(1)-2�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, verb, cid, SUBSTRING(time,0,10) AS days, GetMetaInfo(verb, ap) AS meta;

--(3) ci-labo�ɍi��
FilteredData = FILTER EditData BY cid == 4 AND days > '$START_DATE';

--(4) �s�v�ȗ�icid�j���폜
EditData = FOREACH FilteredData GENERATE time, uid, meta;


-----------------------------------------------------------
--(5) �Z�b�V����ID��U��
Grp = GROUP EditData BY uid;

addSession = FOREACH Grp { 
    ord = ORDER EditData BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

-- meta��verb:sample�݂̂̃f�[�^���擾���A���̃Z�b�V�������擾����
getSampleSessionId = FILTER addSession BY meta == 'view:sample';

------------------------------------------------------------
-- join����
Joined = JOIN addSession BY session_id , getSampleSessionId BY session_id;

-- �f�[�^�̎�̑I��
Edit = FOREACH Joined GENERATE 
	$0 AS time,
	$1 AS uid,
	$2 AS meta,
	$3 AS origSessionId,
	$4 AS sampleTime,
	$7 AS sessionId 
;

Fil  = FILTER Edit BY origSessionId == sessionId AND time >= sampleTime;

--�s�v�ȃf�[�^���̂Ă�
Ed = FOREACH Fil GENERATE uid, meta, time,origSessionId;

-------------------------------------------------------------
-- sample��̍s�����擾
Grouped = GROUP Ed BY origSessionId;

ResultJux = FOREACH Grouped { 
    ord02 = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(JuxtaposeNextVerb(ord02));
} 

--------------------------------------------------
--��������d�݂�join�̂��߂̏����ɓ���
Grouped = GROUP ResultJux BY (verb, postVerb);


Result05 = FOREACH Grouped { 
    cnt = ResultJux.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS cnt;
} 

Grouped = GROUP Result05 BY (verb, postVerb);

--lastVerb��postVerb�̑g�ݍ��킹�ł܂Ƃ߂�
--�����Result04�ƌ�������
Result06 = FOREACH Grouped { 
    GENERATE FLATTEN(Result05);
} 

JoinedData = JOIN
 ResultJux BY (verb, postVerb), 
 Result06 BY (verb, postVerb)
 USING 'replicated'
;

Result = FOREACH JoinedData GENERATE $1 AS lastVerb, $2 AS postVerb, $5 AS cnt;

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');