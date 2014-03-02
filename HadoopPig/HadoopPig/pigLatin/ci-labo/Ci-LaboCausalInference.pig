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
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/test/';
%default PATH_OUTPUT_PreTotal 'works/output/Mining/Ci-LaboTotalVerbPre_Kutikomi';
%default PATH_OUTPUT_ProTotal 'works/output/Mining/Ci-LaboTotalVerbPro_Kutikomi';
%default PATH_OUTPUT_PreVerb 'works/output/Mining/Ci-LaboVerbPre_Kutikomi';
%default PATH_OUTPUT_ProVerb 'works/output/Mining/Ci-LaboVerbPro_Kutikomi';


RawData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--変数の絞り込み
Edit = FOREACH RawData GENERATE ISOFormat(time) AS IsoTime ,SUBSTRING(time,0,10) AS time, uid, cid, GetMetaInfo(verb,ap) AS verb;

--------------------------------------
--イベント前のデータ取得
--------------------------------------
--総verb数の
FilPre = FILTER Edit BY (cid == 8 OR cid == 7) 
			AND time < '2012-12-16' AND time > '2012-12-03';-- AND verb == 'view:kuchikomi';	--view:favorite,cart:favorite

Grp = GROUP FilPre BY uid;
CntVerbPre = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPre.verb) AS cntV;

CntDatePre = FOREACH Grp {
	cd = DISTINCT FilPre.time;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntDate;
}
JoinPre = JOIN CntVerbPre BY uid, CntDatePre BY uid USING 'replicated';

EdPre = FOREACH JoinPre GENERATE
	CntVerbPre::uid AS uid,
	CntVerbPre::cntV AS cntV,
	CntDatePre::CntDate AS CntDate
;

EdPre = FOREACH EdPre GENERATE uid, ((double)cntV/(double)CntDate) AS cntV;

ResultPre = FOREACH EdPre GENERATE uid, cntV, (uid IS NULL ? 0: 0) as Z;

--------------------
--session系
--sessionCnt
--セッションカウント
addSession = FOREACH Grp { 
    ord = ORDER FilPre BY IsoTime ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, SUBSTRING(IsoTime, 0, 10) AS date, IsoTime, session_id;

Grp = GROUP EditData BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER EditData  BY IsoTime ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.IsoTime)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpUid = GROUP sessionTime BY uid;  

ResultSessPre = FOREACH grpUid  GENERATE FLATTEN(group) AS uid, COUNT(sessionTime.session_id) AS cntSession, 
					AVG(sessionTime.session_time) AS ave_session_time;

JoinedResultPre = JOIN ResultSessPre BY uid, ResultPre BY uid USING 'replicated';

JoinedResultPre = FOREACH JoinedResultPre GENERATE
	ResultSessPre::uid AS uid,
	ResultSessPre::cntSession AS cntSession,
	ResultSessPre::ave_session_time AS ave_session_time,
	ResultPre::cntV AS cntV,
	ResultPre::Z AS Z
;

STORE JoinedResultPre INTO '$PATH_OUTPUT_PreTotal' USING PigStorage('\t');


--------------------------------------
--イベント後のデータ取得
FilPro = FILTER Edit BY cid == 8
				AND time > '2012-12-15' AND time < '2013-01-17';-- AND verb == 'view:kuchikomi';	--view:favorite,cart:favorite;

Grp = GROUP FilPro BY uid;
CntVerbPro = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilPro.verb) AS cntV;

CntDatePro = FOREACH Grp {
	cd = DISTINCT FilPro.time;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntDate;
}

JoinPro = JOIN CntVerbPro BY uid, CntDatePro BY uid USING 'replicated';

EdPro = FOREACH JoinPro GENERATE
	CntVerbPro::uid AS uid,
	CntVerbPro::cntV AS cntV,
	CntDatePro::CntDate AS CntDate
;

