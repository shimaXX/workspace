# coding: utf-8
'''
Created on 2013/11/24

@author: nahki
'''
import MeCab

# 無視すべき単語のリスト
ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it', 'の'])
igonoresymbols = set(['-', '/', '#', "'", '_', ',', '(', ')', '[', ']',
                     '~', '!', '|', '♪', '...', '>', '<', ':', '!',
                      '&', '/', '+', '*', '【', '】', '（', '）', '！', '：', 'ー',
                      '＿', '？','%', '「', '」','～','.', '{', '}','"',
                      '＜', '＞', '／'])

def separateWords(text):
    tagger = MeCab.Tagger('-Ochasen')
    node = tagger.parseToNode(text.encode('utf-8'))
    word_set = set([])
    while node:
        feat = node.feature.split(",")
        if feat[0] == "名詞" \
                and (feat[1] == "一般" # 接尾はどうするか
                or feat[1] == "固有名詞" or feat[1] == "形容動詞語幹"):
            #word = node.surface.decode(en)
            word = node.surface
            if word not in ignorewords:
                word_set.add( word )
        node = node.next
    return word_set