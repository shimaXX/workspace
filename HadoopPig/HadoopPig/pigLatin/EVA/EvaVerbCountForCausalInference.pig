-----------------------------------------
--イベント効果を計測するための値を取得する
--イベント参加者を完全に一致させている
-----------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-24' --つまり25日からのデータを取得する
%declare LAST_DATE  '2012-11-01' --つまり31日までのデータを取得する
%declare POSTSTART_DATE  '2012-10-31'
%declare POSTLAST_DATE  '2012-11-08'

--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar
REGISTER GetIntervalDate.jar

--UDFの呼び出し名の定義
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');

define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategory myUDF.GetCategory();
define GetClient myUDF.GetClient();
define GetIntervalDate myUDF.GetIntervalDate('$START_DATE');
define GetSessionTime myUDF.GetSessionTime();


--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT 'works/output/Ming/EvaCausalInference0115';
%default PATH_OUTPUT_VERB 'works/output/Ming/EvaCountVerb0115';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--------------------------------
--対象者の絞り込みを行う
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS time, uid, cid, verb, GetClient(ap) AS client;
FilData = FILTER Edit BY cid == 3 AND time < '$LAST_DATE';	---日付

Ouid = FOREACH FilData GENERATE uid;
Grp = GROUP Ouid BY uid; 
Ouid = FOREACH Grp { 
	U = DISTINCT Ouid.uid;
	GENERATE FLATTEN(U) AS uid;
}

Fil = FILTER FilData BY verb=='entry' or verb=='login';

Grp = GROUP Fil BY uid;
CntEntry = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(Fil.verb) AS cntV;

--EntryFlagを付けるためにフルのuidとentryユーザを結合する
Joined = JOIN Ouid BY uid LEFT OUTER, CntEntry BY uid USING 'replicated';

--必要な変数のみに整理
Edj = FOREACH Joined GENERATE 
	Ouid::uid AS uid,
	CntEntry::cntV AS cntV
;

--entryFlagを付ける
Ed = FOREACH Edj GENERATE uid, (cntV IS NULL ? 0: 1) AS entFlag;

--entryしていないユーザに絞る
FF = FILTER Ed BY entFlag==0;

--entryしていないユーザのuidだけのテーブルを取得
POU = FOREACH FF GENERATE uid;

--初訪問後1週間以上経過したの人間に絞るためにuidを取得
Filed = FILTER Edit BY cid == 3 AND time < '2012-10-25';
Grp = GROUP FilData BY uid;
UU = FOREACH Grp { 
	U = DISTINCT FilData.uid;
	GENERATE FLATTEN(U) AS uid;
}

--初訪問後1週間以上経過したの人間のみに絞る
JoinedOU = JOIN UU BY uid, POU BY uid USING 'replicated';

OUR = FOREACH JoinedOU GENERATE UU::uid AS uid;


--------------------------------------
--イベント前1週間のデータ取得
FilPre = FILTER Edit BY cid == 3 AND time < '$LAST_DATE' AND time > '$START_DATE';	---日付

Grp = GROUP FilPre BY uid;
CntVerbPre = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPre.verb) AS cntV;

ResultPre = FOREACH CntVerbPre GENERATE uid, cntV, (uid IS NULL ? 0: 0) as Delta;


--------------------------------------
--イベント後1週間のデータ取得
FilPro = FILTER Edit BY cid == 3 AND time >= '$LAST_DATE' AND time < '$POSTLAST_DATE';	---日付

Grp = GROUP FilPro BY uid;
CntVerbPro = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPro.verb) AS cntV;

EntryUsr = FILTER FilPro BY verb=='entry';
JoinedPro = JOIN CntVerbPro BY uid LEFT OUTER, EntryUsr BY uid USING 'replicated';

EdPro = FOREACH JoinedPro GENERATE
	CntVerbPro::uid AS uid,
	CntVerbPro::cntV AS cntV,
	EntryUsr::verb AS entFlag
;

ResultPro = FOREACH EdPro GENERATE uid, cntV, (entFlag IS NULL ? 0 : 1) AS Z,  (uid IS NULL ? 1 : 1) AS Delta;


----------------------------------------
--join
JoinedRePre = JOIN OUR BY uid, ResultPre BY uid USING 'replicated';
JoinedRePro = JOIN OUR BY uid, ResultPro BY uid USING 'replicated';

Jpre = FOREACH JoinedRePre GENERATE
	OUR::uid AS uid,
	ResultPre::cntV AS cntVPre,
	ResultPre::Delta AS DeltaPre
;

Jpro = FOREACH JoinedRePro GENERATE
	OUR::uid AS uid,
	ResultPro::cntV AS cntVPro,
	ResultPro::Z AS Z,
	ResultPro::Delta AS DeltaPro
;

JoinedRe = JOIN Jpre BY uid, Jpro BY uid USING 'replicated';

Result = FOREACH JoinedRe GENERATE
	Jpre::uid AS uid,
	Jpre::cntVPre AS cntVPre,
	Jpro::cntVPro AS cntVPro,
	Jpro::Z AS Z,
	Jpre::DeltaPre AS DeltaPre,	--計算時は不要
	Jpro::DeltaPro AS DeltaPro	--計算時は不要
;


--------------------------------
--------------------------------
--verbの最小日からの期間を求める
Grp = GROUP Filed BY uid;
minActTime = FOREACH Grp GENERATE FLATTEN(group) AS uid, MIN(Filed.time) AS minTime; 
SpanFromMinTime = FOREACH minActTime GENERATE uid, GetIntervalDate(minTime) AS DateFromFirst;

