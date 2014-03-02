-----------------------------------------
--因果推論分析をするために必要なデータセットの構築
--a時点＝なにもイベント等やっていない
--b時点＝sprocket導入とキャンペーンを同時に行ている時期
--b時点について、Entryしたユーザをsprocket参加ユーザとみなす、
--Entryしていないユーザをsprocket不参加ユーザとみなす
------対象ユーザ-----------
--a時点集計期間前にEntryフラグが無いユーザのみを対象とする
--集計する従属変数はsession回数、session時間、期間無い総アクション回数
-----------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-28' --つまり29日からのデータを取得する
%declare LAST_DATE  '2012-11-05' --つまり4日までのデータを取得する
%declare AXSTART_DATE  '2012-10-21' --つまり22日からのデータを取得する
%declare AXLAST_DATE  '2012-10-29' --つまり28日までのデータを取得する

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

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT 'works/output/Ming/TestData';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--対象者の絞り込みを行う
Edit = FOREACH RowData GENERATE SUBSTRING(time,0,10) AS time, uid, cid, verb, GetClient(ap) AS client;
FilData = FILTER Edit BY cid == 3 AND time < '2012-11-01';

Ouid = FOREACH FilData GENERATE uid;
Grp = GROUP Ouid BY uid; 
Ouid = FOREACH Grp { 
	U = DISTINCT Ouid.uid;
	GENERATE FLATTEN(U) AS uid;
}

Fil = FILTER FilData BY verb=='entry' or verb=='mypage';

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
FilPre = FILTER Edit BY cid == 3 AND time < '2012-11-01' AND time > '2012-10-24';

Grp = GROUP FilPre BY uid;
CntVerbPre = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPre.verb) AS cntV;

ResultPre = FOREACH CntVerbPre GENERATE uid, cntV, (uid IS NULL ? 0: 0) as Delta;


--------------------------------------
--イベント後1週間のデータ取得
FilPro = FILTER Edit BY cid == 3 AND time >= '2012-11-01' AND time < '2012-11-08';

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
	Jpre::DeltaPre AS DeltaPre,
	Jpro::DeltaPro AS DeltaPro
;

STORE Result INTO '$PATH_OUTPUT' USING PigStorage('\t'); 