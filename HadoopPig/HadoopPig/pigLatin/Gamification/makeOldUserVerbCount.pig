----------------------------------------------------
--sprocket導入前の会員のverbの数を導入後の数と比較する
--sprocket導入前に会員だったユーザのみ取ってくる
----------------------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-31' --つまり11/1日からのデータを取得する
%declare LAST_DATE  '2012-11-05' --つまり4日までのデータを取得する
%declare EXSTART_DATE  '2012-10-09' --つまり10日からのデータを取得する
%declare EXLAST_DATE  '2012-10-25' --つまり24日までのデータを取得する

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
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT_OLDUSER 'works/output/GAMIFICATION/oldUserTEST';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--Sessionizeは先頭にtimeが必要
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS days, uid, cid, verb;

-----------------------------------------------------
--まずはjoinの元となるテーブルを作成する
--EVAのみ、10/10以降、10/31までに会員に絞る（login, entry, mypage）
FilData = FILTER Edit BY cid == 3 AND days > '$EXSTART_DATE' AND days < '$EXLAST_DATE'
	AND (verb == 'login' OR verb == 'entry' OR verb == 'mypage');  

Grp = GROUP FilData BY (uid);

--joinの元となるuidテーブル
ResultOrg = FOREACH Grp { 
    GENERATE FLATTEN(group) AS uid; 
} 

-----------------------------------------------------------
--EVAのみ、10/10以降の会員のアクティビティを取得
FilData = FILTER Edit BY cid == 3 AND days > '$EXSTART_DATE';  

Grp = GROUP FilData BY (uid, days,verb);

--joinするテーブル
ResultEX = FOREACH Grp { 
    cntVerb = FilData.verb;
    GENERATE FLATTEN(group) AS (uid, days, verb), COUNT(cntVerb) AS cntVerb; 
} 

-----------------------------------------------------------
--EVAのみ、10/10以降の会員のDAUを取得
joinedData = JOIN ResultOrg BY uid LEFT OUTER , FilData BY uid USING 'replicated';

TMP = FOREACH joinedData GENERATE 
	FilData::uid AS uid,
	FilData::days AS days	
;

Grp = GROUP TMP BY (days);

--joinするテーブル
ResultDAU = FOREACH Grp { 
    UU = DISTINCT TMP.uid;
    GENERATE FLATTEN(group) AS days, COUNT(UU) AS DAU; 
} 

----------------------------------------------------
--ここからはjoin
joined = JOIN ResultOrg BY uid LEFT OUTER,ResultEX BY uid USING 'replicated';

--必要なcolumnだけ取得
Prior = FOREACH joined GENERATE
	ResultEX::uid AS uid,
	ResultEX::days AS days,
	ResultEX::verb AS verb,
	ResultEX::cntVerb AS cntVerb
;

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

STORE Result INTO '$PATH_OUTPUT_OLDUSER' USING PigStorage('\t');