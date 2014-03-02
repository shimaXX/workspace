--変数への格納
--%declare TIME_WINDOW  30m

--外部UDFの読み込み
--REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
--define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
--define ISOFormat myUDF.ISO8601Format();
--define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
--define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT 'works/input/sample.txt';
%default PATH_OUTPUT 'works/output/test';


--(1) データの対応付け
RawData = LOAD '$PATH_INPUT' USING PigStorage('\t') AS (
  time:chararray, id:chararray, domain:chararray, ip:chararray, zip:chararray)
;

--(2) 変数の選定
Data = FOREACH RawData GENERATE SUBSTRING(time, 16, 24) AS time , domain, CONCAT(domain, SUBSTRING(time, 16, 24)) AS dtime;

--(3) 変数操作
Med = FOREACH Data GENERATE time, domain, dtime, ( 
  CASE
     WHEN time<'10:00:00' THEN '_tseg1' 
     WHEN time>='10:00:00' AND time<'20:00:00' THEN '_tseg2' 
     ELSE '_tseg3' 
  END 
) AS seg;

--(4) ドメインとセグメントのクロス
res = FOREACH Med GENERATE time, domain, seg, CONCAT(domain, seg) AS dseg;

DUMP res;

--STORE Result06 INTO '$PATH_OUTPUT' using PigStorage('\t');