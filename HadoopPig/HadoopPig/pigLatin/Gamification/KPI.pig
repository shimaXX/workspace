--変数への格納
%declare TIME_WINDOW  30m

--%declare START_DATE  '2012-11-07' --つまり11/8日からのデータを取得する
--%declare LAST_DATE  '2012-11-15' --つまり14日までのデータを取得する
--%declare EXSTART_DATE  '2012-10-31' --つまり11/1日からのデータを取得する
--%declare EXLAST_DATE  '2012-11-08' --つまり07日までのデータを取得する

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
--%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/GAMIFICATION/UUetc1107';
%default PATH_OUTPUT_ACTION 'works/output/GAMIFICATION/Action1107';
%default PATH_OUTPUT_UNI_ACT 'works/output/GAMIFICATION/UniAct1107';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

EditData = FOREACH RowData GENERATE
	uid, cid, verb, SUBSTRING(time, 0, 10) AS days, GetClient(ap) AS client,
	GetCategory(ap) AS category,
	GetNewflag(ap) AS newFlag,
	GetReservationflag(ap) AS reservationFlag
;

-------------------------------------
--DAUのカウント
FilteredData = FILTER EditData BY (cid == 3) AND (days > '$START_DATE') AND (days >= '2012-11-01');
Grouped = GROUP FilteredData BY (days);

--UUのカウント
ResultUU = FOREACH Grouped { 
    UU = DISTINCT FilteredData.uid;
    GENERATE FLATTEN(group) AS days, COUNT(UU) AS DAU; 
} 

---------------------------------
--新規UUの取得_OK
FilNUU = FILTER EditData BY (cid == 3) AND (days > '$START_DATE') AND (verb == 'entry');
GrpNUU = GROUP FilNUU BY (days);

ResultNUU = FOREACH GrpNUU { 
    NUU = DISTINCT FilNUU.uid;
    GENERATE FLATTEN(group) AS days, COUNT(NUU) AS DNU; 
} 

---------------------------------
--アクティビティ数の取得_try
GrpVerb = GROUP FilteredData BY (days);

ResultVerb = FOREACH GrpVerb { 
    cntVerb = FilteredData.verb;
    GENERATE FLATTEN(group) AS days, COUNT(cntVerb) AS cntDailyVerb; 
} 

---------------------------------
--平均アクティビティ数の取得
JoinVerbAndUU = JOIN ResultVerb BY days, ResultUU BY days USING 'replicated';

EditAveVerb = FOREACH JoinVerbAndUU GENERATE ResultVerb::days AS days, ResultUU::DAU AS DAU, ResultVerb::cntDailyVerb AS cntDailyVerb;  

ResultAveVerb = FOREACH EditAveVerb GENERATE days, ((double)cntDailyVerb/(double)DAU) AS DAA;
 
---------------------------------
--PUの取得
FilPUU = FILTER EditData BY (cid == 3) AND (days > '$START_DATE') AND (verb == 'buy');
GrpPUU = GROUP FilPUU BY (days);

ResultPUU = FOREACH GrpPUU { 
    cntPUU = DISTINCT FilPUU.uid;
    GENERATE FLATTEN(group) AS days, COUNT(cntPUU) AS PUU; 
} 

---------------------------------
--CVRの取得
JoinPUUAndUU = JOIN ResultUU BY days, ResultPUU BY days USING 'replicated';
EditAveCVR = FOREACH JoinPUUAndUU GENERATE ResultUU::days AS days, ResultPUU::PUU AS PUU, ResultUU::DAU AS DAU;  
ResultAveCVR = FOREACH EditAveCVR GENERATE days, ((double)PUU/(double)DAU) AS CVR;

---------------------------------
--再訪率（前日比）の取得
FilEntry =  FILTER EditData BY (cid == 3) AND (days > '$START_DATE') AND (verb == 'entry');
FilEntry =  FOREACH FilEntry GENERATE uid, days;

ModDay = FOREACH FilEntry GENERATE
	uid,
	GetNextDate(days) AS cmpDays
;

JoinedEntry = JOIN FilEntry BY uid ,ModDay BY uid;

