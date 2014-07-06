--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE  '2012-10-09' --つまり29日からのデータを取得する
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
define GetMetaInfo myUDF.GetMetaInfo(); 
define GetNextDate myUDF.GetNextDate();
define GetRewards myUDF.GetRewards();
--define CountBadges myUDF.TestCountBadges();
define CountBadges myUDF.CountBadges();
define TestTmp myUDF.TestTmp();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/test/2012-12-20*';
%default PATH_OUTPUT 'works/output/TEST/EvaBadgeTime1209';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray,f6,rb:chararray)
;

--rewardsのみ取ってくる。rewardsが空の場合はNULLとしている。
Edit = FOREACH RowData GENERATE uid, SUBSTRING(time,0,10) AS time, cid, GetRewards(rb) AS badges;

FilData = FILTER Edit BY (cid == 7 OR cid==8) AND time > '$START_DATE';

Grp = GROUP FilData BY (uid,time);

Result = FOREACH Grp GENERATE FLATTEN(group) AS (uid,time) ,FLATTEN(CountBadges(FilData.badges)) AS (RN ,CntBdg);

STORE Result INTO '$PATH_OUTPUT' USING PigStorage();