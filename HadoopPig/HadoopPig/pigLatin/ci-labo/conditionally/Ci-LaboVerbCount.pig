------------------------------------
--各ユーザ毎にverbの回数をカウントする
------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare EXSTART_DATE '2012-11-07' --ci-laboは11/8からの集計を行う
%declare EXLAST_DATE  '2012-11-20' --つまり19日までのデータを取得する
%declare START_DATE  '2012-11-19' --つまり20日からのデータを取得する
%declare LAST_DATE  '2012-12-04' --つまり03日までのデータを取得する

--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategory myUDF.GetCategory();
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT_OCT 'works/input/ci-labo/';
%default PATH_OUTPUT 'works/output/Ci-Labo/Ci-LaboVerbCount1203';

--(1)-2データの対応付け
RowData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time,0,10) AS time;

--(3) ci-laboに絞る
FilteredDataPrior = FILTER EditData BY cid == 4 AND time > '$EXSTART_DATE' AND time < '$EXLAST_DATE';
FilteredDataPost = FILTER EditData BY cid == 4 AND time > '$START_DATE' AND time < '$LAST_DATE';

--(4) 不要な列（cid）を削除
EditDataPrior = FOREACH FilteredDataPrior GENERATE uid, verb;
EditDataPost = FOREACH FilteredDataPost GENERATE uid, verb;

--(5) 集計対象者を絞るためのuid毎,verb毎の集計
Grouped = GROUP EditDataPrior BY uid; 

CntPrior = FOREACH Grouped { 
    verb_count = EditDataPrior.verb; 
    GENERATE FLATTEN(group) AS uid, COUNT(verb_count) AS verbCnt; 
} 

FilteredPrior = FILTER CntPrior BY verbCnt > 0 ;
ResultPrior = FOREACH FilteredPrior GENERATE uid; 

-----------------------------------------------------------
--(6) 集計用のuid毎,verb毎の集計
Grouped = GROUP EditDataPost BY (uid, verb); 

ResultPost = FOREACH Grouped { 
    verb_count = EditDataPost.verb; 
    GENERATE FLATTEN(group) AS (uid,verb), COUNT(verb_count) AS verbCnt; 
} 

--(7) 集計対象者用のデータのみに絞る(join)
Joined = join ResultPrior BY uid LEFT OUTER, ResultPost BY uid USING 'replicated';

--(8) データの取捨選択
Result = FOREACH Joined GENERATE 
	ResultPrior::uid AS uid,
	ResultPost::verb AS verb,
	ResultPost::verbCnt AS verbCnt
;

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');