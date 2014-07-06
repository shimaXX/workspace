-----------------------------------------
--1 daily�̃Z�b�V���������J�E���g
--2 daily�̃��O�C�������J�E���g
--3 1,2��join
--4 ���O�C����/�Z�b�V���������v�Z����
-----------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE '2012-10-09'

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCharacterCategory myUDF.GetCharacterCategory();
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/EVA/EvaCulucrateLoginRate1217';

--(1)-2�f�[�^�̑Ή��t���@10��
RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowData GENERATE ISOFormat(time) AS time, GetClient(ap) AS client, uid, verb, cid;

--(3) Eva�ɍi��B
FilteredData = FILTER EditData BY (cid == 3) AND (SUBSTRING(time, 0, 10) >= '$START_DATE');

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
Edit = FOREACH Sessionize GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) time�ŃO���[�v��
Grouped = GROUP Edit BY time;

--(9) session�񐔂��J�E���g
countSession = FOREACH Grouped { 
    countS = DISTINCT Edit.session_id; 
    GENERATE FLATTEN(group) AS date, (int)COUNT(countS) AS scnt; 
} 

-------------------------------------------
--�������܂ł�session���̃J�E���g�͏I��
--����������daily��login�����J�E���g����
Edit = FOREACH EditData GENERATE verb, SUBSTRING(time,0,10) AS date;

Filtered = FILTER Edit BY verb == 'login';

-- date�ŃO���[�v��
Grp = GROUP Filtered BY date;

-- login���̃J�E���g
CntLogin = FOREACH Grp {
	login = Filtered.verb;
	GENERATE FLATTEN(group) AS date, (double)COUNT(login) AS cntLogin;
}

-------------------------------------------
--��������join�ɓ���
Joined = JOIN countSession BY date LEFT OUTER, CntLogin BY date USING 'replicated'; 

--�f�[�^�̐��`
Ed = FOREACH Joined GENERATE 
	countSession::date AS date,
	countSession::scnt AS scnt,
	CntLogin::cntLogin AS cntLogin
; 

Result = FOREACH Ed GENERATE date, scnt, cntLogin, (double)(cntLogin/scnt) AS loginRate;

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');