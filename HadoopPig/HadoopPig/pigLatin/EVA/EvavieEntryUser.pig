--10/23までにアクティビティがあり、かつ11/1までentryしていないユーザ
--を母集団とし、11/1以降entryしたユーザとしていないユーザでどこに差があるのかを見る
--決定木を使う

--変数への格納
%declare TIME_WINDOW  30m

--entryしたユーザとしていないユーザの母集団を形成する期間
%declare TEST_START_DATE  '2012-10-09' --つまり10/10日からのデータを取得する
%declare TEST_LAST_DATE  '2012-10-24' --つまり10/23日からのデータを取得する

--
%declare START_DATE  '2012-10-31' --つまり11/1日からのデータを取得する
%declare LAST_DATE  '2012-11-08' --つまり7日までのデータを取得する


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
%default PATH_OUTPUT 'works/output/EVA/EVAentryUserView';
%default PATH_OUTPUT_SESSION 'works/output/EVA/EVAentryUserViewSession';
%default PATH_OUTPUT_SESSION_TIME 'works/output/EVA/EVAentryUserViewSessionTime';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

EditData = FOREACH RowData GENERATE uid, cid, verb, SUBSTRING(time, 0, 10) AS days, ISOFormat(time) AS time;

--エヴァのみ、10/10～10/23のみのデータを取得
FilData = FILTER EditData BY cid == 3 AND days > '$TEST_START_DATE' AND days < '$TEST_LAST_DATE';

----------------------------------------
--上記の条件のユーザのみ取る
--ユニークユーザIDのみ取得
--joinの大元
Grp = GROUP FilData BY uid;

uniqueUserId = FOREACH Grp {
	GENERATE FLATTEN(group) AS uUid; 
}

-------------------------------------------
--上記の条件プラス会員登録してそうなユーザ
--あとでjoinしてnotで除外する
FilData = FILTER EditData BY cid == 3 AND days > '$TEST_START_DATE' AND days < '2012-11-01'
	AND (verb == 'login' OR verb == 'entry' OR verb == 'mypage') 
;

Grp = GROUP FilData BY uid;

entryFlag = FOREACH Grp {
	cnt = FilData.verb;
	GENERATE FLATTEN(group) AS uUid, COUNT(cnt) AS entryFlag;
}

---------------------------------------------
--10/10～10/23に行動があるユーザでかつ既にentryしているユーザを外す
--ますはjoin
joinedData = JOIN uniqueUserId BY uUid LEFT OUTER, entryFlag BY uUid USING 'replicated';

TMP = FOREACH joinedData GENERATE
	uniqueUserId::uUid AS uid,
	entryFlag::entryFlag AS flag
;

---------------------------------------------------
--flagだけではfilterがかからないため、countで1,0を振る
Grp = GROUP TMP BY uid;

TMP = FOREACH Grp {
	cnt = TMP.flag;
	GENERATE FLATTEN(group) AS uid, COUNT(cnt) AS Flag; 
}

--flag = 0、つまり10/23までにentryしていないユーザのみに絞る
Fil = FILTER TMP BY Flag == 0;

--そのuidのみ取得する
getUid = FOREACH Fil GENERATE uid;

-----------------------------------------------------
--10/24～11/7の間のverbをカウントする
FilData = FILTER EditData BY cid == 3 AND days >= '$TEST_LAST_DATE' AND days < '2012-11-08';

Grp = GROUP FilData BY (uid,days,verb);

ResultVerb = FOREACH Grp {
	cnt = FilData.verb;
	GENERATE FLATTEN(group) AS (uid, days, verb), COUNT(cnt) AS cntVerb;
}

-------------------------------------------------------
--join
joined = JOIN getUid BY uid LEFT OUTER, ResultVerb BY uid;

TMP = FOREACH joined GENERATE
	getUid::uid AS uid,
	ResultVerb::days AS days,
	ResultVerb::verb AS verb,
	ResultVerb::cntVerb AS cntVerb
;

Org = FILTER TMP BY days != '';

--uid、verb毎にcntデータをsumする
Grp = GROUP Org BY (uid, verb);

Result = FOREACH Grp {
	cnt = Org.cntVerb;
	GENERATE FLATTEN(group) AS (uid, verb), FLATTEN(SUM(cnt)) AS sumVerb;
}

-----------------------------------------------------
--10/24～10/31の間のsession数をカウントする
FilData = FILTER EditData BY cid == 3 AND days >= '$TEST_LAST_DATE' AND days < '2012-11-01';

Ed = FOREACH FilData GENERATE time, uid, verb; 

Grp = GROUP Ed BY (uid);

Sessionize = FOREACH Grp {
	ord = ORDER Ed BY time;
	GENERATE FLATTEN(Sessionize(ord));
}

--並び替え
Ed = FOREACH Sessionize GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--session回数をカウント
GroupUid = GROUP Ed BY uid;

--session回数をカウント
countSession = FOREACH GroupUid { 
    countS = DISTINCT Ed.session_id; 
    GENERATE FLATTEN(group) AS uid, (int)COUNT(countS) AS scnt; 
} 

joined = JOIN getUid BY uid , countSession BY uid;

TMP = FOREACH joined GENERATE
	getUid::uid AS uid,
	countSession::scnt AS scnt
;

STORE TMP INTO '$PATH_OUTPUT_SESSION' using PigStorage('\t');

-----------------------------------------------------
--10/24～10/31の間のsessionTimeの平均値を取得する
FilData = FILTER EditData BY cid == 3 AND days >= '$TEST_LAST_DATE' AND days < '2012-11-01';

Ed = FOREACH FilData GENERATE time, uid, verb; 

Grp = GROUP Ed BY (uid);

addSession = FOREACH Grp {
	ord = ORDER Ed BY time;
	GENERATE FLATTEN(Sessionize(ord));
}

Ed = FOREACH addSession GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP Ed BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpDaily = GROUP sessionTime BY uid;  

aveDailySessionTime = FOREACH grpDaily  GENERATE FLATTEN(group) AS uid, AVG(sessionTime.session_time) AS ave_session_time;

joined = JOIN getUid BY uid , aveDailySessionTime BY uid;

TMP = FOREACH joined GENERATE
	getUid::uid AS uid,
	aveDailySessionTime::ave_session_time AS ave_session_time
;

STORE TMP INTO '$PATH_OUTPUT_SESSION_TIME' USING PigStorage('\t'); 