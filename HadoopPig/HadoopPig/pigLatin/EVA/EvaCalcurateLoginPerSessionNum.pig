-----------------------------------------
--1 dailyのセッション数をカウント
--2 dailyのログイン数をカウント
--3 1,2をjoin
--4 ログイン数/セッション数を計算する
-----------------------------------------

--変数への格納
%declare TIME_WINDOW  30m
%declare START_DATE '2012-10-09'

--外部UDFの読み込み
REGISTER lib/datafu-0.0.4.jar

--UDFの呼び出し名の定義
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCharacterCategory myUDF.GetCharacterCategory();
define GetClient myUDF.GetClient();

--入出力パスの定義
%default PATH_INPUT_AWS 'works/input/aws/';
%default PATH_OUTPUT 'works/output/EVA/EvaCulucrateLoginRate1217';

--(1)-2データの対応付け　10月
RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) 必要なデータに絞る
EditData = FOREACH RowData GENERATE ISOFormat(time) AS time, GetClient(ap) AS client, uid, verb, cid;

--(3) Evaに絞る。
FilteredData = FILTER EditData BY (cid == 3) AND (SUBSTRING(time, 0, 10) >= '$START_DATE');

--(4) 不要な列（client, cid）を削除
EditData = FOREACH FilteredData GENERATE time, uid, verb;

--(5) セッションIDを振るためにuidでグループ化
Grouped = GROUP EditData BY uid; 

--(6) セッションIDの生成→{time, uid, verb, session_id}.time=20xx-xx-xxTxx:xx:xx000Z
Sessionize = FOREACH Grouped { 
    ord = ORDER EditData  BY time ASC;
    GENERATE FLATTEN(Sessionize(ord));
} 

--(7) timeを年月日に直して列の並べ替え
Edit = FOREACH Sessionize GENERATE uid, verb, session_id, SUBSTRING(time, 0, 10) AS time;

--(8) timeでグループ化
Grouped = GROUP Edit BY time;

--(9) session回数をカウント
countSession = FOREACH Grouped { 
    countS = DISTINCT Edit.session_id; 
    GENERATE FLATTEN(group) AS date, (int)COUNT(countS) AS scnt; 
} 

-------------------------------------------
--↑ここまででsession数のカウントは終了
--↓ここからdailyのlogin数をカウントする
Edit = FOREACH EditData GENERATE verb, SUBSTRING(time,0,10) AS date;

Filtered = FILTER Edit BY verb == 'login';

-- dateでグループ化
Grp = GROUP Filtered BY date;

-- login数のカウント
CntLogin = FOREACH Grp {
	login = Filtered.verb;
	GENERATE FLATTEN(group) AS date, (double)COUNT(login) AS cntLogin;
}

-------------------------------------------
--ここからjoinに入る
Joined = JOIN countSession BY date LEFT OUTER, CntLogin BY date USING 'replicated'; 

--データの整形
Ed = FOREACH Joined GENERATE 
	countSession::date AS date,
	countSession::scnt AS scnt,
	CntLogin::cntLogin AS cntLogin
; 

Result = FOREACH Ed GENERATE date, scnt, cntLogin, (double)(cntLogin/scnt) AS loginRate;

STORE Result INTO '$PATH_OUTPUT' using PigStorage('\t');