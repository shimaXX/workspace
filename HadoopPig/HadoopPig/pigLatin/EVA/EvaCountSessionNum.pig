--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCharacterCategory myUDF.GetCharacterCategory();
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
--%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/aws/';
%default PATH_OUTPUT 'works/output/EVA/EvaCountSessionNum1025';

--(1)-2�f�[�^�̑Ή��t���@10��
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowOctData GENERATE ISOFormat(time) AS time, GetClient(ap) AS client, uid, verb, cid;

--(3) Eva�ɍi��B
FilteredData = FILTER EditData BY (cid == 3) AND (SUBSTRING(time, 0, 10) >= '2012-10-25');

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