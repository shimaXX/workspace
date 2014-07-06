--�ϐ��ւ̊i�[
%declare TIME_WINDOW  30m

--�O��UDF�̓ǂݍ���
REGISTER lib/datafu-0.0.4.jar

--UDF�̌Ăяo�����̒�`
define Sessionize datafu.pig.sessions.Sessionize('$TIME_WINDOW');
define ISOFormat myUDF.ISO8601Format();
define JuxtaposeNextVerb myUDF.JuxtaposeNextVerb();
define GetCategoryId myUDF.GetCategoryId();
define GetClient myUDF.GetClient();

--���o�̓p�X�̒�`
--%default PATH_INPUT 'works/input/log_queue_activities_201207xx.csv.gz';
%default PATH_INPUT_OCT 'works/input/oct/';
%default PATH_OUTPUT 'works/output/actionGraph';
%default PATH_OUTHOGE 'works/output/EVA/EvaCountCharacter';

--(1)-2�f�[�^�̑Ή��t���@10��
RowOctData = LOAD '$PATH_INPUT_OCT' USING PigStorage() AS (
  f0, verb:chararray, ap:chararray, cid:int, uid:chararray,time:chararray)
;

--(2) �K�v�ȃf�[�^�ɍi��
EditData = FOREACH RowOctData GENERATE uid, verb, cid, GetClient(ap) AS client, ap, GetCategoryId(ap) AS categoryId ,time;

--(3) EVA�ɍi��
FilteredData = FILTER EditData BY (cid == 3) AND (SUBSTRING(time, 0, 10) > '2012-10-24');

--(4) �s�v�ȗ�icid�j���폜
EditData = FOREACH FilteredData GENERATE uid, verb, categoryId;

--(4)-1 uid�݂̂ɍi��
Uids = FOREACH EditData GENERATE uid;

--(5) uid
Result = DISTINCT Uids; 

------------------------------------
--�����܂ł̓��j�[�N���[�U�̓���
--��������͊e�L�����N�^���̋L���������񐔂��W�v����B�̂���join����
--(6) ���C�̏W�v
FilteredRei = FILTER EditData BY (categoryId == '45');

Grouped = GROUP FilteredRei BY (uid, categoryId); 

ResultRei = FOREACH Grouped { 
    rei_count = FilteredRei.uid; 
    GENERATE FLATTEN(group), COUNT(rei_count) AS reiCnt; 
} 

--(7) �A�X�J�̏W�v
FilteredAsuka = FILTER EditData BY (categoryId == '46');

Grouped = GROUP FilteredAsuka BY (uid, categoryId); 

ResultAsuka = FOREACH Grouped { 
    asuka_count = FilteredAsuka.uid; 
    GENERATE FLATTEN(group), COUNT(asuka_count) AS asukaCnt; 
} 

--(8) �}���J�̏W�v
FilteredMarika = FILTER EditData BY (categoryId == '47');

Grouped = GROUP FilteredMarika BY (uid, categoryId); 

ResultMarika = FOREACH Grouped { 
    marika_count = FilteredMarika.uid; 
    GENERATE FLATTEN(group), COUNT(marika_count) AS marikaCnt; 
} 

--(9) �V���W�̏W�v
FilteredShinji = FILTER EditData BY (categoryId == '48');

Grouped = GROUP FilteredShinji BY (uid, categoryId); 

ResultShinji = FOREACH Grouped { 
    shinji_count = FilteredShinji.uid; 
    GENERATE FLATTEN(group), COUNT(shinji_count) AS shinjiCnt; 
} 

--(10) �J�����̏W�v
FilteredKaoru = FILTER EditData BY (categoryId == '49');

Grouped = GROUP FilteredKaoru BY (uid, categoryId); 

ResultKaoru = FOREACH Grouped { 
    kaoru_count = FilteredKaoru.uid; 
    GENERATE FLATTEN(group), COUNT(kaoru_count) AS kaoruCnt; 
} 

--(11) �~�T�g�̏W�v
FilteredMisato = FILTER EditData BY (categoryId == '50');

Grouped = GROUP FilteredMisato BY (uid, categoryId); 

ResultMisato = FOREACH Grouped { 
    misato_count = FilteredMisato.uid; 
    GENERATE FLATTEN(group), COUNT(misato_count) AS misatoCnt; 
} 

--(12) �G���@�̏W�v
FilteredEva = FILTER EditData BY (categoryId == '51');

Grouped = GROUP FilteredEva BY (uid, categoryId); 

ResultEva = FOREACH Grouped { 
    eva_count = FilteredEva.uid; 
    GENERATE FLATTEN(group), COUNT(eva_count) AS evaCnt; 
} 

-----------------------------
--�ȏ��join�̂��߂̃p�[�c�͍쐬�ł���
--���������join����Bpig��1�Â���join�o���Ȃ��̂ŁA������join����

--(13) �܂��̓��C����join
JoinRei = JOIN Result BY uid LEFT OUTER , ResultRei BY uid USING 'replicated';
PicOutData01 = FOREACH JoinRei GENERATE 
	Result::uid AS uid,
	ResultRei::reiCnt AS reiCnt
;

--(14) �A�X�J��join
JoinAsuka = JOIN PicOutData01 BY uid LEFT OUTER , ResultAsuka BY uid USING 'replicated';
PicOutData02 = FOREACH JoinAsuka GENERATE 
	PicOutData01::uid AS uid,
	PicOutData01::reiCnt AS reiCnt,
	ResultAsuka::asukaCnt AS asukaCnt
;

--(15) �}���J��join
JoinMarika = JOIN PicOutData02 BY uid LEFT OUTER , ResultMarika BY uid USING 'replicated';
PicOutData03 = FOREACH JoinMarika GENERATE 
	PicOutData02::uid AS uid,
	PicOutData02::reiCnt AS reiCnt,
	PicOutData02::asukaCnt AS asukaCnt,
	ResultMarika::marikaCnt AS marikaCnt
;

--(16) �V���W��join
JoinShinji = JOIN PicOutData03 BY uid LEFT OUTER , ResultShinji BY uid USING 'replicated';
PicOutData04 = FOREACH JoinShinji GENERATE 
	PicOutData03::uid AS uid,
	PicOutData03::reiCnt AS reiCnt,
	PicOutData03::asukaCnt AS asukaCnt,
	PicOutData03::marikaCnt AS marikaCnt,
	ResultShinji::shinjiCnt AS shinjiCnt
;

--(17) �J������join
JoinKaoru = JOIN PicOutData04 BY uid LEFT OUTER , ResultKaoru BY uid USING 'replicated';
PicOutData05 = FOREACH JoinKaoru GENERATE 
	PicOutData04::uid AS uid,
	PicOutData04::reiCnt AS reiCnt,
	PicOutData04::asukaCnt AS asukaCnt,
	PicOutData04::marikaCnt AS marikaCnt,
	PicOutData04::shinjiCnt AS shinjiCnt,
	ResultKaoru::kaoruCnt AS kaoruCnt
;

--(18) �~�T�g��join
JoinMisato = JOIN PicOutData05 BY uid LEFT OUTER , ResultMisato BY uid USING 'replicated';
PicOutData06 = FOREACH JoinMisato GENERATE 
	PicOutData05::uid AS uid,
	PicOutData05::reiCnt AS reiCnt,
	PicOutData05::asukaCnt AS asukaCnt,
	PicOutData05::marikaCnt AS marikaCnt,
	PicOutData05::shinjiCnt AS shinjiCnt,
	PicOutData05::kaoruCnt AS kaoruCnt,
	ResultMisato::misatoCnt AS misatoCnt
;

--(19) �G���@��join
JoinEva = JOIN PicOutData06 BY uid LEFT OUTER , ResultEva BY uid USING 'replicated';
FinalData = FOREACH JoinEva GENERATE 
	PicOutData06::uid AS uid,
	PicOutData06::reiCnt AS reiCnt,
	((int)PicOutData06::asukaCnt > 0 ? (int)PicOutData06::asukaCnt : 0) AS asukaCnt,
	((int)PicOutData06::marikaCnt > 0 ? (int)PicOutData06::marikaCnt : 0) AS marikaCnt,
	((int)PicOutData06::shinjiCnt > 0 ? (int)PicOutData06::shinjiCnt : 0) AS shinjiCnt,
	((int)PicOutData06::kaoruCnt > 0 ? (int)PicOutData06::kaoruCnt : 0) AS kaoruCnt,
	((int)PicOutData06::misatoCnt > 0 ? (int)PicOutData06::misatoCnt : 0) AS misatoCnt,
	((int)ResultEva::evaCnt > 0 ? (int)ResultEva::evaCnt : 0) AS evaCnt
;


STORE FinalData INTO '$PATH_OUTHOGE' using PigStorage('\t');