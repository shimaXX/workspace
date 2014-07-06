----------------------------------------
--���ԓ�session��
--���ԓ�����session����
--���ԓ��w�����z �� ��肭�l���o�Ȃ����߁A�œK���֐��ɂ��œK��_���iannealingOprimize�j
--���Ԗ��Ɗ��ԓ��̍ŏI�A�N�V�������̍�
----------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m

%declare START_DATE  '2012-10-31' --�܂�11/1������̃f�[�^���擾����
%declare LAST_DATE  '2012-11-15' --�܂�14���܂ł̃f�[�^���擾����
%declare EXSTART_DATE  '2012-10-17' --�܂�10/18������̃f�[�^���擾����
%declare EXLAST_DATE  '2012-11-01' --�܂�10/31���܂ł̃f�[�^���擾����


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
define GetPriorIntervalDate myUDF.GetIntervalDate('$EXLAST_DATE');
define GetPostIntervalDate myUDF.GetIntervalDate('$LAST_DATE');

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT_PRIOR 'works/output/GAMIFICATION/EVA/RFMpriorCnt1122';
%default PATH_OUTPUT_POST 'works/output/GAMIFICATION/EVA/RFMpostCnt1122';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

EditData = FOREACH RowData GENERATE uid, cid, verb, ISOFormat(time) AS time,GetPayment(ap) AS payment, SUBSTRING(time,0,10) AS days;

FilData01 = FILTER EditData BY cid ==3 AND days > '$EXSTART_DATE' AND days < '$EXLAST_DATE';
FilData02 = FILTER EditData BY cid ==3 AND days > '$START_DATE' AND days < '$LAST_DATE';

--------------------------------------------
--------------------------------------------
--�y�܂���臒l���O�̃f�[�^���擾�z
--�Z�b�V�������̎擾---------------------------------
--(4) �s�v�ȗ�iclient, cid�j���폜
Ed = FOREACH FilData01 GENERATE time, uid, verb;

--(5) �Z�b�V����ID��U�邽�߂�uid�ŃO���[�v��
Grouped = GROUP Ed BY uid; 

--(6) �Z�b�V����ID�̐�����{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
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
--Ed = FOREACH FilData01 GENERATE uid, verb;

--Fil = FILTER Ed BY verb == 'buy';

--Grp = GROUP Ed BY uid;

--ResultPayment01 =  FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(Ed.verb) AS cntBuy;


--���ԓ��ŏI�s�������擾����------------------------------------
--(2) �K�v�ȃf�[�^�ɍi��
Ed = FOREACH FilData01 GENERATE uid, cid, SUBSTRING(time, 0, 10) AS time;

--(3) galster�ɍi��Bsp�ɍi��B
FilteredData = FILTER Ed BY cid == 3;

--(4) �s�v�ȗ�iclient, cid�j���폜
Ed = FOREACH FilteredData GENERATE uid, time;

--(5) uid�ŃO���[�v��
Grouped = GROUP Ed BY (uid); 

getMaxStamp = FOREACH Grouped { 
    row_time = Ed.time; 
    GENERATE FLATTEN(group) AS uid, MAX(row_time) AS lastDate; 
}

--��`�̒i�K��terminal��+1�������t�������Ă��邽�߁A-1����
ResultRecency01 = FOREACH getMaxStamp GENERATE uid, GetPriorIntervalDate(lastDate) - 1.0 AS recency;


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
	--TMP0102::cntBuy AS cntBuy,
	ResultRecency01::recency AS recency 
;



--------------------------------------------
--------------------------------------------
--�y臒l����̃f�[�^���擾�z
--�Z�b�V�������̎擾---------------------------------
--(4) �s�v�ȗ�iclient, cid�j���폜
Ed = FOREACH FilData02 GENERATE time, uid, verb;

--(5) �Z�b�V����ID��U�邽�߂�uid�ŃO���[�v��
Grouped = GROUP Ed BY uid; 

--(6) �Z�b�V����ID�̐�����{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize02 = FOREACH Grouped { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) time��N�����ɒ����ė�̕��בւ�
Ed = FOREACH Sessionize02 GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) session�񐔂��J�E���g
GroupUid = GROUP Ed BY uid;

--(9) session�񐔂��J�E���g
ResultCountSession02 = FOREACH GroupUid { 
    countS = DISTINCT Ed.session_id; 
    GENERATE FLATTEN(group) AS uid, (int)COUNT(countS) AS scnt; 
} 


--�Z�b�V��������---------------------------------
--Sessionize�͐擪��time���K�v
--Ed�Ɏg�p����Ă���Sessionize�͏�̃Z�b�V�����񐔂��J�E���g����Ƃ��Ɏ��������
Ed = FOREACH Sessionize02 GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP Ed BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpDaily = GROUP sessionTime BY uid;  

ResultSessionTime02 = FOREACH grpDaily  GENERATE FLATTEN(group) AS uid, AVG(sessionTime.session_time) AS ave_session_time;


--�w�����z---------------------------------
Ed = FOREACH FilData02 GENERATE uid, payment;

Grp = GROUP Ed BY uid;

ResultPayment02 =  FOREACH Grp GENERATE FLATTEN(group) AS uid, SUM(Ed.payment) AS payment;


--�w����---------------------------------
--Ed = FOREACH FilData02 GENERATE uid, verb;

--Fil = FILTER Ed BY verb == 'buy';

--Grp = GROUP Ed BY uid;

--ResultPayment02 =  FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(Ed.verb) AS cntBuy;


--���ԓ��ŏI�s�������擾����------------------------------------
--(2) �K�v�ȃf�[�^�ɍi��
Ed = FOREACH FilData02 GENERATE uid, cid, SUBSTRING(time, 0, 10) AS time;

--(3) galster�ɍi��Bsp�ɍi��B
FilteredData = FILTER Ed BY cid == 3;

--(4) �s�v�ȗ�iclient, cid�j���폜
Ed = FOREACH FilteredData GENERATE uid, time;

--(5) uid�ŃO���[�v��
Grouped = GROUP Ed BY (uid); 

getMaxStamp = FOREACH Grouped { 
    row_time = Ed.time; 
    GENERATE FLATTEN(group) AS uid, MAX(row_time) AS lastDate; 
}

--��`�̒i�K��terminal��+1�������t�������Ă��邽�߁A-1����
ResultRecency02 = FOREACH getMaxStamp GENERATE uid, GetPostIntervalDate(lastDate) - 1.0 AS recency;


---------------------------------------------------
--���������join
--�Z�b�V�����񐔂ƃZ�b�V��������
joined0201 = JOIN ResultCountSession02 BY uid LEFT OUTER, ResultSessionTime02 BY uid USING 'replicated';

TMP0201 = FOREACH joined0201 GENERATE 
	ResultCountSession02::uid AS uid,
	ResultCountSession02::scnt AS scnt,
	ResultSessionTime02::ave_session_time AS ave_session_time 
;

joined0202 = JOIN TMP0201 BY uid LEFT OUTER, ResultPayment02 BY uid USING 'replicated';

TMP0202 = FOREACH joined0202 GENERATE 
	TMP0201::uid AS uid,
	TMP0201::scnt AS scnt,
	TMP0201::ave_session_time AS ave_session_time,
	ResultPayment02::payment AS payment
	--ResultPayment02::cntBuy AS cntBuy  
;

joined0203 = JOIN TMP0202 BY uid LEFT OUTER, ResultRecency02 BY uid USING 'replicated';

Result02 = FOREACH joined0203 GENERATE 
	TMP0202::uid AS uid,
	TMP0202::scnt AS scnt,
	TMP0202::ave_session_time AS ave_session_time,
	TMP0202::payment AS payment,
	--TMP0202::cntBuy AS cntBuy,
	ResultRecency02::recency AS recency 
;



------------------------------------------------
------------------------------------------------
--�O�ƌ��inner join���O�̃��[�U�ɍ��킹��
--session time�����郆�[�U������filter����
--����ɑO�ƌ�ɕ�������
jnd = JOIN Result01 BY uid , Result02 BY uid USING 'replicated';  

TMP = FOREACH jnd GENERATE 
	Result01::uid AS uid,
	Result01::scnt AS scntPrior,
	Result01::ave_session_time AS sessionTimePrior,
	Result01::payment AS paymentPrior,
	--Result01::cntBuy AS cntBuyPrior,
	Result01::recency AS recencyPrior,
	Result02::scnt AS scntPost,
	Result02::ave_session_time AS sessionTimePost,
	Result02::payment AS paymentPost,
	--Result02::cntBuy AS cntBuyPost,
	Result02::recency AS recencyPost
;

Fil = FILTER TMP BY (chararray)sessionTimePrior != '' AND (chararray)sessionTimePost != '';

--�w�����z�p
ResultPrior = FOREACH Fil GENERATE uid, scntPrior, sessionTimePrior, paymentPrior, recencyPrior;
ResultPost = FOREACH Fil GENERATE uid, scntPost, sessionTimePost, paymentPost, recencyPost;

--�w���񐔗p
--ResultPrior = FOREACH Fil GENERATE uid, scntPrior, sessionTimePrior, cntBuyPrior, recencyPrior;
--ResultPost = FOREACH Fil GENERATE uid, scntPost, sessionTimePost, cntBuyPost, recencyPost;


---------------------------------------------------
--�f�[�^�o��
STORE ResultPrior INTO '$PATH_OUTPUT_PRIOR' USING PigStorage('\t');
STORE ResultPost INTO '$PATH_OUTPUT_POST' USING PigStorage('\t');