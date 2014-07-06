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
%default PATH_INPUT_TYPE 'works/input/EVAtypeonlyPU.csv';
%default PATH_INPUT_OCT 'works/input/aws/2012-11-*gz';
%default PATH_OUTPUT 'works/output/EVA/Transe1114Search';


--(1)-2データの対応付け
RowData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(1)-3データの対応付け　typeとuidのみのデータ
RowTypeData = LOAD '$PATH_INPUT_TYPE' USING PigStorage(',') AS (
  uid:chararray,type:chararray)
;

--(2)input dataの変数の選定
EditData = FOREACH RowData GENERATE ISOFormat(time) AS time , uid, verb, cid, GetClient(ap) AS client;

--(3)フィルター処理
FilData = FILTER EditData BY (cid == 3) AND (SUBSTRING(time, 0, 10) > '2012-10-31');
FilTypeData = FILTER RowTypeData BY type != '';

--(4) データのunion
--FiledData = UNION FilSepData , FilOctData;

--(5) 元になるデータとTypeデータをjoin
JoinedData = JOIN FilData BY uid LEFT OUTER, FilTypeData By uid;

--(6) join後の変数の選定
PicOutData = FOREACH JoinedData GENERATE 
	FilData::time AS time,
	FilData::uid AS uid,
	FilData::verb AS verb,
	FilTypeData::type AS type
;

--(7) joinされたデータでtypeが振られていないユーザを削除：
--購入履歴があり、行動回数が2回以上あり、指定した4つの行動回数に差が見られるもの
--FixedData = FILTER PicOutData BY type != '';
--FixedData = FILTER PicOutData BY type == 'new';
FixedData = FILTER PicOutData BY type == 'search';
--FixedData = FILTER PicOutData BY type == 'comment';
--FixedData = FILTER PicOutData BY type == 'category';


--(8) グループ化(time,type,verb)
Grouped = GROUP FixedData BY (uid); 

Result = FOREACH Grouped { 
    ord = ORDER FixedData BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

Result02 = FOREACH Result GENERATE uid AS uid, verb AS verb, time AS time, session_id AS session_id;

Grouped = GROUP Result02 BY session_id;

Result03 = FOREACH Grouped { 
    ord02 = ORDER Result02  BY time ASC;
    GENERATE FLATTEN(JuxtaposeNextVerb(ord02));
} 

--ここまでで各ユーザ毎のlastVerbとpostVerbの整形は終了
Result04 = FILTER Result03 BY postVerb != '';

--------------------------------------------------
Grouped = GROUP Result04 BY (verb, postVerb);

Result05 = FOREACH Grouped { 
    cnt = Result04.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS cnt;
} 

STORE Result05 INTO '$PATH_OUTPUT' using PigStorage('\t');