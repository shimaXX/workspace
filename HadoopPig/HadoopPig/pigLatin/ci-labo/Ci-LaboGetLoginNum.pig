--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-12-03' --�܂�29������̃f�[�^���擾����
%declare LAST_DATE  '2012-12-16' --�܂�4���܂ł̃f�[�^���擾����
%declare PROSTART_DATE  '2012-12-15' --�܂�22������̃f�[�^���擾����
%declare PROLAST_DATE  '2012-12-23' --�܂�28���܂ł̃f�[�^���擾����

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCharacterCategory myUDF.GetCharacterCategory();
define GetClient myUDF.GetClient();
define GetPayment myUDF.GetPayment();
define GetMetaInfo myUDF.GetMetaInfo(); 
define GetNextDate myUDF.GetNextDate();
define GetRewards myUDF.GetRewards();
define CountBadges myUDF.CountBadges();
define TestTmp myUDF.TestTmp();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();
define GetSessionTime myUDF.GetSessionTime();


--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT 'works/output/Mining/Ci-LaboFlag_Buzz_1week_0124';
%default PATH_OUTPUT_VERB 'works/output/Mining/Ci-LaboBuzz_1week_0124';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray,f6,rb:chararray)
;

--rewards�̂ݎ���Ă���Brewards����̏ꍇ��NULL�Ƃ��Ă���B
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, GetMetaInfo(verb, ap) AS verb, SUBSTRING(time,0,10) AS date, cid;


----------------------------------------
--�������O��login�̐��l
----------------------------------------
FilData = FILTER Edit BY (cid == 7 OR cid==8) AND date > '$START_DATE' AND date < '$LAST_DATE';

--(5) �Z�b�V����ID��U�邽�߂�uid�ŃO���[�v��
Grouped = GROUP FilData BY uid; 

--(6) �Z�b�V����ID�̐�����{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize = FOREACH Grouped { 
    ord = ORDER FilData  BY time ASC;
	cd = DISTINCT FilData.date;    
    GENERATE FLATTEN(Sessionize(ord)), COUNT(cd) AS CntDate;
} 

--(7) time��N�����ɒ����ė�̕��בւ�
EditData = FOREACH Sessionize GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time ,CntDate;

Fil = FILTER EditData BY verb == 'buy';

Grp = GROUP Fil BY session_id;
EditBuySessId = FOREACH Grp GENERATE FLATTEN(group) AS session_id;	--�w���̂���Z�b�V�������O�����߂�ID���擾

------------------------------------
--buy�̃Z�b�V������join
Joined = JOIN EditData BY session_id LEFT OUTER, EditBuySessId BY session_id USING 'replicated'; 

EdJoin = FOREACH Joined GENERATE
	$0 AS uid,
	$1 As verb,
	$2 AS session_id,
	$3 AS time,
	$4 AS CntDate,
	($5 IS NULL? 'NULL' :$5) AS buySession_id
;

--buy�ȊO�̃Z�b�V�����ɍi����
FilNotBuySess = FILTER EdJoin BY buySession_id == 'NULL';

EdNotBuy = FOREACH FilNotBuySess GENERATE uid, verb, session_id, time, CntDate;

Fil = FILTER EdNotBuy BY verb == 'login';

Grp = GROUP EdNotBuy BY uid;
CntLogin = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(EdNotBuy.verb) AS CntLogin, FLATTEN(EdNotBuy.CntDate) AS CntDate;

Grp = GROUP CntLogin BY (uid, CntLogin, CntDate);
CntLogin = FOREACH Grp GENERATE FLATTEN(group);

EdLoginPerDayPre = FOREACH CntLogin GENERATE uid, CntLogin, CntDate, ((double)CntLogin/(double)CntDate) AS CntLoginPerDay;


----------------------------------------
--���������login�̐��l
----------------------------------------
FilDataPro = FILTER Edit BY (cid == 7 OR cid==8) AND date > '$PROSTART_DATE' AND date < '$PROLAST_DATE';

--(5) �Z�b�V����ID��U�邽�߂�uid�ŃO���[�v��
Grouped = GROUP FilDataPro BY uid; 

--(6) �Z�b�V����ID�̐�����{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize = FOREACH Grouped { 
    ord = ORDER FilDataPro  BY time ASC;
	cd = DISTINCT FilDataPro.date;    
    GENERATE FLATTEN(Sessionize(ord)), COUNT(cd) AS CntDate;
} 

--(7) time��N�����ɒ����ė�̕��בւ�
EditData = FOREACH Sessionize GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time ,CntDate;

Fil = FILTER EditData BY verb == 'buy';

Grp = GROUP Fil BY session_id;
EditBuySessId = FOREACH Grp GENERATE FLATTEN(group) AS session_id;	--�w���̂���Z�b�V�������O�����߂�ID���擾

------------------------------------
--buy�̃Z�b�V������join
Joined = JOIN EditData BY session_id LEFT OUTER, EditBuySessId BY session_id USING 'replicated'; 

EdJoin = FOREACH Joined GENERATE
	$0 AS uid,
	$1 As verb,
	$2 AS session_id,
	$3 AS time,
	$4 AS CntDate,
	($5 IS NULL? 'NULL' :$5) AS buySession_id
;

--buy�ȊO�̃Z�b�V�����ɍi����
FilNotBuySess = FILTER EdJoin BY buySession_id == 'NULL';

EdNotBuy = FOREACH FilNotBuySess GENERATE uid, verb, session_id, time, CntDate;

Fil = FILTER EdNotBuy BY verb == 'login';

Grp = GROUP EdNotBuy BY uid;
CntLogin = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(EdNotBuy.verb) AS CntLogin, FLATTEN(EdNotBuy.CntDate) AS CntDate;

Grp = GROUP CntLogin BY (uid, CntLogin, CntDate);
CntLogin = FOREACH Grp GENERATE FLATTEN(group);

EdLoginPerDayPro = FOREACH CntLogin GENERATE uid, CntLogin, CntDate, ((double)CntLogin/(double)CntDate) AS CntLoginPerDay;


----------------------------------------
--��pec�Q���t���O����
----------------------------------------
Joined = JOIN EdLoginPerDayPre BY uid, EdLoginPerDayPro BY uid USING 'replicated';

EdJoin = FOREACH Joined GENERATE
	EdLoginPerDayPre::group::uid AS uid,
	EdLoginPerDayPre::group::CntDate AS CntDatePre,
	EdLoginPerDayPre::CntLoginPerDay AS CntLoginPerDayPre, 
	EdLoginPerDayPro::CntLoginPerDay AS CntLoginPerDayPro
;

ResultFlag = FOREACH EdJoin GENERATE uid, CntDatePre, CntLoginPerDayPre, CntLoginPerDayPro, (CntLoginPerDayPro > CntLoginPerDayPre ? 1 : 0) AS pecFlag;


---------------------------------
--��kuchikomi�Ƃ��̃J�E���g
---------------------------------
--��verb����
Fil = FILTER Edit BY (cid == 8 OR cid == 7) 
			AND date > '$PROSTART_DATE' AND date < '$PROLAST_DATE' AND verb == 'pmp_commu:buzz';	--view:kuchikomi,view:favorite,cart:favorite,pmp_commu:buzz

FilDate = FILTER Edit BY (cid == 8 OR cid == 7)  AND date > '$PROSTART_DATE' AND date < '$PROLAST_DATE';

Grp = GROUP Fil BY uid;
CntVerb = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(Fil.verb) AS cntV;

GrpDate = GROUP FilDate By uid; 
CntDate = FOREACH GrpDate {
	cd = DISTINCT FilDate.date;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntDate;
}
Joined = JOIN CntVerb BY uid, CntDate BY uid USING 'replicated';

Ed = FOREACH Joined GENERATE
	CntVerb::uid AS uid,
	CntVerb::cntV AS cntV,
	CntDate::CntDate AS CntDate
;

ResultCntV = FOREACH Ed GENERATE uid, ((double)cntV/(double)CntDate) AS cntV, CntDate;

--session�n
Grp = GROUP FilData BY uid;
addSession = FOREACH Grp { 
    ord = ORDER FilData BY time ASC;
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

ResultSess = FOREACH grpUid  GENERATE FLATTEN(group) AS uid, COUNT(sessionTime.session_id) AS cntSession, 
					AVG(sessionTime.session_time) AS ave_session_time;

--join����
JoinedResult = JOIN ResultSess BY uid, ResultCntV BY uid USING 'replicated';

JoinedResult = FOREACH JoinedResult GENERATE
	ResultSess::uid AS uid,
	ResultSess::cntSession AS cntSession,
	ResultSess::ave_session_time AS ave_session_time,
	ResultCntV::cntV AS cntV,
	ResultCntV::CntDate AS CntDate
;

ResultIden = FOREACH JoinedResult GENERATE uid, ((double)cntSession/(double)CntDate) AS cntSess, ave_session_time, cntV, CntDate;


---------------------
--join
Joined = JOIN ResultFlag BY uid, ResultIden BY uid USING 'replicated'; 

Result = FOREACH Joined GENERATE
	ResultFlag::uid AS uid,
	ResultFlag::CntDatePre AS CntDatePre,
	ResultFlag::CntLoginPerDayPre AS CntLoginPerDayPre,
	ResultFlag::CntLoginPerDayPro AS CntLoginPerDayPro,
	ResultIden::cntSess AS cntSess,
	ResultIden::ave_session_time AS ave_session_time,
	ResultIden::cntV AS cntV,
	ResultFlag::pecFlag AS pecFlag
;

STORE Result INTO '$PATH_OUTPUT' USING PigStorage();

----------------------------------------
--��verb�̃J�E���g
----------------------------------------
--uid���Averb���ɃJ�E���g
--�C�x���g�O��verb
FilData = FILTER Edit BY (cid == 7 OR cid==8) AND date > '$START_DATE' AND date < '$LAST_DATE';
				
Grp = GROUP FilData BY (uid,verb);
CntVerb = FOREACH Grp {
	cv = FilData.verb;
	GENERATE FLATTEN(group) AS (uid,verb), COUNT(cv) AS VerbCnt;
}

Grp = GROUP FilData BY uid;
CntDate = FOREACH Grp {
	cd = DISTINCT FilData.date;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntD;
}

Joined = JOIN CntVerb BY uid, CntDate BY uid USING 'replicated';

EdPre = FOREACH Joined GENERATE
	CntVerb::uid AS uid,
	CntVerb::verb AS verb,
	CntVerb::VerbCnt AS VerbCnt,
	CntDate::CntD AS CntD
;

ResultVerb = FOREACH EdPre GENERATE uid, verb, VerbCnt , CntD, ((double)VerbCnt/(double)CntD) AS VerbPerDate; 

Joined = JOIN Result BY uid LEFT OUTER, ResultVerb BY uid USING 'replicated';
ResultVerb = FOREACH Joined GENERATE
	Result::uid AS uid,
	ResultVerb::verb AS verb,
	ResultVerb::VerbPerDate AS VerbPerDate
; 

STORE ResultVerb INTO '$PATH_OUTPUT_VERB' USING PigStorage();