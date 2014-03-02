--変数への格納
%declare TIME_WINDOW  30m

--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT_TYPE 'works/input/typeonlyPU.csv';
%default PATH_INPUT 'works/input/log_queue_activities_20120*xx.csv.gz';
%default PATH_OUTPUT 'works/output/TEST/getTranceVerbCount_comment';


--(1)データの対応付け
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;

--(1)-2データの対応付け　typeとuidのみのデータ
RowTypeData = LOAD '$PATH_INPUT_TYPE' USING PigStorage(',') AS (
  uid:chararray,type:chararray)
;

--(2) RowDataの再定義
RowData = FOREACH RowData GENERATE ISOFormat(time) AS time, uid, cid, verb, GetClient(ap) AS client;

--(3) フィルター処理
FiledData = FILTER RowData BY (cid == 2) AND (client == 'sp');
FilTypeData = FILTER RowTypeData BY type != '';

--(4) 元になるデータとTypeデータをjoin
JoinedData = JOIN FiledData BY uid LEFT OUTER, FilTypeData By uid USING 'replicated';

--(5) join後の変数の選定
PicOutData = FOREACH JoinedData GENERATE 
	FiledData::time AS time,
	FiledData::uid AS uid,
	FiledData::verb AS verb,
	FilTypeData::type AS type
;

--(6) joinされたデータでtypeが振られていないユーザを削除：
--購入履歴があり、session回数が2回以上あり、指定した4つの行動回数に差が見られるもの（15回以上の購入者は異常値として除いた）
FixedData = FILTER PicOutData BY type != '';
--FixedData = FILTER PicOutData BY type == 'new';
--FixedData = FILTER PicOutData BY type == 'search';
FixedData = FILTER PicOutData BY type == 'comment';
--FixedData = FILTER PicOutData BY type == 'category';

--(7) 不要なデータを削除
EditData = FOREACH FixedData GENERATE time, uid, verb;

Grouped = GROUP EditData BY uid; 

Result = FOREACH Grouped { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

Result02 = FOREACH Result GENERATE uid, verb, time, session_id;

----------------------------------------
--ここからはbuyを含むsessionのみの絞る
FilterBuy = FILTER Result02 BY verb == 'buy';

GroupedSession = GROUP FilterBuy BY session_id;

CountBuy = FOREACH GroupedSession { 
    filBuy = FilterBuy.verb;
    GENERATE FLATTEN(group) AS session_id, COUNT(filBuy) AS cntBuy;
} 

--大元とjoin
JoinedData = JOIN Result02 BY session_id LEFT OUTER ,CountBuy BY session_id  USING 'replicated';

EditData = FOREACH JoinedData GENERATE
	$0 AS uid,
	$1 AS verb,
	$2 AS time,
	$3 AS session_id,
	$5 AS cntBuy
;

Fil = FILTER EditData BY (chararray)cntBuy !=''; 

EditData = FOREACH Fil GENERATE $0 AS uid, $1 AS verb, $2 AS time, $3 AS session_id;

Grouped = GROUP EditData BY uid;

-------------------------
--ここからは連続するverbを獲得
Result03 = FOREACH Grouped { 
    ord02 = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(JuxtaposeNextVerb(ord02));
} 

--ここまでで各ユーザ毎のlastVerbとpostVerbの整形は終了
Result04 = FILTER Result03 BY postVerb != '' AND postVerb != verb;

--------------------------------------------------
--ここから重みのjoinのための処理に入る
Grouped = GROUP Result04 BY (verb, postVerb);

Result05 = FOREACH Grouped { 
    cnt = Result04.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS cnt;
} 

--Grouped = GROUP Result05 BY (verb, postVerb);

--lastVerbとpostVerbの組み合わせでまとめる
--これをResult04と結合する
--Result06 = FOREACH Grouped { 
--    GENERATE FLATTEN(Result05);
--} 

--JoinedData = JOIN
-- Result04 BY (verb, postVerb), 
-- Result06 BY (verb, postVerb)
-- USING 'replicated'
--;

--ResultData = FOREACH JoinedData GENERATE $0 AS uid, $1 AS lastVerb, $2 AS postVerb, $5 AS cnt;

--STORE ResultData INTO '$PATH_OUTPUT' using PigStorage('\t');
STORE Result05 INTO '$PATH_OUTPUT' using PigStorage('\t');