EdPro = FOREACH EdPro GENERATE uid, ((double)cntV/(double)CntDate) AS cntV;

ResultPro = FOREACH EdPro GENERATE uid, cntV, (uid IS NULL ? 1 : 1) AS Z;

--------------------
--session系
--sessionCnt
--セッションカウント
addSession = FOREACH Grp { 
    ord = ORDER FilPro BY IsoTime ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

EditData = FOREACH addSession GENERATE uid, SUBSTRING(IsoTime, 0, 10) AS date, IsoTime, session_id;

Grp = GROUP EditData BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER EditData  BY IsoTime ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.IsoTime)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpUid = GROUP sessionTime BY uid;  

ResultSessPro = FOREACH grpUid  GENERATE FLATTEN(group) AS uid, COUNT(sessionTime.session_id) AS cntSession, 
					AVG(sessionTime.session_time) AS ave_session_time;

JoinedResultPro = JOIN ResultSessPro BY uid, ResultPro BY uid USING 'replicated';

JoinedResultPro = FOREACH JoinedResultPro GENERATE
	ResultSessPro::uid AS uid,
	ResultSessPro::cntSession AS cntSession,
	ResultSessPro::ave_session_time AS ave_session_time,
	ResultPro::cntV AS cntV,
	ResultPro::Z AS Z
;

STORE JoinedResultPro INTO '$PATH_OUTPUT_ProTotal' USING PigStorage('\t');

----------------------------------------
--uid毎、verb毎にカウント
--イベント前のverb
FilPre = FILTER Edit BY (cid == 8 OR cid == 7)  
				AND time < '2012-12-16' AND time > '2012-12-03';
				
Grp = GROUP FilPre BY (uid,verb);
CntVerbByUPre = FOREACH Grp {
	cv = FilPre.verb;
	GENERATE FLATTEN(group) AS (uid,verb), COUNT(cv) AS VerbCnt;
}

Grp = GROUP FilPre BY uid;
CntDatePre = FOREACH Grp {
	cd = DISTINCT FilPre.time;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntDate;
}

JoinPre = JOIN CntVerbByUPre BY uid, CntDatePre BY uid USING 'replicated';

EdPre = FOREACH JoinPre GENERATE
	CntVerbByUPre::uid AS uid,
	CntVerbByUPre::verb AS verb,
	CntVerbByUPre::VerbCnt AS VerbCnt,
	CntDatePre::CntDate AS CntDate
;

ResultPre = FOREACH EdPre GENERATE uid, verb, ((double)VerbCnt/(double)CntDate) AS verbCnt;

STORE ResultPre INTO '$PATH_OUTPUT_PreVerb' USING PigStorage('\t');

--イベント後のverb
FilPro = FILTER Edit BY cid == 8
				AND time < '2013-01-17' AND time > '2012-12-15';
				
Grp = GROUP FilPro BY (uid,verb);
CntVerbByUPro = FOREACH Grp {
	cv = FilPro.verb;
	GENERATE FLATTEN(group) AS (uid,verb), COUNT(cv) AS VerbCnt;
}

Grp = GROUP FilPro BY uid;
CntDatePro = FOREACH Grp {
	cd = DISTINCT FilPro.time;
	GENERATE FLATTEN(group) AS uid, COUNT(cd) AS CntDate;
}

JoinPro = JOIN CntVerbByUPro BY uid, CntDatePro BY uid USING 'replicated';

EdPro = FOREACH JoinPro GENERATE
	CntVerbByUPro::uid AS uid,
	CntVerbByUPro::verb AS verb,
	CntVerbByUPro::VerbCnt AS VerbCnt,
	CntDatePro::CntDate AS CntDate
;

ResultPro = FOREACH EdPro GENERATE uid, verb, ((double)VerbCnt/(double)CntDate) AS verbCnt;

STORE ResultPro INTO '$PATH_OUTPUT_ProVerb' USING PigStorage('\t');