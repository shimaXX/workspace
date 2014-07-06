-----------------------------------------
--エンゲージメント算出に利用するための値を取得
-----------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-12-18'
%declare LAST_DATE  '2013-01-14'
%declare AXSTART_DATE  '2012-10-21'
%declare AXLAST_DATE  '2012-10-29'

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
define GetIntervalDate myUDF.GetIntervalDate('$LAST_DATE');
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/Minig/Ci-LaboEngage_1218-0114';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--対象者の絞り込みを行う
Edit = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid,
	GetPayment(ap) AS payment,  GetMetaInfo(verb, ap) AS meta;
FilData01 = FILTER Edit BY (cid == 8 OR cid == 7) AND SUBSTRING(time,0,10)>= '$START_DATE' AND SUBSTRING(time,0,10)<= '$LAST_DATE';

--------------------------------------------
--------------------------------------------
--【まずは閾値より前のデータを取得】
--セッション数の取得---------------------------------
--(4) 不要な列（client, cid）を削除
Ed = FOREACH FilData01 GENERATE time, uid, meta;

--(5) セッションIDを振るためにuidでグループ化
Grouped = GROUP Ed BY uid; 

--(6) セッションIDの生成→{time, uid, meta, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize01 = FOREACH Grouped { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) timeを年月日に直して列の並べ替え
Ed = FOREACH Sessionize01 GENERATE uid, meta, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) session回数をカウント
GroupUid = GROUP Ed BY uid;

--(9) session回数をカウント
ResultCountSession01 = FOREACH GroupUid { 
    countS = DISTINCT Ed.session_id; 
    GENERATE FLATTEN(group) AS uid, (int)COUNT(countS) AS scnt; 
} 


--セッション時間---------------------------------
--Sessionizeは先頭にtimeが必要
--Edに使用されているSessionizeは上のセッション回数をカウントするときに取ったもの
Ed = FOREACH Sessionize01 GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP Ed BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpUU = GROUP sessionTime BY uid;  

ResultSessionTime01 = FOREACH grpUU  GENERATE FLATTEN(group) AS uid, AVG(sessionTime.session_time) AS ave_session_time;


--購入総額---------------------------------
Ed = FOREACH FilData01 GENERATE uid, payment;

Grp = GROUP Ed BY uid;

ResultPayment01 =  FOREACH Grp GENERATE FLATTEN(group) AS uid, SUM(Ed.payment) AS payment;


--購入回数---------------------------------
--使ってない--
--Ed = FOREACH FilData01 GENERATE uid, verb;
--Fil = FILTER Ed BY verb == 'buy';
--Grp = GROUP Ed BY uid;
--ResultPayment01 =  FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(Ed.verb) AS cntBuy;


--期間内最終行動日を取得する------------------------------------
--(2) 必要なデータに絞る
Ed = FOREACH FilData01 GENERATE uid, cid, SUBSTRING(time, 0, 10) AS time;

--(3) galsterに絞る。spに絞る。
FilteredData = FILTER Ed BY cid == 8;

--(4) 不要な列（client, cid）を削除
Ed = FOREACH FilteredData GENERATE uid, time;

--(5) uidでグループ化
Grouped = GROUP Ed BY (uid); 

getMaxStamp = FOREACH Grouped { 
    row_time = Ed.time; 
    GENERATE FLATTEN(group) AS uid, MAX(row_time) AS lastDate; 
}

ResultRecency01 = FOREACH getMaxStamp GENERATE uid, GetIntervalDate(lastDate) AS recency;


---------------------------------------------------
--ここからはjoin
--セッション回数とセッション時間
joined0101 = JOIN ResultCountSession01 BY uid LEFT OUTER, ResultSessionTime01 BY uid USING 'replicated';

TMP0101 = FOREACH joined0101 GENERATE 
	ResultCountSession01::uid AS uid,
	ResultCountSession01::scnt AS scnt,
	ResultSessionTime01::ave_session_time AS ave_session_time 
;

joined0102 = JOIN TMP0101 BY uid LEFT OUTER, ResultPayment01 BY uid USING 'replicated';

TMP0102 = FOREACH joined0102 GENERATE 
	TMP0101::uid AS uid,
	TMP0101::scnt AS scnt,
	TMP0101::ave_session_time AS ave_session_time,
	ResultPayment01::payment AS payment
	--ResultPayment01::cntBuy AS cntBuy
;

joined0103 = JOIN TMP0102 BY uid LEFT OUTER, ResultRecency01 BY uid USING 'replicated';

Result01 = FOREACH joined0103 GENERATE 
	TMP0102::uid AS uid,
	TMP0102::scnt AS scnt,
	TMP0102::ave_session_time AS ave_session_time,
	TMP0102::payment AS payment,
	ResultRecency01::recency AS recency 
;


----------------------------------------------
--■コミュニティ関係指標
--コミュニティへの投稿数のカウント
----------------------------------------------
EdCom = FOREACH FilData01 GENERATE uid, meta;
--口コミ投稿数
FilBz = FILTER EdCom BY meta == 'pmp_commu:buzz';

