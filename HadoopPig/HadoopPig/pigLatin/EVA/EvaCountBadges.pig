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
define GetMetaInfo myUDF.GetMetaInfo(); 
define GetNextDate myUDF.GetNextDate();
define GetRewards myUDF.GetRewards();
define CountBadges myUDF.CountBadges();

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/aws/2012-11-*.gz';
%default PATH_OUTPUT 'works/output/GAMIFICATION/badges1104';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray,f6,rb:chararray)
;

--rewards�̂ݎ���Ă���Brewards����̏ꍇ��NULL�Ƃ��Ă���B
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS time, cid, GetRewards(rb) AS badges;

FilData = FILTER Edit BY (cid == 3) AND (time >= '2012-11-01');

Grp = GROUP FilData BY time;

Result = FOREACH Grp GENERATE group ,FLATTEN(CountBadges(FilData.badges));

STORE Result INTO '$PATH_OUTPUT' USING PigStorage();