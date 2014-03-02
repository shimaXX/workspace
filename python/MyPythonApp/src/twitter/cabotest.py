# coding: utf-8
'''
Created on 2014/02/12

@author: nahki
'''

"""CaboCha"""
'http://needtec.exblog.jp/20555221/'
"""MeCab"""
'http://seesaawiki.jp/spz/d/Windows%A4%CBmecab-python%A4%F2%C6%B3%C6%FE'

#import MeCab
import CaboCha

#c = CaboCha.Parser("-n2")
c = CaboCha.Parser()

sentence = "武志が聖人に借りた本は面白い"

print c.parseToString(sentence)

#tree =  c.parse(sentence)
#
tree =  c.parse(sentence)
print tree.toString(CaboCha.FORMAT_TREE)
print tree.toString(CaboCha.FORMAT_LATTICE)
print tree.toString(CaboCha.FORMAT_XML)
"""
for i in range(tree.chunk_size()):
    chunk = tree.chunk(i)
    print 'Chunk:', i
    print ' Score:', chunk.score
    print ' Link:', chunk.link
    print ' Size:', chunk.token_size
    print ' Pos:', chunk.token_pos
    print ' Head:', chunk.head_pos # 主辞
    print ' Func:', chunk.func_pos # 機能語
    print ' Features:',
    for j in range(chunk.feature_list_size):
        print '  ' + chunk.feature_list(j) 
    print
    print 'Text' 
    for ix  in range(chunk.token_pos,chunk.token_pos + chunk.token_size):
        print ' ', tree.token(ix).surface 
    print

for i in range(tree.token_size()):
    token = tree.token(i)
    print 'Surface:', token.surface
    print ' Normalized:', token.normalized_surface
    print ' Feature:', token.feature
    print ' NE:', token.ne # 固有表現
    print ' Info:', token.additional_info
    print ' Chunk:', token.chunk
"""