--期間毎のverb数と観測期間内で最小日からの日数をjoin
Joined = JOIN Result BY uid, SpanFromMinTime BY uid USING 'replicated';

--整形
ResultJoinDays = FOREACH Joined GENERATE
	Result::uid AS uid,
	Result::cntVPre AS cntVPre,
	Result::cntVPro AS cntVPro,
	SpanFromMinTime::DateFromFirst AS DateFromFirst,
	Result::Z AS Z
;


------------------------------------------
--セッション系---------------------------------
--Sessionizeは先頭にtimeが必要
--Session回数のカウント
EdSession = FOREACH RowData GENERATE ISOFormat(time) AS time, SUBSTRING(time,0,10) AS date, uid, cid, verb, GetClient(ap) AS client;
Fil = FILTER EdSession BY cid == 3 AND date > '$START_DATE' AND date < '$LAST_DATE'; 

Ed = FOREACH Fil GENERATE time, verb, uid;

--(5) セッションIDを振るためにuidでグループ化
Grouped = GROUP Ed BY uid; 

--(6) セッションIDの生成
Sessionize01 = FOREACH Grouped { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) timeを年月日に直して列の並べ替え
Ed = FOREACH Sessionize01 GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) session回数をカウント
GroupUid = GROUP Ed BY uid;

--(9) session回数をカウント
ResultCountSession01 = FOREACH GroupUid { 
    countS = DISTINCT Ed.session_id; 
    GENERATE FLATTEN(group) AS uid, (int)COUNT(countS) AS scnt; 
} 


---------------------------------
--sessionTimeの平均値の取得
Ed = FOREACH Sessionize01 GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP Ed BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpUU = GROUP sessionTime BY uid;  

ResultSessionTime01 = FOREACH grpUU  GENERATE FLATTEN(group) AS uid, AVG(sessionTime.session_time) AS ave_session_time;

----------------------
--大元のデータセットとsessionCntとsessionTimeをjoinする
Joined = Join ResultJoinDays BY uid, ResultCountSession01 BY uid;

EdJoinDaysAndCntSess = FOREACH Joined GENERATE
	ResultJoinDays::uid AS uid,
	ResultJoinDays::cntVPre AS cntVPre,
	ResultJoinDays::cntVPro AS cntVPro,
	ResultJoinDays::DateFromFirst AS DateFromFirst,
	ResultCountSession01::scnt AS scnt,
	ResultJoinDays::Z AS Z
;


Joined = Join EdJoinDaysAndCntSess BY uid, ResultSessionTime01 BY uid;

EdJoinDaysAndCntSess = FOREACH Joined GENERATE
	EdJoinDaysAndCntSess::uid AS uid,
	EdJoinDaysAndCntSess::cntVPre AS cntVPre,
	EdJoinDaysAndCntSess::cntVPro AS cntVPro,
	EdJoinDaysAndCntSess::DateFromFirst AS DateFromFirst,
	EdJoinDaysAndCntSess::scnt AS scnt,
	ResultSessionTime01::ave_session_time AS ave_session_time,
	EdJoinDaysAndCntSess::Z AS Z
;

STORE EdJoinDaysAndCntSess INTO '$PATH_OUTPUT' using PigStorage('\t');


--------------------------------------
--------------------------------------
--verbをカウントする
--(3) EVAに絞る
FilteredData = FILTER Edit BY cid == 3 AND
				time > '$START_DATE' AND time < '$LAST_DATE';	---日付

--(4) 不要な列（cid）を削除
EditData = FOREACH FilteredData GENERATE uid, verb;

--(5) uid毎,verb毎の集計
Grouped = GROUP EditData BY (uid, verb); 

ResultVerb = FOREACH Grouped { 
    verb_count = EditData.verb; 
    GENERATE FLATTEN(group) AS (uid,verb), COUNT(verb_count) AS verbCnt; 
} 

--------------------------------------------
--期間内の訪問日数をカウントする
EditData = FOREACH FilteredData GENERATE uid, time;
Grp = GROUP EditData BY uid;
CntDays = FOREACH Grp{
	Dates = DISTINCT EditData.time;
	GENERATE FLATTEN(group) AS uid, COUNT(Dates) AS CntVisitDays;
}


--------------------------------
--verbの回数を訪問日数で割る
--まずはverbの回数と訪問日をjoint--
Joined = JOIN ResultVerb BY uid, CntDays BY uid USING 'replicated';

EdVerbDate = FOREACH Joined GENERATE
	ResultVerb::uid AS uid,
	ResultVerb::verb AS verb,
	ResultVerb::verbCnt AS verbCnt,
	CntDays::CntVisitDays AS VisitDays
;

VerbPerDay = FOREACH EdVerbDate GENERATE uid, verb, ((double)verbCnt/(double)VisitDays) AS VperD;

JoinedEdVerbData = JOIN EdJoinDaysAndCntSess BY uid LEFT OUTER, VerbPerDay BY uid USING 'replicated';

ResultVerbCount = FOREACH JoinedEdVerbData GENERATE
	EdJoinDaysAndCntSess::uid AS uid,
	VerbPerDay::verb AS verb,
	VerbPerDay::VperD AS VperD
;

STORE ResultVerbCount INTO '$PATH_OUTPUT_VERB' USING PigStorage();