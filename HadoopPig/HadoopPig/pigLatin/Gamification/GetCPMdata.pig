-----------------------------------------
--CPM�p�̃f�[�^����邽�߂̂�`��
-----------------------------------------

--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-12-18'
%declare LAST_DATE  '2013-02-04'
%declare AXSTART_DATE  '2012-10-21'
%declare AXLAST_DATE  '2012-10-29'

--�������߂̃p�����^
%declare BOUND  '13000'
%declare DAYS_BOUND '120' 

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
define MergeVerb myUDF.MergeVerb();
define GetIntervalDate myUDF.GetIntervalDate('$LAST_DATE');
define GetIntervalDateInd myUDF.GetIntervalDateIndividuals();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--���o�̓p�X�̒�`
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/Minig/GalsterCPM20130205';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--�Ώێ҂̍i�荞�݂��s��
Edit = FOREACH RowData GENERATE SUBSTRING(time, 0, 10) AS date, uid, cid,
	GetPayment(ap) AS payment,  verb;

FilData = FILTER Edit BY cid == 2;

-------------------------------
--���K�ƍŏI�K������擾
Grp = GROUP FilData BY uid;
VisitDate = FOREACH Grp GENERATE FLATTEN(group) AS uid, MIN(FilData.date) AS MinDate, MAX(FilData.date) AS MaxDate;

-------------------------------
--����w�����ƍŏI�w�������擾
Fil = FILTER FilData BY verb == 'buy';
Grp = GROUP Fil BY uid;
BuyDate = FOREACH Grp GENERATE FLATTEN(group) AS uid, MIN(Fil.date) AS MinBuy, MAX(Fil.date) AS MaxBuy, SUM(Fil.payment) AS payment;

-------------------------------
--�������Ă݂�
Joined = JOIN VisitDate BY uid LEFT OUTER , BuyDate BY uid;
Ed = FOREACH Joined GENERATE
	VisitDate::uid AS uid,
	VisitDate::MinDate AS MinDate,
	VisitDate::MaxDate AS MaxDate,
	BuyDate::MinBuy AS MinBuy,
	BuyDate::MaxBuy AS MaxBuy,
	BuyDate::payment AS payment
;

Ed = FOREACH Ed GENERATE uid, MinDate, MaxDate,
	(MinBuy IS NULL ? 'NULL' : MinBuy) AS MinBuy,
	(MaxBuy IS NULL ? 'NULL' : MaxBuy) AS MaxBuy,
	(payment IS NULL ? 0 : payment) AS payment
;

-------------------------------
--1 ���K����̌o��
--2 �ŏI�K�������̌o�ߓ���
--3 ����w��������̌o�ߓ���
--4���K����ŏI�w�����܂ł̊���
--5�ŏI�w��������̊���
--6����w�����܂ł̌o�ߓ���
--7�ݐύw���z

Clc = FOREACH Ed GENERATE
	uid,
	MinDate,
	MaxDate,
	MinBuy,
	MaxBuy,
	payment,
	GetIntervalDate(MinDate) AS TrmMinDate,
	GetIntervalDate(MaxDate) AS TrmMaxDate,
	GetIntervalDate(MinBuy) AS TrmMinBuy,
	GetIntervalDate(MaxBuy) AS TrmMaxBuy,
	GetIntervalDateInd(MinDate,MaxBuy) AS IntrvBuyDateFrmFirstVis,
	GetIntervalDateInd(MinDate,MinBuy) AS IntrvMinBuyDateFrmFirstVis
;
	
Result = FOREACH Clc GENERATE uid, MinDate, MaxDate, MinBuy, MaxBuy, payment,
			TrmMinDate, TrmMaxDate, TrmMinBuy, TrmMaxBuy, IntrvBuyDateFrmFirstVis, IntrvMinBuyDateFrmFirstVis,
			((int)TrmMaxDate < (int)'$DAYS_BOUND' AND (TrmMinBuy == 'NULL' OR TrmMinBuy == TrmMaxBuy) AND (int)TrmMinDate < 90 ? 1 : 0) AS FstGnk,
			((int)TrmMaxDate < (int)'$DAYS_BOUND' AND TrmMaxBuy != TrmMinBuy AND (int)TrmMinDate < 90 ? 1 : 0) AS YtytGnk,
			( ((int)TrmMinDate >=90 AND (int)TrmMinDate <=210) AND
				 (int)TrmMaxDate < (int)'$DAYS_BOUND' AND (int)payment >= (int)'$BOUND' ? 1 : 0 ) AS CrzGnk,
			( (int)TrmMinDate >=90 AND (int)TrmMaxDate < (int)'$DAYS_BOUND' AND (int)payment < (int)'$BOUND' ? 1 : 0 ) AS CtctGnk,
			( (int)TrmMinDate >=210 AND (int)TrmMaxDate < (int)'$DAYS_BOUND' AND (int)payment >= (int)'$BOUND' ? 1 : 0 ) AS RylGnk,
			
			( (int)TrmMaxDate >= (int)'$DAYS_BOUND' AND 
				(TrmMinBuy == 'NULL' OR (TrmMinBuy == TrmMaxBuy AND (int)TrmMinBuy >= (int)'$DAYS_BOUND')) ? 1 : 0) AS FstRdt,
			( (int)TrmMaxDate >= (int)'$DAYS_BOUND' AND 
				TrmMinBuy != 'NULL' AND TrmMinBuy != TrmMaxBuy
				AND ((int)TrmMaxBuy - (int)TrmMinDate) < 90 AND (int)TrmMaxBuy >= (int)'$DAYS_BOUND' ? 1 : 0) AS YtytRdt,
			( (int)TrmMaxDate >= (int)'$DAYS_BOUND' AND 
				((int)TrmMaxBuy - (int)TrmMinDate) >= 90 AND ((int)TrmMaxBuy - (int)TrmMinDate) < 210
				AND (int)TrmMaxBuy >= (int)'$DAYS_BOUND' AND (int)payment >= (int)'$BOUND' ? 1 : 0 ) AS CrzRdt,
			( (int)TrmMaxDate >= (int)'$DAYS_BOUND' AND 
				((int)TrmMaxBuy - (int)TrmMinDate) >=90 AND (int)TrmMaxBuy >= (int)'$DAYS_BOUND' AND (int)payment < (int)'$BOUND' ? 1 : 0 ) AS CtctRdt,
			( (int)TrmMaxDate >= (int)'$DAYS_BOUND' AND 
				((int)TrmMaxBuy -(int)TrmMinDate) >=210 AND (int)TrmMaxBuy >= (int)'$DAYS_BOUND' AND (int)payment >= (int)'$BOUND' ? 1 : 0 ) AS RylRdt
;

Ed = FOREACH Result GENERATE uid, (Long)payment, (Long)TrmMinDate, (Long)((Long)TrmMinDate - (Long)TrmMaxDate) AS Trm,
		(int)FstGnk, (int)YtytGnk, (int)CrzGnk, (int)CtctGnk, (int)RylGnk,
		(int)FstRdt, (int)YtytRdt, (int)CrzRdt, (int)CtctRdt, (int)RylRdt,
		(FstGnk == 1 ? 1:
			(YtytGnk == 1 ? 2:
				(CrzGnk == 1 ? 3:
					(CtctGnk == 1 ? 4:
						(RylGnk == 1 ? 5:
							(FstRdt == 1 ? 6:
								(YtytRdt == 1 ? 7:
									(CrzRdt == 1 ? 8:
										(CtctRdt == 1 ? 9:
											(RylRdt == 1 ? 10: 0
											)
										)
									)
								)
							)
						)
					)
				)
			)
		) AS SegFlag
;

Grp = GROUP Ed BY SegFlag;
CntRes = FOREACH Grp GENERATE FLATTEN(group), COUNT(Ed.uid), AVG(Ed.payment),  AVG(Ed.TrmMinDate), AVG(Ed.Trm), SUM(Ed.FstGnk), SUM(Ed.YtytGnk), SUM(Ed.CrzGnk),
			 SUM(Ed.CtctGnk), SUM(Ed.RylGnk), SUM(Ed.FstRdt), SUM(Ed.YtytRdt), SUM(Ed.CrzRdt), SUM(Ed.CtctRdt), SUM(Ed.RylRdt);

STORE CntRes INTO '$PATH_OUTPUT' USING PigStorage();