EditEntry = FOREACH JoinedEntry GENERATE
	FilEntry::uid AS uid,
	FilEntry::days AS days,
	ModDay::cmpDays AS cmpDays
;

JoinCmpDays = JOIN FilteredData BY uid LEFT OUTER , EditEntry BY uid USING 'replicated';

EditLastNewUU = FOREACH JoinCmpDays GENERATE
	FilteredData::uid AS uid,
	FilteredData::days AS origDays,
	EditEntry::cmpDays AS cmpDays
; 

FilLNU = FILTER EditLastNewUU BY origDays == cmpDays;

Grp = GROUP FilLNU BY (origDays);

ResultLNUU = FOREACH Grp { 
    cntUU = DISTINCT FilLNU.uid;
    GENERATE FLATTEN(group) AS days, COUNT(cntUU) AS cntLNUU; 
} 

---------------------------------
--再訪率（前週比）の取得
FilWEntry =  FILTER EditData BY (cid == 3) AND (days > '$EXSTART_DATE') AND (days < '$EXLAST_DATE') AND (verb == 'entry');
FilWEntry =  FOREACH FilWEntry GENERATE uid, days;

VisitWEntry = FILTER EditData BY (cid == 3) AND (days > '$START_DATE') AND (days < '$LAST_DATE');
VisitWEntry = FOREACH VisitWEntry GENERATE uid, days;

JoinedWEntry = JOIN FilWEntry BY uid  ,VisitWEntry BY uid USING 'replicated';

EditWEntry = FOREACH JoinedWEntry GENERATE
	FilWEntry::uid AS uid,
	VisitWEntry::days AS days,
	VisitWEntry::days AS Wdays
;

EditWEntry = FILTER EditWEntry BY Wdays != '';

Grp = GROUP EditWEntry BY days;

ResultWEntry = FOREACH Grp{
	cntUU = DISTINCT EditWEntry.uid;
	GENERATE FLATTEN(group) AS days ,COUNT(cntUU) AS cntLWNUU;
}

----------------------------------
--session数のカウント
Edit = FOREACH RowData GENERATE
	ISOFormat(time) AS time, uid, cid, SUBSTRING(time, 0, 10) AS days;

FilData = FILTER Edit BY cid == 3 AND days > '$START_DATE';

Grp = GROUP FilData BY uid;

Session = FOREACH Grp {
	ord = ORDER FilData BY time ASC;
    GENERATE FLATTEN(group), FLATTEN(Sessionize(ord));
}

--daysでグループ化し、session数をカウント
Grp = GROUP Session BY days;

cntSession = FOREACH Grp {
	session = DISTINCT Session.session_id;
    GENERATE FLATTEN(group) AS days, FLATTEN(COUNT(session)) AS cntSession;
}

-------------------------------
--日付ごとに1つのデータしかないモノをjoin

--UUとNUU
JoinResult01 = JOIN ResultUU BY days, ResultNUU BY days;
Result01 = FOREACH JoinResult01 GENERATE
	ResultUU::days AS days,
	ResultUU::DAU AS DAU,
	ResultNUU::DNU AS DNU
;

--Verbと上の結果
JoinResult02 = JOIN Result01 BY days LEFT OUTER, ResultVerb BY days USING 'replicated';

Result02 = FOREACH JoinResult02 GENERATE
	Result01::days AS days,
	Result01::DAU AS DAU,
	Result01::DNU AS DNU,
	ResultVerb::cntDailyVerb AS cntDailyVerb
;

--AverageVerbと上の結果
JoinResult03 = JOIN Result02 BY days LEFT OUTER, ResultAveVerb BY days USING 'replicated';

Result03 = FOREACH JoinResult03 GENERATE
	Result02::days AS days,
	Result02::DAU AS DAU,
	Result02::DNU AS DNU,
	Result02::cntDailyVerb AS cntDailyVerb,
	ResultAveVerb::DAA AS DAA
;

--PUUと上の結果
JoinResult04 = JOIN Result03 BY days LEFT OUTER, ResultPUU BY days USING 'replicated';

