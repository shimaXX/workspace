# coding: utf-8
'''
Created on 2014/02/18

@author: nahki
'''

import unicodedata
import re
import cnvk

class Transform:
    """ KHcoder用に記号や英数字も全角に変換
    cnvkモジュールで変換
    """
    @staticmethod
    def tf_cnvk(text):
        # 半角を全角に統一（khcoderに投入するため）
        return cnvk.convert(text, cnvk.Z_NUM, cnvk.Z_ALPHA, cnvk.Z_KIGO, cnvk.Z_KATA) #KATA2HIRA
    
    @staticmethod
    def tf_unicodenorm(text):
        """ 日本語半角を全角に変換+英数字,記号は半角
        """
#         tmp = text.split(' ')
#         text = ''.join(tmp)
        return unicodedata.normalize('NFKC', text)
    
class Replace:
    @staticmethod
    def str_replace(string):
        # html特殊文字の変換
#        string = re.sub('&.+;', ' ', string) # これにすると空白がない場合は真ん中の文字も全て消える
        string = re.sub('&amp;', '&', string)
        string = re.sub('&lt;', '<', string)
        string = re.sub('&gt;', '>', string)

        """
        # remove URL
        string = re.sub(r'(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)', 'URL', string)
        """

        # remove quote
#        string = re.sub('"', ' ', string)
#        string = re.sub("'", ' ', string)

        # remove mention
        string = re.sub(r'@(.*?)[\s:]', 'Mention ', string)
        
        """
        # remove hashtag
        string = re.sub(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?)[\s　,、\.。$]', 'Hashtag ', string)
        string = re.sub(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?)$', 'Hashtag ', string)
        """

        # remove retweet
        string = re.sub(r'RT', 'Retweet', string)
        
        ## 同じ文字が3つ以上連続している場合、2つに短縮
        # 漢字 :[一-龠], カタカナ:[ァ-ヾ][ァ-ヴ], ひらがな:[ぁ-ゞ][ぁ-ん], 半角カタカナ:[ｦ-ﾝ]   ｱﾞｱﾞｱﾞｱﾞｱﾞ
        string = re.sub(ur'([一-龠ぁ-んァ-ヴｦ-ﾝ／ー～!！？\?;；:：a-zA-ZWｗ\s　])\1{2,}', ur'\1'*2, string)
        
        # 空白が2つ以上連続している場合は1つにする
        string = re.sub(ur'([\s　])\1+', ur'\1', string)

        # ．。、,・の3つ続くことに意味があるものは4つ以上で3つに短縮
        string = re.sub(ur'([。、．\.・])\1{3,}', ur'\1'*3, string)
        
        return string.strip()
    
    @staticmethod
    def hash_replace(string):
        # remove hashtag
        string = re.sub(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?)[\s　,、\.。$]', 'Hashtag ', string)
        string = re.sub(ur'[＃#]([.a-zA-Z0-9一-龠ぁ-んァ-ヴｦ-ﾝー、。・？！\-_.!~;:；：<>＜＞\[\]]*?)$', 'Hashtag ', string)
        
        return string.strip()

    @staticmethod
    def url_replace(string):
        """ remove URL """
        string = re.sub(r'(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)', 'URL', string)
        return string.strip()