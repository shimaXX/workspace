-----------------------------------------
--�Z�b�V�������Ԃ̕��ϒl�����߂�pig script
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

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT_TIME 'works/output/GAMIFICATION/sessonTime';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionize�͐擪��time���K�v
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid;

FilData = FILTER Edit BY cid == 3;

Grp = GROUP FilData BY uid;

addSession = FOREACH Grp { 
    ord = ORDER FilData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP EditData BY (date, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(group) AS (date ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpDaily = GROUP sessionTime BY date;  

aveDailySessionTime = FOREACH grpDaily  GENERATE FLATTEN(group) AS date, AVG(sessionTime.session_time) AS ave_session_time;

STORE aveDailySessionTime INTO '$PATH_OUTPUT_TIME' USING PigStorage('\t'); 