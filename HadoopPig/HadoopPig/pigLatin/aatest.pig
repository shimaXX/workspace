--REGISTER test.py USING jython AS myfuncs;

%default PATH_INPUT 'works/input/testdata';

x = LOAD '$PATH_INPUT' USING PigStorage(',');

DUMP x;

Data = FOREACH x GENERATE $0, $1;

DUMP Data;