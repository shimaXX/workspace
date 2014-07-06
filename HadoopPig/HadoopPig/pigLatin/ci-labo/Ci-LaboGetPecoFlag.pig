--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-12-03' --つまり29日からのデータを取得する
%declare LAST_DATE  '2012-12-17' --つまり4日までのデータを取得する
%declare PROSTART_DATE  '2013-01-09' --つまり22日からのデータを取得する
%declare PROLAST_DATE  '2013-01-17' --つまり28日までのデータを取得する

--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCharacterCategory myUDF.GetCharacterCategory();
define GetClient myUDF.GetClient();
define GetPayment myUDF.GetPayment();
define GetMetaInfo myUDF.GetMetaInfo(); 
define GetNextDate myUDF.GetNextDate();
define GetRewards myUDF.GetRewards();
define CountBadges myUDF.CountBadges();
define TestTmp myUDF.TestTmp();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();


--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT 'works/output/Mining/Ci-LaboPecoFlag0124';
%default PATH_OUTPUT_VERB 'works/output/Mining/Ci-LaboPecoVerb0124';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray,f6,rb:chararray)
;

--rewardsのみ取ってくる。rewardsが空の場合はNULLとしている。
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, GetMetaInfo(verb, ap) AS verb, SUBSTRING(time,0,10) AS date, cid;


---------------------------------------
--◆導入前の訪問日数のカウント
----------------------------------------
FilData = FILTER Edit BY (cid == 7 OR cid==8) AND date > '$START_DATE' AND date < '$LAST_DATE';

--(5) セッションIDを振るためにuidでグループ化
Grouped = GROUP FilData BY uid; 

--(6) 日数のカウント
CntDate = FOREACH Grouped { 
	cd = DISTINCT FilData.date;    
    GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntDate;
} 

--(7) timeを年月日に直して列の並べ替え
EditDate = FOREACH CntDate GENERATE uid, CntDate;


----------------------------------------
--◆導入後の目的verbの数値
----------------------------------------
FilData = FILTER Edit BY (cid == 7 OR cid==8) AND date > '$PROSTART_DATE' AND date < '$PROLAST_DATE' AND verb == 'view:peko_my';

FilPro = FILTER Edit BY (cid == 7 OR cid==8) AND date > '$PROSTART_DATE' AND date < '$PROLAST_DATE';
Grp = GROUP FilPro By uid;
EdPro = FOREACH Grp GENERATE FLATTEN(group) AS uid;

--(5) セッションIDを振るためにuidでグループ化
Grouped = GROUP FilData BY uid; 
GetPecoNum = FOREACH Grouped GENERATE {
	cd = DISTINCT FilData.date;
	FLATTEN(group) AS uid, COUNT(FilData.verb) AS PecoCnt, COUNT(cd) AS cntD;
}

Joined = JOIN EdPro BY uid LEFT OUTER, GetPecoNum BY uid USING 'replicated'; 

Result = FOREACH Joined GENERATE
	EdPro::uid AS uid,
	GetPecoNum::PecoCnt AS PecoCnt,
	GetPecoNum::cntD AS cntD
;

Result = FOREACH Result GENERATE uid, PecoCnt, cntD, ((double)PecoCnt/(double)cntD) AS cntDailyPeco, (PecoCnt IS NULL ? 0 : 1) AS pecoFlag;

STORE Result INTO '$PATH_OUTPUT' USING PigStorage();


----------------------------------------
--◆導入前verbのカウント
----------------------------------------
--uid毎、verb毎にカウント
--イベント前のverb
FilData = FILTER Edit BY (cid == 7 OR cid==8) AND date > '$START_DATE' AND date < '$LAST_DATE';
				
Grp = GROUP FilData BY (uid,verb);
CntVerb = FOREACH Grp {
	cv = FilData.verb;
	GENERATE FLATTEN(group) AS (uid,verb), COUNT(cv) AS VerbCnt;
}

Grp = GROUP FilData BY uid;
CntDate = FOREACH Grp {
	cd = DISTINCT FilData.date;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntD;
}

Joined = JOIN CntVerb BY uid, CntDate BY uid USING 'replicated';

EdPre = FOREACH Joined GENERATE
	CntVerb::uid AS uid,
	CntVerb::verb AS verb,
	CntVerb::VerbCnt AS VerbCnt,
	CntDate::CntD AS CntD
;

ResultVerb = FOREACH EdPre GENERATE uid, verb, VerbCnt , CntD, ((double)VerbCnt/(double)CntD) AS VerbPerDate; 

Joined = JOIN Result BY uid LEFT OUTER, ResultVerb BY uid;

ResultVerb = FOREACH Joined GENERATE
	Result::uid AS uid,
	ResultVerb::verb AS verb,
	ResultVerb::VerbCnt AS VerbCnt,
	ResultVerb::CntD AS CntD,
	ResultVerb::VerbPerDate AS VerbPerDate
;

ResultVerb = FOREACH ResultVerb GENERATE uid, verb, VerbPerDate, (VerbPerDate IS NULL ? 'NULL' : '1') AS flag; 

ResultVerb = FILTER ResultVerb BY flag != 'NULL';
ResultVerb = FOREACH ResultVerb GENERATE uid, verb, VerbPerDate;

STORE ResultVerb INTO '$PATH_OUTPUT_VERB' USING PigStorage();