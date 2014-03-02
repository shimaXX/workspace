# -*- encoding: utf-8 -*-
import sys
import re
import codecs
import unicodedata
import cnvk

if __name__ == "__main__":
#   argvs = sys.argv
#   argc = len(argvs)
#   if (argc != 3):
#     print 'Usage: # python %s Input_FileName Output_FileName' % argvs[0]
#     quit()

  fin_name = 'jawiki-latest-all-titles-in-ns0'
  fout_name = 'wikipedia.csv'

  fin = codecs.open(fin_name, "r", "utf-8")
  fout = codecs.open(fout_name, "w", "utf-8")
  for line in fin:
    word = line.rstrip() 
    if len(word) <= 3: continue
    if re.compile(r'^[-.0-9]+$').search(word) is not None: continue
    if re.compile(r'/[0-9]{4}.').search(word) is not None: continue
    if re.compile(r'^\.').search(word) is not None: continue
    if re.compile(r',').search(word) is not None: continue
        
    print word
    
    word = word.upper()
#     word = word.replace(u'"', u'""')
#     word = word.replace(u'〜', u'~')
    """
    score = [-36000.0 ,-400 *(title.size**1.5)].max.to_i
        をちょっと変更することで、良い結果が得られました。
    naist-jdicの名詞の標準的なスコアはだいたい6000点ぐらいだったので、
        そこから16bitの符号付整数の最小値である-32768に向けてもうちょっと分布が広がるように調整してみました。
    score = [-32768.0, (6000 - 200 *(title.size**1.3))].max.to_i
        この数式だと日本語でだいたい20文字(utf-8で)ぐらいまでの名詞が 分布されるようになります。
    """
    cost = int(max(-32768, 6000 - 200*len(word)**1.3))
    word = cnvk.convert(word.replace(u'_', u' '), cnvk.Z_NUM, cnvk.Z_ALPHA, cnvk.Z_KIGO, cnvk.Z_KATA).strip()
    fout.write(u"\"%s\",,,%d,名詞,一般,*,*,*,*,*,*,*,%s\n" % (word, cost, u"Wikipedia"))
  fin.close()
  fout.close()