--入力データファイルパスを設定
--(%が付いているのもはコマンドラインから設定出来る)
%default PATH_INPUT 'works/input/testdata';

--データの読み込み
x = LOAD '$PATH_INPUT' USING PigStorage(',') AS 
(
  code:chararray, date:chararray, cnt:int
);

--入力データの表示
DUMP x;

--codeだけにデータを絞って表示
Data = FOREACH x GENERATE code;
DUMP Data;

--日付毎にcntの合計値を取得
grouped = Group x BY date;
sumCntEachDate = FOREACH grouped GENERATE SUM(x.cnt) as cntSum;
DUMP sumCntEachDate;