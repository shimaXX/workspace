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
%default PATH_OUTPUT_OLDUSER 'works/output/GAMIFICATION/test';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

EditData = FOREACH RowData GENERATE
	uid, cid, verb, SUBSTRING(time, 0, 10) AS days;

FilteredData = FILTER EditData BY (cid == 3) AND (days > '$EXSTART_DATE') AND uid == 'eva506a48daae05e';

---------------------------------
--アクティビティ数の取得_try
GrpVerb = GROUP FilteredData BY (days);

ResultVerb = FOREACH GrpVerb { 
    cntVerb = FilteredData.verb;
    GENERATE FLATTEN(group) AS days, COUNT(cntVerb) AS cntDailyVerb; 
} 

STORE ResultVerb INTO '$PATH_OUTPUT_OLDUSER' USING PigStorage('\t');