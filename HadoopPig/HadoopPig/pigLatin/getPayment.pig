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
define GetPayment myUDF.GetPayment();

--���o�̓p�X�̒�`
--%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/oct/';
%default PATH_OUTPUT 'works/output/GalsterPayment1025';

--(1)-2�f�[�^�̑Ή��t���@10��
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

EditData = FOREACH RowOctData GENERATE uid, cid, SUBSTRING(time, 0, 10) AS days, GetClient(ap) AS client, GetPayment(ap) AS payment;

FilteredData = FILTER EditData BY (cid == 2) AND (client == 'sp') AND (days > '2012-10-17') AND (days < '2012-10-25');

Grouped = GROUP FilteredData BY (uid); 

Result01 = FOREACH Grouped { 
    spay = FilteredData.payment; 
    GENERATE FLATTEN(group), SUM(spay) AS totalPay; 
} 

STORE Result01 INTO '$PATH_OUTPUT' using PigStorage('\t');