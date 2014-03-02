# coding: utf-8

import MeCab
s = u"「」形態素解析には「MeCab」を使っているので上のプログラムを動かすには事前にインストールが必要です。 かわいい！"
tagger = MeCab.Tagger('-Ochasen')
node = tagger.parseToNode(s.encode('utf-8'))
wordList = []
while node:
    print node.feature
    if node.feature.split(",")[0] == "名詞":
        wordList.append(node.surface)
    node = node.next
for word in wordList:
    print word.decode('utf-8')