-----------------------------------------
--請求費用を算出するために必要なパラメータを見るためのコード
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
%default PATH_OUTPUT 'works/output/Minig/Ci-LaboKPI20130201';

RowData = LOAD '$PATH_INPUT_AWS' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--------------------------------
--対象者の絞り込みを行う
Edit = FOREACH RowData GENERATE SUBSTRING(time, 0, 10) AS date, uid, cid,
	GetPayment(ap) AS payment,  GetMetaInfo(verb, ap) AS meta;
FilData = FILTER Edit BY cid == 8 AND date >= '$START_DATE';

--------------------------------
--DAU
Grp = GROUP FilData BY date;
DAU = FOREACH Grp {
	uu = DISTINCT FilData.uid;
	GENERATE FLATTEN(group) AS date, COUNT(uu) AS DAU;
}

--------------------------------
--直帰じゃないユーザ数
Grp = GROUP FilData BY uid; 
CntPV = FOREACH Grp GENERATE FLATTEN(group) AS uid, COUNT(FilData.meta) AS cntPV;

Fil = FILTER CntPV by cntPV > 1;

Joined = JOIN Fil BY uid , FilData BY uid USING 'replicated';

Ed = FOREACH Joined GENERATE
	Fil::uid AS uid,
	FilData::date AS date
;

Grp = GROUP Ed BY date;
CntPV2 = FOREACH Grp {
	uu = DISTINCT Ed.uid;
	GENERATE FLATTEN(group) AS date, COUNT(uu) AS PV2;
}


--------------------------------
--商品ページ閲覧ユーザ
Fil = FILTER FilData BY meta == 'view:goods';

Grp = GROUP Fil BY date;
CntViewGoods = FOREACH Grp {
	uu = DISTINCT Fil.uid;
	GENERATE FLATTEN(group) AS date, COUNT(uu) AS cntViewGoods;
}

--------------------------------
--カート投入ユーザ数
Fil = FILTER FilData BY meta == 'cart:item';

Grp = GROUP Fil BY date;
CntCart = FOREACH Grp{
	uu = DISTINCT Fil.uid;
	GENERATE FLATTEN(group) AS date, COUNT(uu) AS cntCartItem;
}

--------------------------------
--購買者数
Fil = FILTER FilData BY meta == 'buy';

Grp = GROUP Fil BY date;
CntBuy = FOREACH Grp{
	uu = DISTINCT Fil.uid;
	GENERATE FLATTEN(group) AS date, COUNT(uu) AS cntBuy;
}

--------------------------------
--総購買額
Grp = GROUP FilData BY date;
SmPayment = FOREACH Grp GENERATE FLATTEN(group) AS date, SUM(FilData.payment) AS payment;


--------------------------------
--それぞれの値をjoinし、割り算値を算出
Joined01 = JOIN DAU BY date LEFT OUTER, CntPV2 BY date USING 'replicated';
Res01 = FOREACH Joined01 GENERATE
	DAU::date AS date,
	DAU::DAU AS DAU,
	CntPV2::PV2 AS PV2
; 

Joined02 = JOIN Res01 BY date LEFT OUTER, CntViewGoods BY date USING 'replicated';
Res02 = FOREACH Joined02 GENERATE
	Res01::date AS date,
	Res01::DAU AS DAU,
	Res01::PV2 AS PV2,
	CntViewGoods::cntViewGoods AS cntGoods
; 

Joined03 = JOIN Res02 BY date LEFT OUTER, CntCart BY date USING 'replicated';
Res03 = FOREACH Joined03 GENERATE
	Res02::date AS date,
	Res02::DAU AS DAU,
	Res02::PV2 AS PV2,
	Res02::cntGoods AS cntGoods,
	CntCart::cntCartItem AS cntCartItem
; 

Joined04 = JOIN Res03 BY date LEFT OUTER, CntBuy BY date USING 'replicated';
Res04 = FOREACH Joined04 GENERATE
	Res03::date AS date,
	Res03::DAU AS DAU,
	Res03::PV2 AS PV2,
	Res03::cntGoods AS cntGoods,
	Res03::cntCartItem AS cntCartItem,
	CntBuy::cntBuy AS cntBuy
; 

Joined05 = JOIN Res04 BY date LEFT OUTER, SmPayment BY date USING 'replicated';
Res05 = FOREACH Joined05 GENERATE
	Res04::date AS date,
	Res04::DAU AS DAU,
	Res04::PV2 AS PV2,
	Res04::cntGoods AS cntGoods,
	Res04::cntCartItem AS cntCartItem,
	Res04::cntBuy AS cntBuy,
	SmPayment::payment AS payment
; 

Result = FOREACH Res05 GENERATE date, DAU , PV2, cntGoods, cntCartItem, cntBuy, payment,
			(double)PV2/(double)DAU , (double)cntGoods/(double)PV2, (double)cntCartItem/(double)cntGoods, 
			(double)cntBuy/(double)cntCartItem, (double)payment/(double)cntBuy; 

STORE Result INTO '$PATH_OUTPUT' USING PigStorage();