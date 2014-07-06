--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-09' --�܂�29������̃f�[�^���擾����
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
define GetMetaInfo myUDF.GetMetaInfo(); 
define GetNextDate myUDF.GetNextDate();
define GetRewards myUDF.GetRewards();
--define CountBadges myUDF.TestCountBadges();
define CountBadges myUDF.CountBadges();
define TestTmp myUDF.TestTmp();

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/test/2012-12-20*';
%default PATH_OUTPUT 'works/output/TEST/EvaBadgeTime1209';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray,f6,rb:chararray)
;

--rewards�̂ݎ���Ă���Brewards����̏ꍇ��NULL�Ƃ��Ă���B
Edit = FOREACH RowData GENERATE uid, SUBSTRING(time,0,10) AS time, cid, GetRewards(rb) AS badges;

FilData = FILTER Edit BY (cid == 7 OR cid==8) AND time > '$START_DATE';

Grp = GROUP FilData BY (uid,time);

Result = FOREACH Grp GENERATE FLATTEN(group) AS (uid,time) ,FLATTEN(CountBadges(FilData.badges)) AS (RN ,CntBdg);

STORE Result INTO '$PATH_OUTPUT' USING PigStorage();