Result04 = FOREACH JoinResult04 GENERATE
	Result03::days AS days,
	Result03::DAU AS DAU,
	Result03::DNU AS DNU,
	Result03::cntDailyVerb AS cntDailyVerb,
	Result03::DAA AS DAA,
	ResultPUU::PUU AS PUU
;

--AveCVRと上の結果
JoinResult05 = JOIN Result04 BY days LEFT OUTER, ResultAveCVR BY days USING 'replicated';

Result05 = FOREACH JoinResult05 GENERATE
	Result04::days AS days,
	Result04::DAU AS DAU,
	Result04::DNU AS DNU,
	Result04::cntDailyVerb AS cntDailyVerb,
	Result04::DAA AS DAA,
	Result04::PUU AS PUU,
	ResultAveCVR::CVR AS CVR
;

--NUUと上の結果
JoinResult06 = JOIN Result05 BY days LEFT OUTER, ResultLNUU BY days USING 'replicated';

Result06 = FOREACH JoinResult06 GENERATE
	Result05::days AS days,
	Result05::DAU AS DAU,
	Result05::DNU AS DNU,
	Result05::cntDailyVerb AS cntDailyVerb,
	Result05::DAA AS DAA,
	Result05::PUU AS PUU,
	Result05::CVR AS CVR,
	ResultLNUU::cntLNUU AS cntLNUU
;

--WEntryと上の結果
JoinResult07 = JOIN Result06 BY days LEFT OUTER, ResultWEntry BY days USING 'replicated';

Result07 = FOREACH JoinResult07 GENERATE
	Result06::days AS days,
	Result06::DAU AS DAU,
	Result06::DNU AS DNU,
	Result06::cntDailyVerb AS cntDailyVerb,
	Result06::DAA AS DAA,
	Result06::PUU AS PUU,
	Result06::CVR AS CVR,
	Result06::cntLNUU AS cntLNUU,
	ResultWEntry::cntLWNUU AS cntLWNUU 
;

--cntSessionと上の結果
JoinResult08 = JOIN Result07 BY days LEFT OUTER, cntSession BY days USING 'replicated';

Result08 = FOREACH JoinResult08 GENERATE
	Result07::days AS days,
	Result07::DAU AS DAU,
	Result07::DNU AS DNU,
	Result07::cntDailyVerb AS cntDailyVerb,
	Result07::DAA AS DAA,
	Result07::PUU AS PUU,
	Result07::CVR AS CVR,
	Result07::cntLNUU AS cntLNUU,
	Result07::cntLWNUU AS cntLWNUU,
	cntSession::cntSession AS cntSession
;

STORE Result08 INTO '$PATH_OUTPUT' USING PigStorage('\t');

---------------------------------
--各種行動数の取得
--まずはカテゴリ
GrpCat = GROUP FilteredData BY (days, verb, category);

ResultCat = FOREACH GrpCat { 
    cntCat = FilteredData.verb;
    GENERATE FLATTEN(group), COUNT(cntCat) AS cntCat; 
} 

--新商品
GrpNew = GROUP FilteredData BY (days, verb, newFlag);

ResultNew = FOREACH GrpNew { 
    cntNew = FilteredData.verb;
    GENERATE FLATTEN(group), COUNT(cntNew) AS cntNew; 
} 

--入荷予約
GrpReservation = GROUP FilteredData BY (days, verb, reservationFlag);

ResultReservation = FOREACH GrpReservation { 
    cntReservation = FilteredData.verb;
    GENERATE FLATTEN(group), COUNT(cntReservation) AS cntReservation; 
} 

--metaデータなし
GrpAct = GROUP FilteredData BY (days, verb);

ResultAct = FOREACH GrpAct { 
    cntAct = FilteredData.verb;
    GENERATE FLATTEN(group), COUNT(cntAct) AS cntAct; 
} 

--それぞれをunionする
UniCatNew = UNION ResultCat ,ResultNew;
UniRes = UNION UniCatNew ,ResultReservation;

FilUni = FILTER UniRes BY $2 !='';

STORE ResultAct INTO '$PATH_OUTPUT_ACTION' USING PigStorage('\t');
STORE FilUni INTO '$PATH_OUTPUT_UNI_ACT' USING PigStorage('\t');