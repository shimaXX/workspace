--���o�̓p�X�̒�`
%default PATH_INPUT 'works/input/';
%default PATH_OUTPUT 'works/output/galster_verb_day';
--data/log_queue_activities_20120*xx.csv.gz

--(1)�f�[�^�̑Ή��t��
RowData = LOAD '$PATH_INPUT' USING PigStorage() AS (
  f0, f1, verb:chararray, ap:chararray, cid:int, uid:chararray, f6, f7, f8, f9, f10, f11, f12,time:chararray)
;

ThinData = FOREACH RowData GENERATE uid, verb, cid, SUBSTRING(time, 0, 10) AS day;
FilteredData = FILTER ThinData BY cid == 2;
Grouped = GROUP FilteredData BY (uid, day, verb); 

--user,��,verb���Ƀf�[�^�_�����J�E���g
Result01 = FOREACH Grouped { 
    verb_count = FilteredData.verb; 
    GENERATE FLATTEN(group), (int)COUNT(verb_count) AS vcnt; 
} 

--�J�E���g�����f�[�^�����user,verb���ɓ����σA�N�V�����񐔂��Z�o
Grouped02 = GROUP Result01 BY (uid, verb);

Result02 = FOREACH Grouped { 
    cnt = Result01.uid;
    sm = (int)Result01.vcnt;
    GENERATE FLATTEN(group), (int)SUM(sm) AS sm, (int)COUNT(cnt) AS cnt; 
} 

STORE Result02 INTO '$PATH_OUTPUT' using PigStorage('\t');