----------------------------------------------------
--sprocket導入前の会員のverbの数を導入後の数と比較する
--sprocket導入後にアクションを開始したユーザのみを拾ってくる
----------------------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-31' --つまり11/1日からのデータを取得する

--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
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

--入出力パスの定義
--%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT_AWS 'works/input/aws/2012-11-*.gz';
%default PATH_OUTPUT_NEWUSER 'works/output/GAMIFICATION/newEntryUser';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionizeは先頭にtimeが必要
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS days, uid, cid, verb;

--Evaで11/1からのデータに絞る
FilData = FILTER Edit BY cid == 3 AND days > '$START_DATE' AND verb == 'entry';


--それぞれのuserの行動日の最小値を求めるためにuidでグループ化
Grp = GROUP FilData BY uid;

--それぞれのuserの行動日の最小値を求める
getEntryUser = FOREACH Grp {
	GENERATE FLATTEN(group) AS uid;
}

---------------------------------
--join元のデータを作る（普通にverbをカウントする）
FilData = FILTER Edit BY cid == 3 AND days > '$START_DATE';
Grp = GROUP FilData BY (uid, days, verb);

getData = FOREACH Grp {
	verb = FilData.verb;
	GENERATE FLATTEN(group) AS (uid, days, verb), COUNT(verb) AS cntVerb;
}

-----------------------------------------------------------
--EVAのみ、11/1以降の会員のDAUを取得
FilData = FILTER Edit BY cid == 3 AND days > '$START_DATE';  

joined = JOIN getEntryUser BY uid LEFT OUTER, FilData BY uid USING 'replicated'; 

TMP = FOREACH joined GENERATE 
	FilData::uid AS uid,
	FilData::days AS days
;

Grp = GROUP TMP BY (days);

--joinするテーブル
ResultDAU = FOREACH Grp { 
    UU = DISTINCT TMP.uid;
    GENERATE FLATTEN(group) AS days, COUNT(UU) AS DAU; 
} 

------------------------------------
--ここからはjoinする
joinedData = JOIN getEntryUser BY uid LEFT OUTER, getData BY uid USING 'replicated';

TMP = FOREACH joinedData GENERATE
	getData::uid AS uid,
	getData::days AS days,
	getData::verb AS verb,
	getData::cntVerb AS cntVerb
;

Prior = FOREACH TMP GENERATE uid, days, verb, cntVerb;

Grp  = GROUP Prior BY (days,verb);

--date,verb毎の集計を行う
ResultVerb = FOREACH Grp {
	sVerb = Prior.cntVerb;
	GENERATE FLATTEN(group) AS (days, verb), FLATTEN(SUM(sVerb)) AS sumVerb;
}

---------------------------------
--DAUをjoinし平均値を求める
joined = JOIN ResultVerb BY days ,ResultDAU BY days USING 'replicated';

--必要なcolumnだけ取得
Prior = FOREACH joined GENERATE
	ResultVerb::days AS days,
	ResultVerb::verb AS verb,
	ResultVerb::sumVerb AS sumVerb,
	ResultDAU::DAU AS DAU
;

--calculate average count of verbs
Result = FOREACH Prior GENERATE days, verb, sumVerb, DAU,(double)((double)sumVerb/(double)DAU) AS avgVerb;

STORE Result INTO '$PATH_OUTPUT_NEWUSER' USING PigStorage('\t'); 