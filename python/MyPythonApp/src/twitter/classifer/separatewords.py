# coding: utf-8
'''
Created on 2013/11/24

@author: nahki
'''
import MeCab
import re
import normalizewords as nw

# 無視すべき単語のリスト
ignorewords = set(['the', u'of', u'to', u'and', u'a', u'in', u'is', u'it', u'の'])
igonoresymbols = set([u'-', u'/', u'#', u"'", u'_', u',', u'(', u')', u'[', u']',
                     u'~', u'!', u'|', u'♪', u'...', u'>', u'<', u':', u'!',
                      u'&', u'/', u'+', u'*', u'【', u'】', u'（', u'）', u'！', u'：', u'ー',
                      u'＿', u'？',u'%', u'「', u'」',u'～',u'.', u'{', u'}',u'"',
                      u'＜', u'＞', u'／', u'ー', u',', u'＊', u' ', u'　', u',*,',
                      u'*,*', u',*'])

class MecabTokenize:
    """url,hashtagを抽出して、全角に変換
        その後、MeCabにかけている
    """
    @staticmethod
    def tokenize(text):
        text = unicode(text)
        urls = []
        comp = re.compile(ur'(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)')
        for g in comp.findall(text):
            tmp = g[0]+g[1]
            urls.append(tmp) 
        text = re.sub(ur'(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)', '', text)
    
        # hashtag取得後 hashtagを remove 
        comp = re.compile(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?)[\s　,、\.。$]')
        hashtags1 = comp.findall(unicode(text))
        text = re.sub(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?)[\s　,、\.。$]', ' ', unicode(text))
        comp = re.compile(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?)$')
        hashtags2 = comp.findall(unicode(text))
        text = re.sub(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?)$', ' ', unicode(text))
        hashtags = hashtags1 + hashtags2
        hashtags = [nw.Transform.tf_cnvk(h.upper()) for h in hashtags]
        
        text = nw.Transform.tf_cnvk(text.strip().upper())
        
        # 10文字未満だとmecabがバグるので飛ばす
        if len(text.decode('utf-8')) < 10: return None
        # 形態素解析
        tagger = MeCab.Tagger('-Ochasen')
        node = tagger.parseToNode(text.encode('utf-8'))
        word_set = set([])
        while node:
            ns = node.surface
            feat = node.feature.split(",")
            if feat[0] == "名詞" \
                    and (feat[1] == "一般" # 接尾はどうするか
                    or feat[1] == "固有名詞" or feat[1] == "形容動詞語幹"):
                if ns not in igonoresymbols and ',' not in ns:
                    word_set.add( ns )
            elif feat[0] == "動詞":
                if ns not in igonoresymbols and ',' not in ns:
                    word_set.add( feat[6] ) # 活用形の原形のみ取得
            elif feat[0] == "形容詞":
                if ns not in igonoresymbols and ',' not in ns:
                    word_set.add( ns )
            elif feat[0] == "副詞":
                if ns not in igonoresymbols and ',' not in ns:
                    word_set.add( ns )
            elif feat[0] == "感動詞":
                if ns not in igonoresymbols and ',' not in ns:
                    word_set.add( ns )
            """
            elif feat[0] == "記号":
                word_set.add( node.surface ) # 活用形の原形のみ取得
            """
            node = node.next
        
        return list(word_set) + urls + hashtags