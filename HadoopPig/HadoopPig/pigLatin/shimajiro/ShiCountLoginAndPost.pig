--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-12-20' 

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategory myUDF.GetCategory();
define GetClient myUDF.GetClient();
define GetIntervalDate myUDF.GetIntervalDate('$START_DATE');
define GetSessionTime myUDF.GetSessionTime();

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/aws/2013-01-*.gz';
%default PATH_OUTPUT 'works/output/Shimajiro/CountLoginAndPost0117';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--�Ώێ҂̍i�荞�݂��s��
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS time, uid, cid, verb;
FilData01 = FILTER Edit BY cid == 5 AND time >= '$START_DATE' AND verb == 'entry';
FilData02 = FILTER Edit BY cid == 5 AND time >= '$START_DATE';

--Grp = COGROUP FilData01 BY (uid, verb);
Grp = COGROUP FilData02 BY (verb);
LL = FOREACH Grp GENERATE FLATTEN(group);


--filtered_matches = filter CoGrp by COUNT(sports_views) > �e0�f;


--LL = LIMIT CoGrp 10;
DUMP LL;
 

