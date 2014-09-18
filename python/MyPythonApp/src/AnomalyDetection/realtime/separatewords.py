# coding: utf-8
'''
Created on 2013/11/24

@author: nahki
'''
import MeCab
import re
import normalizewords as nw

# news排除リスト
news_list = (u'News',u'iNews',u'Safety')
reject_words = (u'対岸の火事',u'上は大火事',u'地震・雷・火事',u'地震、雷、火事',u'テレビアニメのコナン',
                u'http://t.co/2fpGmA1nUP',u'心理テスト',u'夢診断',u'地震雷火事',u'村八分',u'上は洪水'
                u'夢占い',u'惚れさせ197',u'逆転優勝した富山第一',u'上は大水',u'雑学',u'回文',u'異常気象',
                u'地震',u'火事wwシュールすぎる',u'まっち一本火事の',u'火事とけんか',u'火事と喧嘩')

# 無視すべき単語のリスト
ignorewords = set(['the', u'of', u'to', u'and', u'a', u'in', u'is', u'it', u'の'])
igonoresymbols = set(['-', '/', '#', "'", '_', ',', '(', ')', '[', ']',
                     '~', '!', '|', '♪', '...', '>', '<', ':', '!',
                      '&', '/', '+', '*', '【', '】', '（', '）', '！', '：', 'ー',
                      '＿', '？','%', '「', '」','～','.', '{', '}','"',
                      '＜', '＞', '／', '－','―', ',', '＊', ' ', '　', ',*,',
                      '*,*', ',*', '笑', ' ', '　', '\\', '￥', 
                      'Ａ','Ｂ','Ｃ','Ｄ','Ｅ','Ｆ','Ｇ','Ｈ','Ｉ','Ｊ','Ｋ','Ｌ','Ｍ','Ｎ',
                      'Ｏ','Ｐ','Ｑ','Ｒ','Ｓ','Ｔ','Ｕ','Ｖ','Ｗ','Ｘ','Ｙ','Ｚ'])

hira = re.compile(ur'^[あ-ん]*$')
kata = re.compile(ur'^[ァ-ン]*$')
kanj = re.compile(ur'^[一-龠]*$')
kigo = re.compile(ur'^[\w-]*$')

class MecabTokenize:
    """url,hashtagを抽出して、全角に変換
        その後、MeCabにかけている
    """
    @staticmethod
    def tokenize(text):
        text = unicode(text)
        for reject_word in reject_words:
            if reject_word in text: return None

        urls = []
        comp = re.compile(ur'(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)')
        for g in comp.findall(text):
            tmp = g[0]+g[1]
            urls.append(tmp) 
        # remove URL
        text = re.sub(r'(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)', 'ＵＲＬＵＲＬＵＲＬ', text)
        
        # mention
        mentions = []
        comp = re.compile(ur'@(.*?)[\s:]')        
        mention = comp.findall( unicode(text) )
        text = re.sub(ur'@(.*?)[\s:]', ' ', unicode(text))
        for s in mention:
            for news_str in news_list:
                if re.sub(ur'@','',news_str) in s: return None
            mentions.append(nw.Transform.tf_cnvk(s.upper()))

        # hashtag取得後 hashtagを remove 
        comp = re.compile(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?#＃)[\s　,、\.。$]')
        hashtags1 = comp.findall(unicode(text))
        text = re.sub(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?#＃)[\s　,、\.。$]', ' ', unicode(text))
        comp = re.compile(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?#＃)$')
        hashtags2 = comp.findall(unicode(text))
        text = re.sub(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?#＃)$', ' ', unicode(text))
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
                if ns not in igonoresymbols and ',' not in ns and ' ' not in ns:
                    try:
                        if len(unicode(str(ns)))==1 and \
                            (hira.search(unicode(str(ns)))!=None or \
                             kata.search(unicode(str(ns)))!=None or kigo.search(unicode(str(ns)))):
                            pass
                        else:
                            word_set.add( ns )
                    except:
                        pass                    
            """
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
            """
            elif feat[0] == "記号":
                word_set.add( node.surface ) # 活用形の原形のみ取得
            """
            node = node.next
        if len(list(word_set) + urls + hashtags + mentions)==0: return None
        return list(word_set) + urls + hashtags + mentions, urls


        """ urlがある場合のみ取得
        trainingこれじゃない 
        """
        """
        if len(urls)==0: return None
        else:
            cnt = 0
            for u in urls:
                re.search(ur'', unicode(u))
                if ur'http://t.co/' in unicode(u):
                    cnt += 1
            if cnt > 0:
                return list(word_set) + urls + hashtags + mentions
            else:
                return None
        """
