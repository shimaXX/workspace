-----------------------------------------
--�C�x���g���ʂ��v�����邽�߂̒l���擾����
--�C�x���g�Q���҂����S�Ɉ�v�����Ă���
-----------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-24' --�܂�25������̃f�[�^���擾����
%declare LAST_DATE  '2012-11-01' --�܂�31���܂ł̃f�[�^���擾����
%declare POSTSTART_DATE  '2012-10-31'
%declare POSTLAST_DATE  '2012-11-08'

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar
REGISTER GetIntervalDate.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');

define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategory myUDF.GetCategory();
define GetClient myUDF.GetClient();
define GetIntervalDate myUDF.GetIntervalDate('$START_DATE');
define GetSessionTime myUDF.GetSessionTime();


--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT 'works/output/Ming/EvaCausalInference0115';
%default PATH_OUTPUT_VERB 'works/output/Ming/EvaCountVerb0115';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--------------------------------
--�Ώێ҂̍i�荞�݂��s��
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS time, uid, cid, verb, GetClient(ap) AS client;
FilData = FILTER Edit BY cid == 3 AND time < '$LAST_DATE';	---���t

Ouid = FOREACH FilData GENERATE uid;
Grp = GROUP Ouid BY uid; 
Ouid = FOREACH Grp { 
	U = DISTINCT Ouid.uid;
	GENERATE FLATTEN(U) AS uid;
}

Fil = FILTER FilData BY verb=='entry' or verb=='login';

Grp = GROUP Fil BY uid;
CntEntry = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(Fil.verb) AS cntV;

--EntryFlag��t���邽�߂Ƀt����uid��entry���[�U����������
Joined = JOIN Ouid BY uid LEFT OUTER, CntEntry BY uid USING 'replicated';

--�K�v�ȕϐ��݂̂ɐ���
Edj = FOREACH Joined GENERATE 
	Ouid::uid AS uid,
	CntEntry::cntV AS cntV
;

--entryFlag��t����
Ed = FOREACH Edj GENERATE uid, (cntV IS NULL ? 0: 1) AS entFlag;

--entry���Ă��Ȃ����[�U�ɍi��
FF = FILTER Ed BY entFlag==0;

--entry���Ă��Ȃ����[�U��uid�����̃e�[�u�����擾
POU = FOREACH FF GENERATE uid;

--���K���1�T�Ԉȏ�o�߂����̐l�Ԃɍi�邽�߂�uid���擾
Filed = FILTER Edit BY cid == 3 AND time < '2012-10-25';
Grp = GROUP FilData BY uid;
UU = FOREACH Grp { 
	U = DISTINCT FilData.uid;
	GENERATE FLATTEN(U) AS uid;
}

--���K���1�T�Ԉȏ�o�߂����̐l�Ԃ݂̂ɍi��
JoinedOU = JOIN UU BY uid, POU BY uid USING 'replicated';

OUR = FOREACH JoinedOU GENERATE UU::uid AS uid;


--------------------------------------
--�C�x���g�O1�T�Ԃ̃f�[�^�擾
FilPre = FILTER Edit BY cid == 3 AND time < '$LAST_DATE' AND time > '$START_DATE';	---���t

Grp = GROUP FilPre BY uid;
CntVerbPre = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPre.verb) AS cntV;

ResultPre = FOREACH CntVerbPre GENERATE uid, cntV, (uid IS NULL ? 0: 0) as Delta;


--------------------------------------
--�C�x���g��1�T�Ԃ̃f�[�^�擾
FilPro = FILTER Edit BY cid == 3 AND time >= '$LAST_DATE' AND time < '$POSTLAST_DATE';	---���t

Grp = GROUP FilPro BY uid;
CntVerbPro = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPro.verb) AS cntV;

EntryUsr = FILTER FilPro BY verb=='entry';
JoinedPro = JOIN CntVerbPro BY uid LEFT OUTER, EntryUsr BY uid USING 'replicated';

EdPro = FOREACH JoinedPro GENERATE
	CntVerbPro::uid AS uid,
	CntVerbPro::cntV AS cntV,
	EntryUsr::verb AS entFlag
;

ResultPro = FOREACH EdPro GENERATE uid, cntV, (entFlag IS NULL ? 0 : 1) AS Z,  (uid IS NULL ? 1 : 1) AS Delta;


----------------------------------------
--join
JoinedRePre = JOIN OUR BY uid, ResultPre BY uid USING 'replicated';
JoinedRePro = JOIN OUR BY uid, ResultPro BY uid USING 'replicated';

Jpre = FOREACH JoinedRePre GENERATE
	OUR::uid AS uid,
	ResultPre::cntV AS cntVPre,
	ResultPre::Delta AS DeltaPre
;

Jpro = FOREACH JoinedRePro GENERATE
	OUR::uid AS uid,
	ResultPro::cntV AS cntVPro,
	ResultPro::Z AS Z,
	ResultPro::Delta AS DeltaPro
;

JoinedRe = JOIN Jpre BY uid, Jpro BY uid USING 'replicated';

Result = FOREACH JoinedRe GENERATE
	Jpre::uid AS uid,
	Jpre::cntVPre AS cntVPre,
	Jpro::cntVPro AS cntVPro,
	Jpro::Z AS Z,
	Jpre::DeltaPre AS DeltaPre,	--�v�Z���͕s�v
	Jpro::DeltaPro AS DeltaPro	--�v�Z���͕s�v
;


--------------------------------
--------------------------------
--verb�̍ŏ�������̊��Ԃ����߂�
Grp = GROUP Filed BY uid;
minActTime = FOREACH Grp GENERATE FLATTEN(group) AS uid, MIN(Filed.time) AS minTime; 
SpanFromMinTime = FOREACH minActTime GENERATE uid, GetIntervalDate(minTime) AS DateFromFirst;

--���Ԗ���verb���Ɗϑ����ԓ��ōŏ�������̓�����join
Joined = JOIN Result BY uid, SpanFromMinTime BY uid USING 'replicated';

--���`
ResultJoinDays = FOREACH Joined GENERATE
	Result::uid AS uid,
	Result::cntVPre AS cntVPre,
	Result::cntVPro AS cntVPro,
	SpanFromMinTime::DateFromFirst AS DateFromFirst,
	Result::Z AS Z
;


------------------------------------------
--�Z�b�V�����n---------------------------------
--Sessionize�͐擪��time���K�v
--Session�񐔂̃J�E���g
EdSession = FOREACH RowData GENERATE ISOFormat(time) AS time, SUBSTRING(time,0,10) AS date, uid, cid, verb, GetClient(ap) AS client;
Fil = FILTER EdSession BY cid == 3 AND date > '$START_DATE' AND date < '$LAST_DATE'; 

Ed = FOREACH Fil GENERATE time, verb, uid;

--(5) �Z�b�V����ID��U�邽�߂�uid�ŃO���[�v��
Grouped = GROUP Ed BY uid; 

--(6) �Z�b�V����ID�̐���
Sessionize01 = FOREACH Grouped { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) time��N�����ɒ����ė�̕��בւ�
Ed = FOREACH Sessionize01 GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) session�񐔂��J�E���g
GroupUid = GROUP Ed BY uid;

--(9) session�񐔂��J�E���g
ResultCountSession01 = FOREACH GroupUid { 
    countS = DISTINCT Ed.session_id; 
    GENERATE FLATTEN(group) AS uid, (int)COUNT(countS) AS scnt; 
} 


---------------------------------
--sessionTime�̕��ϒl�̎擾
Ed = FOREACH Sessionize01 GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP Ed BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpUU = GROUP sessionTime BY uid;  

ResultSessionTime01 = FOREACH grpUU  GENERATE FLATTEN(group) AS uid, AVG(sessionTime.session_time) AS ave_session_time;

----------------------
--�匳�̃f�[�^�Z�b�g��sessionCnt��sessionTime��join����
Joined = Join ResultJoinDays BY uid, ResultCountSession01 BY uid;

EdJoinDaysAndCntSess = FOREACH Joined GENERATE
	ResultJoinDays::uid AS uid,
	ResultJoinDays::cntVPre AS cntVPre,
	ResultJoinDays::cntVPro AS cntVPro,
	ResultJoinDays::DateFromFirst AS DateFromFirst,
	ResultCountSession01::scnt AS scnt,
	ResultJoinDays::Z AS Z
;


Joined = Join EdJoinDaysAndCntSess BY uid, ResultSessionTime01 BY uid;

EdJoinDaysAndCntSess = FOREACH Joined GENERATE
	EdJoinDaysAndCntSess::uid AS uid,
	EdJoinDaysAndCntSess::cntVPre AS cntVPre,
	EdJoinDaysAndCntSess::cntVPro AS cntVPro,
	EdJoinDaysAndCntSess::DateFromFirst AS DateFromFirst,
	EdJoinDaysAndCntSess::scnt AS scnt,
	ResultSessionTime01::ave_session_time AS ave_session_time,
	EdJoinDaysAndCntSess::Z AS Z
;

STORE EdJoinDaysAndCntSess INTO '$PATH_OUTPUT' using PigStorage('\t');


--------------------------------------
--------------------------------------
--verb���J�E���g����
--(3) EVA�ɍi��
FilteredData = FILTER Edit BY cid == 3 AND
				time > '$START_DATE' AND time < '$LAST_DATE';	---���t

--(4) �s�v�ȗ�icid�j���폜
EditData = FOREACH FilteredData GENERATE uid, verb;

--(5) uid��,verb���̏W�v
Grouped = GROUP EditData BY (uid, verb); 

ResultVerb = FOREACH Grouped { 
    verb_count = EditData.verb; 
    GENERATE FLATTEN(group) AS (uid,verb), COUNT(verb_count) AS verbCnt; 
} 

--------------------------------------------
--���ԓ��̖K��������J�E���g����
EditData = FOREACH FilteredData GENERATE uid, time;
Grp = GROUP EditData BY uid;
CntDays = FOREACH Grp{
	Dates = DISTINCT EditData.time;
	GENERATE FLATTEN(group) AS uid, COUNT(Dates) AS CntVisitDays;
}


--------------------------------
--verb�̉񐔂�K������Ŋ���
--�܂���verb�̉񐔂ƖK�����joint--
Joined = JOIN ResultVerb BY uid, CntDays BY uid USING 'replicated';

EdVerbDate = FOREACH Joined GENERATE
	ResultVerb::uid AS uid,
	ResultVerb::verb AS verb,
	ResultVerb::verbCnt AS verbCnt,
	CntDays::CntVisitDays AS VisitDays
;

VerbPerDay = FOREACH EdVerbDate GENERATE uid, verb, ((double)verbCnt/(double)VisitDays) AS VperD;

JoinedEdVerbData = JOIN EdJoinDaysAndCntSess BY uid LEFT OUTER, VerbPerDay BY uid USING 'replicated';

ResultVerbCount = FOREACH JoinedEdVerbData GENERATE
	EdJoinDaysAndCntSess::uid AS uid,
	VerbPerDay::verb AS verb,
	VerbPerDay::VperD AS VperD
;

STORE ResultVerbCount INTO '$PATH_OUTPUT_VERB' USING PigStorage();