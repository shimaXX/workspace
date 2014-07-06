--10/23�܂łɃA�N�e�B�r�e�B������A����11/1�܂�entry���Ă��Ȃ����[�U
--���W�c�Ƃ��A11/1�ȍ~entry�������[�U�Ƃ��Ă��Ȃ����[�U�łǂ��ɍ�������̂�������
--����؂��g��

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m

--entry�������[�U�Ƃ��Ă��Ȃ����[�U�̕�W�c���`���������
%declare TEST_START_DATE  '2012-10-09' --�܂�10/10������̃f�[�^���擾����
%declare TEST_LAST_DATE  '2012-10-24' --�܂�10/23������̃f�[�^���擾����

--
%declare START_DATE  '2012-10-31' --�܂�11/1������̃f�[�^���擾����
%declare LAST_DATE  '2012-11-08' --�܂�7���܂ł̃f�[�^���擾����


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
--%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/EVA/EVAentryUserView';
%default PATH_OUTPUT_SESSION 'works/output/EVA/EVAentryUserViewSession';
%default PATH_OUTPUT_SESSION_TIME 'works/output/EVA/EVAentryUserViewSessionTime';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

EditData = FOREACH RowData GENERATE uid, cid, verb, SUBSTRING(time, 0, 10) AS days, ISOFormat(time) AS time;

--�G���@�̂݁A10/10�`10/23�݂̂̃f�[�^���擾
FilData = FILTER EditData BY cid == 3 AND days > '$TEST_START_DATE' AND days < '$TEST_LAST_DATE';

----------------------------------------
--��L�̏����̃��[�U�̂ݎ��
--���j�[�N���[�UID�̂ݎ擾
--join�̑匳
Grp = GROUP FilData BY uid;

uniqueUserId = FOREACH Grp {
	GENERATE FLATTEN(group) AS uUid; 
}

-------------------------------------------
--��L�̏����v���X����o�^���Ă����ȃ��[�U
--���Ƃ�join����not�ŏ��O����
FilData = FILTER EditData BY cid == 3 AND days > '$TEST_START_DATE' AND days < '2012-11-01'
	AND (verb == 'login' OR verb == 'entry' OR verb == 'mypage') 
;

Grp = GROUP FilData BY uid;

entryFlag = FOREACH Grp {
	cnt = FilData.verb;
	GENERATE FLATTEN(group) AS uUid, COUNT(cnt) AS entryFlag;
}

---------------------------------------------
--10/10�`10/23�ɍs�������郆�[�U�ł�����entry���Ă��郆�[�U���O��
--�܂���join
joinedData = JOIN uniqueUserId BY uUid LEFT OUTER, entryFlag BY uUid USING 'replicated';

TMP = FOREACH joinedData GENERATE
	uniqueUserId::uUid AS uid,
	entryFlag::entryFlag AS flag
;

---------------------------------------------------
--flag�����ł�filter��������Ȃ����߁Acount��1,0��U��
Grp = GROUP TMP BY uid;

TMP = FOREACH Grp {
	cnt = TMP.flag;
	GENERATE FLATTEN(group) AS uid, COUNT(cnt) AS Flag; 
}

--flag = 0�A�܂�10/23�܂ł�entry���Ă��Ȃ����[�U�݂̂ɍi��
Fil = FILTER TMP BY Flag == 0;

--����uid�̂ݎ擾����
getUid = FOREACH Fil GENERATE uid;

-----------------------------------------------------
--10/24�`11/7�̊Ԃ�verb���J�E���g����
FilData = FILTER EditData BY cid == 3 AND days >= '$TEST_LAST_DATE' AND days < '2012-11-08';

Grp = GROUP FilData BY (uid,days,verb);

ResultVerb = FOREACH Grp {
	cnt = FilData.verb;
	GENERATE FLATTEN(group) AS (uid, days, verb), COUNT(cnt) AS cntVerb;
}

-------------------------------------------------------
--join
joined = JOIN getUid BY uid LEFT OUTER, ResultVerb BY uid;

TMP = FOREACH joined GENERATE
	getUid::uid AS uid,
	ResultVerb::days AS days,
	ResultVerb::verb AS verb,
	ResultVerb::cntVerb AS cntVerb
;

Org = FILTER TMP BY days != '';

--uid�Averb����cnt�f�[�^��sum����
Grp = GROUP Org BY (uid, verb);

Result = FOREACH Grp {
	cnt = Org.cntVerb;
	GENERATE FLATTEN(group) AS (uid, verb), FLATTEN(SUM(cnt)) AS sumVerb;
}

-----------------------------------------------------
--10/24�`10/31�̊Ԃ�session�����J�E���g����
FilData = FILTER EditData BY cid == 3 AND days >= '$TEST_LAST_DATE' AND days < '2012-11-01';

Ed = FOREACH FilData GENERATE time, uid, verb; 

Grp = GROUP Ed BY (uid);

Sessionize = FOREACH Grp {
	ord = ORDER Ed BY time;
	GENERATE FLATTEN(Sessionize(ord));
}

--���ёւ�
Ed = FOREACH Sessionize GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--session�񐔂��J�E���g
GroupUid = GROUP Ed BY uid;

--session�񐔂��J�E���g
countSession = FOREACH GroupUid { 
    countS = DISTINCT Ed.session_id; 
    GENERATE FLATTEN(group) AS uid, (int)COUNT(countS) AS scnt; 
} 

joined = JOIN getUid BY uid , countSession BY uid;

TMP = FOREACH joined GENERATE
	getUid::uid AS uid,
	countSession::scnt AS scnt
;

STORE TMP INTO '$PATH_OUTPUT_SESSION' using PigStorage('\t');

-----------------------------------------------------
--10/24�`10/31�̊Ԃ�sessionTime�̕��ϒl���擾����
FilData = FILTER EditData BY cid == 3 AND days >= '$TEST_LAST_DATE' AND days < '2012-11-01';

Ed = FOREACH FilData GENERATE time, uid, verb; 

Grp = GROUP Ed BY (uid);

addSession = FOREACH Grp {
	ord = ORDER Ed BY time;
	GENERATE FLATTEN(Sessionize(ord));
}

Ed = FOREACH addSession GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP Ed BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpDaily = GROUP sessionTime BY uid;  

aveDailySessionTime = FOREACH grpDaily  GENERATE FLATTEN(group) AS uid, AVG(sessionTime.session_time) AS ave_session_time;

joined = JOIN getUid BY uid , aveDailySessionTime BY uid;

TMP = FOREACH joined GENERATE
	getUid::uid AS uid,
	aveDailySessionTime::ave_session_time AS ave_session_time
;

STORE TMP INTO '$PATH_OUTPUT_SESSION_TIME' USING PigStorage('\t'); 