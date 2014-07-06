-----------------------------------------
--sprocket導入からの購買総額をユーザ毎に算出する
-----------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-12-18'
%declare LAST_DATE  '2013-01-14'
%declare AXSTART_DATE  '2012-10-21'
%declare AXLAST_DATE  '2012-10-29'

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
define MergeVerb myUDF.MergeVerb();
define GetIntervalDate myUDF.GetIntervalDate('$LAST_DATE');
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/Minig/GalsterPayment20130204';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--対象者の絞り込みを行う
Edit = FOREACH RowData GENERATE SUBSTRING(time, 0, 10) AS date, uid, cid,
	GetPayment(ap) AS payment, verb;
FilData = FILTER Edit BY cid == 2 AND verb == 'buy';

Grp = GROUP FilData BY uid;
PYM = FOREACH Grp GENERATE FLATTEN(group) AS uid, SUM(FilData.payment) AS payment; 

STORE PYM INTO '$PATH_OUTPUT' USING PigStorage();