--お悩み回答回数
FilCm = FILTER EdCom BY meta == 'pmp_commu:comment';

--お悩み投稿回数
FilNym = FILTER EdCom BY meta == 'pmp_commu:onayami';

--ベストアンサー受賞回数
FilBA = FILTER EdCom BY meta == 'pmp_commu:best_answer';

-------------
--カウント
Grp = GROUP FilBz BY (uid,meta);
CntBz = FOREACH Grp GENERATE FLATTEN(group) AS (uid, meta), COUNT(FilBz.meta) AS cntBz;
Grp = GROUP FilCm BY (uid,meta);
CntCm = FOREACH Grp GENERATE FLATTEN(group) AS (uid, meta), COUNT(FilCm.meta) AS cntCm;
Grp = GROUP FilNym BY (uid,meta);
CntNym = FOREACH Grp GENERATE FLATTEN(group) AS (uid, meta), COUNT(FilNym.meta) AS cntNym;
Grp = GROUP FilBA BY (uid,meta);
CntBA = FOREACH Grp GENERATE FLATTEN(group) AS (uid, meta), COUNT(FilBA.meta) AS cntBA;

-------------
--RFM系指標とのjoin
JoinBz = JOIN Result01 BY uid LEFT OUTER, CntBz BY uid USING 'replicated';

ResultBz = FOREACH JoinBz GENERATE 
	Result01::uid AS uid,
	Result01::scnt AS scnt,
	Result01::ave_session_time AS ave_session_time,
	Result01::payment AS payment,
	Result01::recency AS recency,
	CntBz::cntBz AS cntBz
;

JoinCm = JOIN ResultBz BY uid LEFT OUTER, CntCm BY uid USING 'replicated';

ResultCm = FOREACH JoinCm GENERATE 
	ResultBz::uid AS uid,
	ResultBz::scnt AS scnt,
	ResultBz::ave_session_time AS ave_session_time,
	ResultBz::payment AS payment,
	ResultBz::recency AS recency,
	ResultBz::cntBz AS cntBz,
	CntCm::cntCm AS cntCm
;

JoinNym = JOIN ResultCm BY uid LEFT OUTER, CntNym BY uid USING 'replicated';

ResultNym = FOREACH JoinNym GENERATE 
	ResultCm::uid AS uid,
	ResultCm::scnt AS scnt,
	ResultCm::ave_session_time AS ave_session_time,
	ResultCm::payment AS payment,
	ResultCm::recency AS recency,
	ResultCm::cntBz AS cntBz,
	ResultCm::cntCm AS cntCm,
	CntNym::cntNym AS cntNym
;

JoinBA = JOIN ResultNym BY uid LEFT OUTER, CntBA BY uid USING 'replicated';

ResultBA = FOREACH JoinBA GENERATE 
	ResultNym::uid AS uid,
	ResultNym::scnt AS scnt,
	ResultNym::ave_session_time AS ave_session_time,
	ResultNym::payment AS payment,
	ResultNym::recency AS recency,
	ResultNym::cntBz AS cntBz,
	ResultNym::cntCm AS cntCm,
	ResultNym::cntNym AS cntNym,
	CntBA::cntBA AS cntBA
;


----------------------------------------------
--■企業への情報提供
--アンケート回答回数の取得、問い合わせ回数の取得
----------------------------------------------
EdIg = FOREACH FilData01 GENERATE uid, meta;
--アンケート回答回数
FilIg = FILTER EdIg BY meta == 'pmp_commu:question';

Grp = GROUP FilIg BY (uid,meta);
ResultIg = FOREACH Grp GENERATE FLATTEN(group), COUNT(FilIg.meta) AS cntIg; 

--コミュニティ系指標とのjoin
Joined = JOIN ResultBA BY uid LEFT OUTER , ResultIg BY uid;

ResultIg = FOREACH Joined GENERATE 
	ResultBA::uid AS uid,
	ResultBA::scnt AS scnt,
	ResultBA::ave_session_time AS ave_session_time,
	ResultBA::payment AS payment,
	ResultBA::recency AS recency,
	ResultBA::cntBz AS cntBz,
	ResultBA::cntCm AS cntCm,
	ResultBA::cntNym AS cntNym,
	ResultBA::cntBA AS cntBA,
	ResultIg::cntIg AS cntIg
;

Result = FOREACH ResultIg GENERATE uid,
			(scnt IS NULL ? 0 : scnt) AS scnt,
			(ave_session_time IS NULL ? 0 : ave_session_time) AS ave_session_time,
			(payment IS NULL ? 0 : payment) AS payment,
			(recency IS NULL ? 0 : recency) AS recency,
			(cntBz IS NULL ? 0 : cntBz) AS cntBz,
			(cntCm IS NULL ? 0 : cntCm) AS cntCm,
			(cntNym IS NULL ? 0 : cntNym) AS cntNym,
			(cntBA IS NULL ? 0 : cntBA) AS cntBA
--			(cntIg IS NULL ? 0 : cntIg) AS cntIg
;

STORE Result INTO '$PATH_OUTPUT' USING PigStorage();