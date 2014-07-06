-----------------------------------------
--�G���Q�[�W�����g�Z�o�ɗ��p���邽�߂̒l���擾
-----------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-12-18'
%declare LAST_DATE  '2013-01-14'
%declare AXSTART_DATE  '2012-10-21'
%declare AXLAST_DATE  '2012-10-29'

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
define GetIntervalDate myUDF.GetIntervalDate('$LAST_DATE');
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/Minig/Ci-LaboEngage_1218-0114';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--�Ώێ҂̍i�荞�݂��s��
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid,
	GetPayment(ap) AS payment,  GetMetaInfo(verb, ap) AS meta;
FilData01 = FILTER Edit BY (cid == 8 OR cid == 7) AND SUBSTRING(time,0,10)>= '$START_DATE' AND SUBSTRING(time,0,10)<= '$LAST_DATE';

--------------------------------------------
--------------------------------------------
--�y�܂���臒l���O�̃f�[�^���擾�z
--�Z�b�V�������̎擾---------------------------------
--(4) �s�v�ȗ�iclient, cid�j���폜
Ed = FOREACH FilData01 GENERATE time, uid, meta;

--(5) �Z�b�V����ID��U�邽�߂�uid�ŃO���[�v��
Grouped = GROUP Ed BY uid; 

--(6) �Z�b�V����ID�̐�����{time, uid, meta, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize01 = FOREACH Grouped { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) time��N�����ɒ����ė�̕��בւ�
Ed = FOREACH Sessionize01 GENERATE uid, meta, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) session�񐔂��J�E���g
GroupUid = GROUP Ed BY uid;

--(9) session�񐔂��J�E���g
ResultCountSession01 = FOREACH GroupUid { 
    countS = DISTINCT Ed.session_id; 
    GENERATE FLATTEN(group) AS uid, (int)COUNT(countS) AS scnt; 
} 


--�Z�b�V��������---------------------------------
--Sessionize�͐擪��time���K�v
--Ed�Ɏg�p����Ă���Sessionize�͏�̃Z�b�V�����񐔂��J�E���g����Ƃ��Ɏ��������
Ed = FOREACH Sessionize01 GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP Ed BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpUU = GROUP sessionTime BY uid;  

ResultSessionTime01 = FOREACH grpUU  GENERATE FLATTEN(group) AS uid, AVG(sessionTime.session_time) AS ave_session_time;


--�w�����z---------------------------------
Ed = FOREACH FilData01 GENERATE uid, payment;

Grp = GROUP Ed BY uid;

ResultPayment01 =  FOREACH Grp GENERATE FLATTEN(group) AS uid, SUM(Ed.payment) AS payment;


--�w����---------------------------------
--�g���ĂȂ�--
--Ed = FOREACH FilData01 GENERATE uid, verb;
--Fil = FILTER Ed BY verb == 'buy';
--Grp = GROUP Ed BY uid;
--ResultPayment01 =  FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(Ed.verb) AS cntBuy;


--���ԓ��ŏI�s�������擾����------------------------------------
--(2) �K�v�ȃf�[�^�ɍi��
Ed = FOREACH FilData01 GENERATE uid, cid, SUBSTRING(time, 0, 10) AS time;

--(3) galster�ɍi��Bsp�ɍi��B
FilteredData = FILTER Ed BY cid == 8;

--(4) �s�v�ȗ�iclient, cid�j���폜
Ed = FOREACH FilteredData GENERATE uid, time;

--(5) uid�ŃO���[�v��
Grouped = GROUP Ed BY (uid); 

getMaxStamp = FOREACH Grouped { 
    row_time = Ed.time; 
    GENERATE FLATTEN(group) AS uid, MAX(row_time) AS lastDate; 
}

ResultRecency01 = FOREACH getMaxStamp GENERATE uid, GetIntervalDate(lastDate) AS recency;


---------------------------------------------------
--���������join
--�Z�b�V�����񐔂ƃZ�b�V��������
joined0101 = JOIN ResultCountSession01 BY uid LEFT OUTER, ResultSessionTime01 BY uid USING 'replicated';

TMP0101 = FOREACH joined0101 GENERATE 
	ResultCountSession01::uid AS uid,
	ResultCountSession01::scnt AS scnt,
	ResultSessionTime01::ave_session_time AS ave_session_time 
;

joined0102 = JOIN TMP0101 BY uid LEFT OUTER, ResultPayment01 BY uid USING 'replicated';

TMP0102 = FOREACH joined0102 GENERATE 
	TMP0101::uid AS uid,
	TMP0101::scnt AS scnt,
	TMP0101::ave_session_time AS ave_session_time,
	ResultPayment01::payment AS payment
	--ResultPayment01::cntBuy AS cntBuy
;

joined0103 = JOIN TMP0102 BY uid LEFT OUTER, ResultRecency01 BY uid USING 'replicated';

Result01 = FOREACH joined0103 GENERATE 
	TMP0102::uid AS uid,
	TMP0102::scnt AS scnt,
	TMP0102::ave_session_time AS ave_session_time,
	TMP0102::payment AS payment,
	ResultRecency01::recency AS recency 
;


----------------------------------------------
--���R�~���j�e�B�֌W�w�W
--�R�~���j�e�B�ւ̓��e���̃J�E���g
----------------------------------------------
EdCom = FOREACH FilData01 GENERATE uid, meta;
--���R�~���e��
FilBz = FILTER EdCom BY meta == 'pmp_commu:buzz';

--���Y�݉񓚉�
FilCm = FILTER EdCom BY meta == 'pmp_commu:comment';

--���Y�ݓ��e��
FilNym = FILTER EdCom BY meta == 'pmp_commu:onayami';

--�x�X�g�A���T�[��܉�
FilBA = FILTER EdCom BY meta == 'pmp_commu:best_answer';

-------------
--�J�E���g
Grp = GROUP FilBz BY (uid,meta);
CntBz = FOREACH Grp GENERATE FLATTEN(group) AS (uid, meta), COUNT(FilBz.meta) AS cntBz;
Grp = GROUP FilCm BY (uid,meta);
CntCm = FOREACH Grp GENERATE FLATTEN(group) AS (uid, meta), COUNT(FilCm.meta) AS cntCm;
Grp = GROUP FilNym BY (uid,meta);
CntNym = FOREACH Grp GENERATE FLATTEN(group) AS (uid, meta), COUNT(FilNym.meta) AS cntNym;
Grp = GROUP FilBA BY (uid,meta);
CntBA = FOREACH Grp GENERATE FLATTEN(group) AS (uid, meta), COUNT(FilBA.meta) AS cntBA;

-------------
--RFM�n�w�W�Ƃ�join
JoinBz = JOIN Result01 BY uid LEFT OUTER, CntBz BY uid USING 'replicated';

ResultBz = FOREACH JoinBz GENERATE 
	Result01::uid AS uid,
	Result01::scnt AS scnt,
	Result01::ave_session_time AS ave_session_time,
	Result01::payment AS payment,
	Result01::recency AS recency,
	CntBz::cntBz AS cntBz
;

JoinCm = JOIN ResultBz BY uid LEFT OUTER, CntCm BY uid USING 'replicated';

ResultCm = FOREACH JoinCm GENERATE 
	ResultBz::uid AS uid,
	ResultBz::scnt AS scnt,
	ResultBz::ave_session_time AS ave_session_time,
	ResultBz::payment AS payment,
	ResultBz::recency AS recency,
	ResultBz::cntBz AS cntBz,
	CntCm::cntCm AS cntCm
;

JoinNym = JOIN ResultCm BY uid LEFT OUTER, CntNym BY uid USING 'replicated';

ResultNym = FOREACH JoinNym GENERATE 
	ResultCm::uid AS uid,
	ResultCm::scnt AS scnt,
	ResultCm::ave_session_time AS ave_session_time,
	ResultCm::payment AS payment,
	ResultCm::recency AS recency,
	ResultCm::cntBz AS cntBz,
	ResultCm::cntCm AS cntCm,
	CntNym::cntNym AS cntNym
;

JoinBA = JOIN ResultNym BY uid LEFT OUTER, CntBA BY uid USING 'replicated';

ResultBA = FOREACH JoinBA GENERATE 
	ResultNym::uid AS uid,
	ResultNym::scnt AS scnt,
	ResultNym::ave_session_time AS ave_session_time,
	ResultNym::payment AS payment,
	ResultNym::recency AS recency,
	ResultNym::cntBz AS cntBz,
	ResultNym::cntCm AS cntCm,
	ResultNym::cntNym AS cntNym,
	CntBA::cntBA AS cntBA
;


----------------------------------------------
--����Ƃւ̏���
--�A���P�[�g�񓚉񐔂̎擾�A�₢���킹�񐔂̎擾
----------------------------------------------
EdIg = FOREACH FilData01 GENERATE uid, meta;
--�A���P�[�g�񓚉�
FilIg = FILTER EdIg BY meta == 'pmp_commu:question';

Grp = GROUP FilIg BY (uid,meta);
ResultIg = FOREACH Grp GENERATE FLATTEN(group), COUNT(FilIg.meta) AS cntIg; 

--�R�~���j�e�B�n�w�W�Ƃ�join
Joined = JOIN ResultBA BY uid LEFT OUTER , ResultIg BY uid;

ResultIg = FOREACH Joined GENERATE 
	ResultBA::uid AS uid,
	ResultBA::scnt AS scnt,
	ResultBA::ave_session_time AS ave_session_time,
	ResultBA::payment AS payment,
	ResultBA::recency AS recency,
	ResultBA::cntBz AS cntBz,
	ResultBA::cntCm AS cntCm,
	ResultBA::cntNym AS cntNym,
	ResultBA::cntBA AS cntBA,
	ResultIg::cntIg AS cntIg
;

Result = FOREACH ResultIg GENERATE uid,
			(scnt IS NULL ? 0 : scnt) AS scnt,
			(ave_session_time IS NULL ? 0 : ave_session_time) AS ave_session_time,
			(payment IS NULL ? 0 : payment) AS payment,
			(recency IS NULL ? 0 : recency) AS recency,
			(cntBz IS NULL ? 0 : cntBz) AS cntBz,
			(cntCm IS NULL ? 0 : cntCm) AS cntCm,
			(cntNym IS NULL ? 0 : cntNym) AS cntNym,
			(cntBA IS NULL ? 0 : cntBA) AS cntBA
--			(cntIg IS NULL ? 0 : cntIg) AS cntIg
;

STORE Result INTO '$PATH_OUTPUT' USING PigStorage();