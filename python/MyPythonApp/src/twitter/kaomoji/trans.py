# coding: utf-8
'''
Created on 2014/02/20

@author: nahki
'''

import cnvk

if __name__=='__main__':
    ex_word = ''
    of = open('kaomoji_zenkaku.csv', 'w',1000)
    with open('kaomoji_jisho.txt', 'r', 1000) as f:
        for line in f:
            word = cnvk.convert(line.upper(), cnvk.Z_NUM, cnvk.Z_ALPHA, cnvk.Z_KIGO, cnvk.Z_KATA).strip()
            if word == ex_word:
                ex_word = word
                print word
                continue
            cost = int(max(-32768, 6000 - 200*len(word)**1.3))
            res = u"%s,,,%d,名詞,一般,*,*,*,*,*,*,*,%s\n" % (word, cost, u"kaomoji")
            of.write(res)
            ex_word = word
    of.close()