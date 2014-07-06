------------------------------------
--サンプル注文したユーザのその後の行動トラッキング
------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-11-07' --つまり08日からのデータを取得する


--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategory myUDF.GetCategory();
define GetClient myUDF.GetClient();
define GetMetaInfo myUDF.GetMetaInfoForCiLabo();

--入出力パスの定義
%default PATH_INPUT_OCT 'works/input/ci-labo/';
%default PATH_OUTPUT 'works/output/Ci-Labo/Ci-LaboTrack1203';

--(1)-2データの対応付け
RowData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, verb, cid, SUBSTRING(time,0,10) AS days, GetMetaInfo(verb, ap) AS meta;

--(3) ci-laboに絞る
FilteredData = FILTER EditData BY cid == 4 AND days > '$START_DATE';

--(4) 不要な列（cid）を削除
EditData = FOREACH FilteredData GENERATE time, uid, meta;


-----------------------------------------------------------
--(5) セッションIDを振る
Grp = GROUP EditData BY uid;

addSession = FOREACH Grp { 
    ord = ORDER EditData BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

-- metaでverb:sampleのみのデータを取得し、そのセッションを取得する
getSampleSessionId = FILTER addSession BY meta == 'view:sample';

------------------------------------------------------------
-- joinする
Joined = JOIN addSession BY session_id , getSampleSessionId BY session_id;

-- データの取捨選択
Edit = FOREACH Joined GENERATE 
	$0 AS time,
	$1 AS uid,
	$2 AS meta,
	$3 AS origSessionId,
	$4 AS sampleTime,
	$7 AS sessionId 
;

Fil  = FILTER Edit BY origSessionId == sessionId AND time >= sampleTime;

--不要なデータを捨てる
Ed = FOREACH Fil GENERATE uid, meta, time,origSessionId;

-------------------------------------------------------------
-- sample後の行動を取得
Grouped = GROUP Ed BY origSessionId;

ResultJux = FOREACH Grouped { 
    ord02 = ORDER Ed  BY time ASC;
    GENERATE FLATTEN(JuxtaposeNextVerb(ord02));
} 

--------------------------------------------------
--ここから重みのjoinのための処理に入る
Grouped = GROUP ResultJux BY (verb, postVerb);


Result05 = FOREACH Grouped { 
    cnt = ResultJux.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS cnt;
} 

Grouped = GROUP Result05 BY (verb, postVerb);

--lastVerbとpostVerbの組み合わせでまとめる
--これをResult04と結合する
Result06 = FOREACH Grouped { 
    GENERATE FLATTEN(Result05);
} 

JoinedData = JOIN
 ResultJux BY (verb, postVerb), 
 Result06 BY (verb, postVerb)
 USING 'replicated'
;

Result = FOREACH JoinedData GENERATE $1 AS lastVerb, $2 AS postVerb, $5 AS cnt;

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');