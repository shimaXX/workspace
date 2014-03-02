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
%default PATH_INPUT_ORIG 'works/input/log_queue_activities_20120*xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/oct/2012-10-22';
%default PATH_OUTPUT 'works/output/Result_rev2';


--(1)-1データの対応付け　9月末まで
RowSepData = LOAD '$PATH_INPUT_ORIG' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;

--(1)-2データの対応付け　10月
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(1)-3データの対応付け　typeとuidのみのデータ
RowTypeData = LOAD '$PATH_INPUT_TYPE' USING PigStorage(',') AS (
  uid:chararray,type:chararray)
;

--(2)input dataの変数の選定
SepData = FOREACH RowSepData GENERATE ISOFormat(time) AS time , uid, verb, cid, GetClient(ap) AS client;  
OctData = FOREACH RowOctData GENERATE ISOFormat(time) AS time , uid, verb, cid, GetClient(ap) AS client;

--(3)フィルター処理
FilSepData = FILTER SepData BY (cid == 2) AND (client == 'sp');
FilOctData = FILTER OctData BY (cid == 2) AND (client == 'sp');
FilTypeData = FILTER RowTypeData BY type != '';

--(4) データのunion
FiledData = UNION FilSepData , FilOctData;

--(5) 元になるデータとTypeデータをjoin
JoinedData = JOIN FiledData BY uid LEFT OUTER, FilTypeData By uid;

--(6) join後の変数の選定
PicOutData = FOREACH JoinedData GENERATE 
	FiledData::time AS time,
	FiledData::uid AS uid,
	FiledData::verb AS verb,
	FilTypeData::type AS type
;

--(7) joinされたデータでtypeが振られていないユーザを削除：
--購入履歴があり、session回数が2回以上あり、指定した4つの行動回数に差が見られるもの（15回以上の購入者は異常値として除いた）
FixedData = FILTER PicOutData BY type != '';

--(7)-1 データの整形
FixedData = FOREACH FixedData GENERATE SUBSTRING(time,0,10) AS time, uid, verb, type;

--(8) グループ化(time,type,verb)
Grouped = GROUP FixedData BY (time, type, verb); 

--(9) 集計処理
ResultCnt = FOREACH Grouped {  
    cnt = FixedData.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS count;
} 

DESCRIBE ResultCnt;

--(10) グループ化(time,type)
Grouped = GROUP FixedData BY (time, type); 

--(11) 集計処理
ResultUU = FOREACH Grouped {  
    cnt = DISTINCT FixedData.uid;
    GENERATE FLATTEN(group), COUNT(cnt) AS count;
} 

--(12) dailyのseg毎のUUデータをjoin
JoinedData = JOIN ResultCnt BY (time, type) LEFT OUTER, ResultUU By (time, type);

DESCRIBE JoinedData;

--(13) join後の変数の選定
ResultAll = FOREACH JoinedData GENERATE 
	ResultCnt::group::time AS time,
	ResultCnt::group::type AS type,
	ResultCnt::group::verb AS verb,
	ResultCnt::count AS cnt,
	ResultUU::count AS UU
;

STORE ResultAll INTO '$PATH_OUTPUT' using PigStorage('\t');