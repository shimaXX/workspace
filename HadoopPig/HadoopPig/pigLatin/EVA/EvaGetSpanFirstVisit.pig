----------------------------------------------------
--sprocket�����O�̉����verb�̐��𓱓���̐��Ɣ�r����
--sprocket������ɃA�N�V�������J�n�������[�U�݂̂��E���Ă���
----------------------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare OCT_START_DATE  '2012-09-30' --�܂�10/1������̃f�[�^���擾����
%declare NOV_START_DATE  '2012-10-31' --�܂�11/1������̃f�[�^���擾����
%declare DEC_START_DATE  '2012-11-30' --�܂�12/1������̃f�[�^���擾����

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
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/EVA/EvaSpanFirstVisit1217';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionize�͐擪��time���K�v
Edit = FOREACH RowData GENERATE time, uid, cid, verb, SUBSTRING(time,0,7) AS month;

--�f�[�^�ɍi��
FilData = FILTER Edit BY cid == 3 AND time > '$OCT_START_DATE';

--�s�v�ȃJ�������폜
EditData = FOREACH FilData GENERATE uid, time, verb, month;


--------------------------------------------
--entry�̂��郆�[�U�ɍi��ijoin�̑匳�j
entryUser = FILTER EditData BY verb == 'entry';
entryUser = FOREACH entryUser GENERATE uid, time;


--------------------------------------------
--verb�̍ŏ����������߂�
Grp = GROUP EditData BY uid;
minActTime = FOREACH Grp GENERATE FLATTEN(group) AS uid, MIN(EditData.time) AS minTime; 


--------------------------------------------
--buy�̍ŏ�����
onlyBuy = FILTER EditData BY verb == 'buy';
Grp = GROUP onlyBuy BY uid;
minBuyTime = FOREACH Grp GENERATE FLATTEN(group) AS uid, MIN(onlyBuy.time) AS buyTime; 


--------------------------------------------
--mail_magagin_reg�̍ŏ�����
onlyMail = FILTER EditData BY verb == 'mail_magazine_reg';
Grp = GROUP onlyMail BY uid;
minMailTime = FOREACH Grp GENERATE FLATTEN(group) AS uid, MIN(onlyMail.time) AS mailTime; 


--------------------------------------------
--join
--entry��verbMin
Joined01 = JOIN entryUser BY uid , minActTime BY uid;
Result01 = FOREACH Joined01 GENERATE
	entryUser::uid AS uid,
	entryUser::time AS time,
	minActTime::minTime AS minActTime
;

--result01�ƍŏ��w����
Joined02 = JOIN Result01 BY uid , minBuyTime BY uid;
Result02 = FOREACH Joined02 GENERATE
	Result01::uid AS uid,
	Result01::time AS time,
	Result01::minActTime AS minActTime,
	minBuyTime::buyTime AS buyTime
;

--result01�ƃ����}�K�o�^��
Joined03 = JOIN Result02 BY uid , minMailTime BY uid;
Result03 = FOREACH Joined03 GENERATE
	Result02::uid AS uid,
	Result02::minActTime AS minActTime,
	Result02::time AS entryTime,
	Result02::buyTime AS buyTime,
	minMailTime::mailTime AS mailTime
;

STORE Result03 INTO '$PATH_OUTPUT' USING PigStorage('\t'); 