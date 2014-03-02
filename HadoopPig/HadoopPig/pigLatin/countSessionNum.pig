--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
--%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/oct/';
%default PATH_OUTPUT 'works/output/GalsterSession1024';

--(1)�f�[�^�̑Ή��t��
--RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
--  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
--;

--(1)-2�f�[�^�̑Ή��t���@10��
RowData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE ISOFormat(time) AS time, GetClient(ap) AS client, uid, verb, cid;

--(3) galster�ɍi��Bsp�ɍi��B
FilteredData = FILTER EditData BY (cid == 2) AND (client == 'sp')
    AND (SUBSTRING(time, 0, 10) >= '2012-10-18') AND (SUBSTRING(time, 0, 10) < '2012-10-25');

--(4) �s�v�ȗ�iclient, cid�j���폜
EditData = FOREACH FilteredData GENERATE time, uid, verb;

--(5) �Z�b�V����ID��U�邽�߂�uid�ŃO���[�v��
Grouped = GROUP EditData BY uid; 

--(6) �Z�b�V����ID�̐�����{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize = FOREACH Grouped { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) time��N�����ɒ����ė�̕��בւ�
EditData = FOREACH Sessionize GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) uid�ŃO���[�v��
GroupUid = GROUP EditData BY uid;

--(9) session�񐔂��J�E���g
countSession = FOREACH GroupUid { 
    countS = DISTINCT EditData.session_id; 
    GENERATE FLATTEN(group), (int)COUNT(countS) AS scnt; 
} 

STORE countSession INTO '$PATH_OUTPUT' using PigStorage('\t');