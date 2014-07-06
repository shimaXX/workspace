----------------------------------------
--期間内session回数
--期間内平均session時間
--期間内購入総額 ⇒ 上手く値が出ないため、最適化関数による最適を狙う（annealingOprimize）
--期間末と期間内の最終アクション日の差
----------------------------------------

--変数への格納
%declare TIME_WINDOW  30m

%declare START_DATE  '2012-10-31' --つまり11/1日からのデータを取得する
%declare LAST_DATE  '2012-11-15' --つまり14日までのデータを取得する
%declare EXSTART_DATE  '2012-10-17' --つまり10/18日からのデータを取得する
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
define GetSessionTime myUDF.GetSessionTime();
define GetPriorIntervalDate myUDF.GetIntervalDate('$EXLAST_DATE');
define GetPostIntervalDate myUDF.GetIntervalDate('$LAST_DATE');

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT_PRIOR 'works/output/GAMIFICATION/EVA/RFMpriorCnt1122';
%default PATH_OUTPUT_POST 'works/output/GAMIFICATION/EVA/RFMpostCnt1122';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

EditData = FOREACH RowData GENERATE uid, cid, verb, ISOFormat(time) AS time,GetPayment(ap) AS payment, SUBSTRING(time,0,10) AS days;

FilData01 = FILTER EditData BY cid ==3 AND days > '$EXSTART_DATE' AND days < '$EXLAST_DATE';
FilData02 = FILTER EditData BY cid ==3 AND days > '$START_DATE' AND days < '$LAST_DATE';

--------------------------------------------
--------------------------------------------
--【まずは閾値より前のデータを取得】
--セッション数の取得---------------------------------
--(4) 不要な列（client, cid）を削除
Ed = FOREACH FilData01 GENERATE time, uid, verb;

--(5) セッションIDを振るためにuidでグループ化
Grouped = GROUP Ed BY uid; 

