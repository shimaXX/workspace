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
define GetCharacterCategory myUDF.GetCharacterCategory();
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT 'works/input/ci-labo/';
%default PATH_OUTPUT 'works/output/Ci-Labo/Ci-LaboCountSessionNum1203';

--(1)-2データの対応付け
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, verb, cid;

--(3) ci-laboに絞る。
FilteredDataPrior = FILTER Edit BY cid == 4 AND SUBSTRING(time, 0, 10) > '$EXSTART_DATE' AND SUBSTRING(time, 0, 10) < '$EXLAST_DATE';
FilteredDataPost = FILTER Edit BY cid == 4 AND SUBSTRING(time, 0, 10) > '$START_DATE' AND SUBSTRING(time, 0, 10) < '$LAST_DATE';

-------------------------------------------------
-- 集計対象者を絞るためのuid毎,verb毎の集計
Grouped = GROUP FilteredDataPrior BY uid; 

CntPrior = FOREACH Grouped { 
    verb_count = FilteredDataPrior.verb; 
    GENERATE FLATTEN(group) AS uid, COUNT(verb_count) AS verbCnt; 
} 

FilteredPrior = FILTER CntPrior BY verbCnt > 0 ;
ResultPrior = FOREACH FilteredPrior GENERATE uid; 


------------------------------------------------------------
--(4) 不要な列（client, cid）を削除
EditData = FOREACH FilteredDataPost GENERATE time, uid, verb;

--(5) セッションIDを振るためにuidでグループ化
Grouped = GROUP EditData BY uid; 

--(6) セッションIDの生成→{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize = FOREACH Grouped { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) timeを年月日に直して列の並べ替え
EditData = FOREACH Sessionize GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) uidでグループ化
GroupUid = GROUP EditData BY uid;

--(9) session回数をカウント
ResultPost = FOREACH GroupUid { 
    countS = DISTINCT EditData.session_id; 
    GENERATE FLATTEN(group) AS uid, (int)COUNT(countS) AS scnt; 
} 

-----------------------------------------------------------
--join
-- 集計対象者用のデータのみに絞る(join)
Joined = join ResultPrior BY uid LEFT OUTER, ResultPost BY uid USING 'replicated';

-- データの取捨選択
Result = FOREACH Joined GENERATE 
	ResultPrior::uid AS uid,
	ResultPost::scnt AS scnt
;

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');