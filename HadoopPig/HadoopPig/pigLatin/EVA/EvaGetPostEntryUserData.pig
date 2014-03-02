------------------------------------------------
--Evaのリリースに合わせて11/1の前後一週間で
--10/23以前に行動履歴があり、かつ、11/1までentryしていないユーザで
--11/1以降に会員登録しているユーザ
--の11/1の前後1週間の行動データを調べる
------------------------------------------------

--変数への格納
%declare TIME_WINDOW  30m

%declare START_DATE  '2012-10-31' --つまり11/1日からのデータを取得する
%declare LAST_DATE  '2012-11-08' --つまり7日までのデータを取得する
%declare EXSTART_DATE  '2012-10-24' --つまり10/25日からのデータを取得する
%declare EXLAST_DATE  '2012-11-01' --つまり10/31日までのデータを取得する

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

--入出力パスの定義
%default PATH_INPUT_UID 'works/input/EvaEntryUser.txt';
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/GAMIFICATION/EVA/GetEntryPostVerb1107';
%default PATH_OUTPUT_ACTION 'works/output/GAMIFICATION/Action1107';
%default PATH_OUTPUT_UNI_ACT 'works/output/GAMIFICATION/UniAct1107';

---------------------------------------
--sprocketデータの取得
RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

---------------------------------------
--外部uidデータの取得
RowUidData = LOAD '$PATH_INPUT_UID' USING PigStorage() AS (
  uid:chararray)
;

--------------------------------------------
--sprocketデータを加工しuid毎にverbをカウントする
--(2) 必要なデータに絞る
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time, 0, 10) AS time;

--(3) EVAに絞る
FilteredData = FILTER EditData BY cid == 3 AND time > '$START_DATE' AND time < '$LAST_DATE';

--(4) 不要な列（cid）を削除
EditData = FOREACH FilteredData GENERATE uid, verb;

--(5) uid毎,verb毎の集計
Grouped = GROUP FilteredData BY (uid, verb); 

Result = FOREACH Grouped { 
    verb_count = FilteredData.verb; 
    GENERATE FLATTEN(group) AS (uid,verb), COUNT(verb_count) AS verbCnt; 
} 

--外部uidとjoinし、該当ユーザのみに絞る
joined = JOIN RowUidData BY uid LEFT OUTER, Result BY uid USING 'replicated' ; 

ResultFinal = FOREACH joined GENERATE 
	Result::uid AS uid,
	Result::verb AS verb,
	Result::verbCnt AS verbCnt
;

STORE ResultFinal INTO '$PATH_OUTPUT' using PigStorage('\t');