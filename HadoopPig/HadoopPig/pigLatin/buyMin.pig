--���o�̓p�X�̒�`
%default PATH_INPUT 'works/input/';
%default PATH_OUTPUT 'works/output/galster_buyMin_sec';
--data/log_queue_activities_20120*xx.csv.gz

--(1)�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;
  
--(2)verb=buy��filter
FilteredTMP = FILTER RowData BY cid == 2;
FilteredData = FILTER FilteredTMP BY verb == 'buy';

--(3)filter�����f�[�^�̐��`
EditTMP = FOREACH FilteredTMP GENERATE uid, SUBSTRING(time, 0, 10) AS time;
EditData = FOREACH FilteredData GENERATE uid, SUBSTRING(time, 0, 10) AS time;

--(4)uid�ŃO���[�v��
GrpBuyUidData = GROUP EditData BY (uid); 

--(5)user����buy��min�����
BuyMinData = FOREACH GrpBuyUidData {  
  RowTime = EditData.time; 
  GENERATE FLATTEN(group) AS uid, (chararray)MIN(RowTime) AS minBuyTime; 
}

------------------���������action��minTime�̌���
--(6)uid�ŃO���[�v��
GrpUidData = GROUP EditTMP BY (uid); 

--(7)user����time��min�����
MinData = FOREACH GrpUidData {  
  RowTime02 = EditTMP.time;
  GENERATE FLATTEN(group) AS uid, (chararray)MIN(RowTime02) AS minTime; 
}

------------------���������join
--(8)buy�ōi�������[�U�ƍi���Ă��Ȃ�time��join
JoinedData = JOIN
 BuyMinData BY uid,
 MinData BY uid
 USING 'replicated'
;
 
ResultData = FOREACH JoinedData GENERATE 
  MinData::uid AS uid,
  BuyMinData::minBuyTime AS minBuyTime,
  MinData::minTime AS minTime
;
 
 STORE ResultData INTO '$PATH_OUTPUT' USING PigStorage('\t');