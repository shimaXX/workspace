-----------------------------------------
--���ʐ��_���͂����邽�߂ɕK�v�ȃf�[�^�Z�b�g�̍\�z
--a���_���Ȃɂ��C�x���g������Ă��Ȃ�
--b���_��sprocket�����ƃL�����y�[���𓯎��ɍs�Ă��鎞��
--b���_�ɂ��āAEntry�������[�U��sprocket�Q�����[�U�Ƃ݂Ȃ��A
--Entry���Ă��Ȃ����[�U��sprocket�s�Q�����[�U�Ƃ݂Ȃ�
------�Ώۃ��[�U-----------
--a���_�W�v���ԑO��Entry�t���O���������[�U�݂̂�ΏۂƂ���
--�W�v����]���ϐ���session�񐔁Asession���ԁA���Ԗ������A�N�V������
-----------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-28' --�܂�29������̃f�[�^���擾����
%declare LAST_DATE  '2012-11-05' --�܂�4���܂ł̃f�[�^���擾����
%declare AXSTART_DATE  '2012-10-21' --�܂�22������̃f�[�^���擾����
%declare AXLAST_DATE  '2012-10-29' --�܂�28���܂ł̃f�[�^���擾����

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
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT_PreTotal 'works/output/Mining/Ci-LaboTotalVerbPre_Kutikomi';
%default PATH_OUTPUT_ProTotal 'works/output/Mining/Ci-LaboTotalVerbPro_Kutikomi';
%default PATH_OUTPUT_PreVerb 'works/output/Mining/Ci-LaboVerbPre_Kutikomi';
%default PATH_OUTPUT_ProVerb 'works/output/Mining/Ci-LaboVerbPro_Kutikomi';


RawData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--�ϐ��̍i�荞��
Edit = FOREACH RawData GENERATE ISOFormat(time) AS IsoTime ,SUBSTRING(time,0,10) AS time, uid, cid, GetMetaInfo(verb,ap) AS verb;

--------------------------------------
--�C�x���g�O�̃f�[�^�擾
--------------------------------------
--��verb����
FilPre = FILTER Edit BY (cid == 8 OR cid == 7) 
			AND time < '2012-12-16' AND time > '2012-12-03';-- AND verb == 'view:kuchikomi';	--view:favorite,cart:favorite

Grp = GROUP FilPre BY uid;
CntVerbPre = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPre.verb) AS cntV;

CntDatePre = FOREACH Grp {
	cd = DISTINCT FilPre.time;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntDate;
}
JoinPre = JOIN CntVerbPre BY uid, CntDatePre BY uid USING 'replicated';

EdPre = FOREACH JoinPre GENERATE
	CntVerbPre::uid AS uid,
	CntVerbPre::cntV AS cntV,
	CntDatePre::CntDate AS CntDate
;

EdPre = FOREACH EdPre GENERATE uid, ((double)cntV/(double)CntDate) AS cntV;

ResultPre = FOREACH EdPre GENERATE uid, cntV, (uid IS NULL ? 0: 0) as Z;

--------------------
--session�n
--sessionCnt
--�Z�b�V�����J�E���g
addSession = FOREACH Grp { 
    ord = ORDER FilPre BY IsoTime ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, SUBSTRING(IsoTime, 0, 10) AS date, IsoTime, session_id;

Grp = GROUP EditData BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER EditData  BY IsoTime ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.IsoTime)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpUid = GROUP sessionTime BY uid;  

ResultSessPre = FOREACH grpUid  GENERATE FLATTEN(group) AS uid, COUNT(sessionTime.session_id) AS cntSession, 
					AVG(sessionTime.session_time) AS ave_session_time;

JoinedResultPre = JOIN ResultSessPre BY uid, ResultPre BY uid USING 'replicated';

JoinedResultPre = FOREACH JoinedResultPre GENERATE
	ResultSessPre::uid AS uid,
	ResultSessPre::cntSession AS cntSession,
	ResultSessPre::ave_session_time AS ave_session_time,
	ResultPre::cntV AS cntV,
	ResultPre::Z AS Z
;

STORE JoinedResultPre INTO '$PATH_OUTPUT_PreTotal' USING PigStorage('\t');


--------------------------------------
--�C�x���g��̃f�[�^�擾
FilPro = FILTER Edit BY cid == 8
				AND time > '2012-12-15' AND time < '2013-01-17';-- AND verb == 'view:kuchikomi';	--view:favorite,cart:favorite;

Grp = GROUP FilPro BY uid;
CntVerbPro = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPro.verb) AS cntV;

CntDatePro = FOREACH Grp {
	cd = DISTINCT FilPro.time;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntDate;
}

JoinPro = JOIN CntVerbPro BY uid, CntDatePro BY uid USING 'replicated';

EdPro = FOREACH JoinPro GENERATE
	CntVerbPro::uid AS uid,
	CntVerbPro::cntV AS cntV,
	CntDatePro::CntDate AS CntDate
;

EdPro = FOREACH EdPro GENERATE uid, ((double)cntV/(double)CntDate) AS cntV;

ResultPro = FOREACH EdPro GENERATE uid, cntV, (uid IS NULL ? 1 : 1) AS Z;

--------------------
--session�n
--sessionCnt
--�Z�b�V�����J�E���g
addSession = FOREACH Grp { 
    ord = ORDER FilPro BY IsoTime ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, SUBSTRING(IsoTime, 0, 10) AS date, IsoTime, session_id;

Grp = GROUP EditData BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER EditData  BY IsoTime ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.IsoTime)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpUid = GROUP sessionTime BY uid;  

ResultSessPro = FOREACH grpUid  GENERATE FLATTEN(group) AS uid, COUNT(sessionTime.session_id) AS cntSession, 
					AVG(sessionTime.session_time) AS ave_session_time;

JoinedResultPro = JOIN ResultSessPro BY uid, ResultPro BY uid USING 'replicated';

JoinedResultPro = FOREACH JoinedResultPro GENERATE
	ResultSessPro::uid AS uid,
	ResultSessPro::cntSession AS cntSession,
	ResultSessPro::ave_session_time AS ave_session_time,
	ResultPro::cntV AS cntV,
	ResultPro::Z AS Z
;

STORE JoinedResultPro INTO '$PATH_OUTPUT_ProTotal' USING PigStorage('\t');

----------------------------------------
--uid���Averb���ɃJ�E���g
--�C�x���g�O��verb
FilPre = FILTER Edit BY (cid == 8 OR cid == 7)  
				AND time < '2012-12-16' AND time > '2012-12-03';
				
Grp = GROUP FilPre BY (uid,verb);
CntVerbByUPre = FOREACH Grp {
	cv = FilPre.verb;
	GENERATE FLATTEN(group) AS (uid,verb), COUNT(cv) AS VerbCnt;
}

Grp = GROUP FilPre BY uid;
CntDatePre = FOREACH Grp {
	cd = DISTINCT FilPre.time;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntDate;
}

JoinPre = JOIN CntVerbByUPre BY uid, CntDatePre BY uid USING 'replicated';

EdPre = FOREACH JoinPre GENERATE
	CntVerbByUPre::uid AS uid,
	CntVerbByUPre::verb AS verb,
	CntVerbByUPre::VerbCnt AS VerbCnt,
	CntDatePre::CntDate AS CntDate
;

ResultPre = FOREACH EdPre GENERATE uid, verb, ((double)VerbCnt/(double)CntDate) AS verbCnt;

STORE ResultPre INTO '$PATH_OUTPUT_PreVerb' USING PigStorage('\t');

--�C�x���g���verb
FilPro = FILTER Edit BY cid == 8
				AND time < '2013-01-17' AND time > '2012-12-15';
				
Grp = GROUP FilPro BY (uid,verb);
CntVerbByUPro = FOREACH Grp {
	cv = FilPro.verb;
	GENERATE FLATTEN(group) AS (uid,verb), COUNT(cv) AS VerbCnt;
}

Grp = GROUP FilPro BY uid;
CntDatePro = FOREACH Grp {
	cd = DISTINCT FilPro.time;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntDate;
}

JoinPro = JOIN CntVerbByUPro BY uid, CntDatePro BY uid USING 'replicated';

EdPro = FOREACH JoinPro GENERATE
	CntVerbByUPro::uid AS uid,
	CntVerbByUPro::verb AS verb,
	CntVerbByUPro::VerbCnt AS VerbCnt,
	CntDatePro::CntDate AS CntDate
;

ResultPro = FOREACH EdPro GENERATE uid, verb, ((double)VerbCnt/(double)CntDate) AS verbCnt;

STORE ResultPro INTO '$PATH_OUTPUT_ProVerb' USING PigStorage('\t');