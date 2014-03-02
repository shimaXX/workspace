# coding: utf-8
'''
Created on 2014/02/18

@author: nahki
'''

import MeCab
import cnvk
import unicodedata
from separatewords import MecabTokenize

tagger = MeCab.Tagger("-Ochasen")


# 明日のジェル検。めっちゃ緊張する…。お腹痛い＿（´；ω；‘＿）⌒）＿。ハンドモデルママンにお願いするけど。ママンの爪大丈夫かしら…？。いまさら不安…
text = cnvk.convert(u'明日ママ を 芦田愛菜 に空目。',
                     cnvk.Z_NUM, cnvk.Z_ALPHA, cnvk.Z_KIGO, cnvk.Z_KATA)
res = MecabTokenize.tokenize(text)
print res
for r in res:
    print "result",r
"""
node = tagger.parseToNode(text.encode('utf-8')) #(´・ω・｀)
while node:
    #print "%s %s" % (node.surface, node.feature)
    print node.surface, node.feature
    node = node.next
"""