--(6) セッションIDの生成→{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
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
--Ed = FOREACH FilData01 GENERATE uid, verb;

--Fil = FILTER Ed BY verb == 'buy';

--Grp = GROUP Ed BY uid;

--ResultPayment01 =  FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(Ed.verb) AS cntBuy;


--期間内最終行動日を取得する------------------------------------
--(2) 必要なデータに絞る
Ed = FOREACH FilData01 GENERATE uid, cid, SUBSTRING(time, 0, 10) AS time;

--(3) galsterに絞る。spに絞る。
FilteredData = FILTER Ed BY cid == 3;

--(4) 不要な列（client, cid）を削除
Ed = FOREACH FilteredData GENERATE uid, time;

--(5) uidでグループ化
Grouped = GROUP Ed BY (uid); 

getMaxStamp = FOREACH Grouped { 
    row_time = Ed.time; 
    GENERATE FLATTEN(group) AS uid, MAX(row_time) AS lastDate; 
}

--定義の段階でterminalに+1した日付が入っているため、-1する
ResultRecency01 = FOREACH getMaxStamp GENERATE uid, GetPriorIntervalDate(lastDate) - 1.0 AS recency;


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
	--TMP0102::cntBuy AS cntBuy,
	ResultRecency01::recency AS recency 
;



--------------------------------------------
--------------------------------------------
--【閾値より後のデータを取得】
--セッション数の取得---------------------------------
--(4) 不要な列（client, cid）を削除
Ed = FOREACH FilData02 GENERATE time, uid, verb;

--(5) セッションIDを振るためにuidでグループ化
Grouped = GROUP Ed BY uid; 

--(6) セッションIDの生成→{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize02 = FOREACH Grouped { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) timeを年月日に直して列の並べ替え
Ed = FOREACH Sessionize02 GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) session回数をカウント
GroupUid = GROUP Ed BY uid;

--(9) session回数をカウント
ResultCountSession02 = FOREACH GroupUid { 
    countS = DISTINCT Ed.session_id; 
    GENERATE FLATTEN(group) AS uid, (int)COUNT(countS) AS scnt; 
} 


--セッション時間---------------------------------
--Sessionizeは先頭にtimeが必要
--Edに使用されているSessionizeは上のセッション回数をカウントするときに取ったもの
Ed = FOREACH Sessionize02 GENERATE uid, SUBSTRING(time, 0, 10) AS date, time, session_id;

Grp = GROUP Ed BY (uid, session_id);

sessionTime = FOREACH Grp { 
    ord = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(group) AS (uid ,session_id), FLATTEN(GetSessionTime(ord.time)) AS session_time;
} 

sessionTime = FILTER sessionTime BY (chararray)session_time != '';

grpDaily = GROUP sessionTime BY uid;  

ResultSessionTime02 = FOREACH grpDaily  GENERATE FLATTEN(group) AS uid, AVG(sessionTime.session_time) AS ave_session_time;


--購入総額---------------------------------
Ed = FOREACH FilData02 GENERATE uid, payment;

Grp = GROUP Ed BY uid;

ResultPayment02 =  FOREACH Grp GENERATE FLATTEN(group) AS uid, SUM(Ed.payment) AS payment;


--購入回数---------------------------------
--Ed = FOREACH FilData02 GENERATE uid, verb;

--Fil = FILTER Ed BY verb == 'buy';

--Grp = GROUP Ed BY uid;

--ResultPayment02 =  FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(Ed.verb) AS cntBuy;


--期間内最終行動日を取得する------------------------------------
--(2) 必要なデータに絞る
Ed = FOREACH FilData02 GENERATE uid, cid, SUBSTRING(time, 0, 10) AS time;

--(3) galsterに絞る。spに絞る。
FilteredData = FILTER Ed BY cid == 3;

--(4) 不要な列（client, cid）を削除
Ed = FOREACH FilteredData GENERATE uid, time;

--(5) uidでグループ化
Grouped = GROUP Ed BY (uid); 

getMaxStamp = FOREACH Grouped { 
    row_time = Ed.time; 
    GENERATE FLATTEN(group) AS uid, MAX(row_time) AS lastDate; 
}

--定義の段階でterminalに+1した日付が入っているため、-1する
ResultRecency02 = FOREACH getMaxStamp GENERATE uid, GetPostIntervalDate(lastDate) - 1.0 AS recency;


---------------------------------------------------
--ここからはjoin
--セッション回数とセッション時間
joined0201 = JOIN ResultCountSession02 BY uid LEFT OUTER, ResultSessionTime02 BY uid USING 'replicated';

TMP0201 = FOREACH joined0201 GENERATE 
	ResultCountSession02::uid AS uid,
	ResultCountSession02::scnt AS scnt,
	ResultSessionTime02::ave_session_time AS ave_session_time 
;

joined0202 = JOIN TMP0201 BY uid LEFT OUTER, ResultPayment02 BY uid USING 'replicated';

TMP0202 = FOREACH joined0202 GENERATE 
	TMP0201::uid AS uid,
	TMP0201::scnt AS scnt,
	TMP0201::ave_session_time AS ave_session_time,
	ResultPayment02::payment AS payment
	--ResultPayment02::cntBuy AS cntBuy  
;

joined0203 = JOIN TMP0202 BY uid LEFT OUTER, ResultRecency02 BY uid USING 'replicated';

Result02 = FOREACH joined0203 GENERATE 
	TMP0202::uid AS uid,
	TMP0202::scnt AS scnt,
	TMP0202::ave_session_time AS ave_session_time,
	TMP0202::payment AS payment,
	--TMP0202::cntBuy AS cntBuy,
	ResultRecency02::recency AS recency 
;



------------------------------------------------
------------------------------------------------
--前と後をinner joinし前のユーザに合わせる
--session timeがあるユーザだけにfilterする
--さらに前と後に分割する
jnd = JOIN Result01 BY uid , Result02 BY uid USING 'replicated';  

TMP = FOREACH jnd GENERATE 
	Result01::uid AS uid,
	Result01::scnt AS scntPrior,
	Result01::ave_session_time AS sessionTimePrior,
	Result01::payment AS paymentPrior,
	--Result01::cntBuy AS cntBuyPrior,
	Result01::recency AS recencyPrior,
	Result02::scnt AS scntPost,
	Result02::ave_session_time AS sessionTimePost,
	Result02::payment AS paymentPost,
	--Result02::cntBuy AS cntBuyPost,
	Result02::recency AS recencyPost
;

Fil = FILTER TMP BY (chararray)sessionTimePrior != '' AND (chararray)sessionTimePost != '';

--購入金額用
ResultPrior = FOREACH Fil GENERATE uid, scntPrior, sessionTimePrior, paymentPrior, recencyPrior;
ResultPost = FOREACH Fil GENERATE uid, scntPost, sessionTimePost, paymentPost, recencyPost;

--購入回数用
--ResultPrior = FOREACH Fil GENERATE uid, scntPrior, sessionTimePrior, cntBuyPrior, recencyPrior;
--ResultPost = FOREACH Fil GENERATE uid, scntPost, sessionTimePost, cntBuyPost, recencyPost;


---------------------------------------------------
--データ出力
STORE ResultPrior INTO '$PATH_OUTPUT_PRIOR' USING PigStorage('\t');
STORE ResultPost INTO '$PATH_OUTPUT_POST' USING PigStorage('\t');