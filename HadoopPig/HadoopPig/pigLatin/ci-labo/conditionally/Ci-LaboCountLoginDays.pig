-----------------------------------------
--login日数を求めるpig script
-----------------------------------------
--変数への格納
%declare TIME_WINDOW  30m
%declare EXSTART_DATE '2012-11-07' --ci-laboは11/8からの集計を行う
%declare EXLAST_DATE  '2012-11-20' --つまり19日までのデータを取得する
%declare START_DATE  '2012-11-19' --つまり20日からのデータを取得する
%declare LAST_DATE  '2012-12-04' --つまり03日までのデータを取得する

--UDFの定義
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT 'works/input/ci-labo/';
%default PATH_OUTPUT 'works/output/Ci-Labo/Ci-LaboCountLoginDays1203';

--(1)データの対応付け
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time, 0, 10) AS days;

--(3) galsterに絞る。spに絞る。
FilteredDataPrior = FILTER EditData BY cid == 4 AND days > '$EXSTART_DATE' AND days < '$EXLAST_DATE';
FilteredDataPost = FILTER EditData BY cid == 4 AND days > '$START_DATE' AND days < '$LAST_DATE';

--(4) 不要な列（cid）を削除
EditDataPrior = FOREACH FilteredDataPrior GENERATE uid, verb;
EditDataPost = FOREACH FilteredDataPost GENERATE days, uid;

--(5) 集計対象者を絞るためのuid毎,verb毎の集計
Grouped = GROUP EditDataPrior BY uid; 

CntPrior = FOREACH Grouped { 
    verb_count = EditDataPrior.verb; 
    GENERATE FLATTEN(group) AS uid, COUNT(verb_count) AS verbCnt; 
} 

FilteredPrior = FILTER CntPrior BY verbCnt > 0 ;
ResultPrior = FOREACH FilteredPrior GENERATE uid; 

--ログイン日数のカウント
Grouped = GROUP EditDataPost BY (uid); 

ResultPost = FOREACH Grouped { 
    day = EditDataPost.days; 
    disDay = DISTINCT day;
    GENERATE FLATTEN(group) AS uid, COUNT(disDay) AS count_day; 
} 

--(7) 集計対象者用のデータのみに絞る(join)
Joined = join ResultPrior BY uid LEFT OUTER, ResultPost BY uid USING 'replicated';

--(8) データの取捨選択
Result = FOREACH Joined GENERATE 
	ResultPrior::uid AS uid,
	ResultPost::count_day AS count_day
;

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');