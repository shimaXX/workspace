# coding: utf-8

import CaboCha
import xml.etree.ElementTree as ET
from collections import defaultdict

def get_reputation(ET_tree):
    flag = None
    reputation = defaultdict(str)

    for el in ET_tree.findall(".//chunk"):        
        tok = el.find("tok")
        feature = tok.attrib["feature"].strip().split(',')
        part = feature[0]
        typ = feature[1]

        if part=='名詞' and \
            (typ=='一般' or typ=='固有名詞'): 
                reputation["object"]=tok.text
        if part=='形容詞': reputation['adjective']=feature[6]
        link = el.attrib["link"]
        if link=='-1': break
        while 1:
            res = get_next_chunk(link,part)
            if res==None: break
            part, typ, word, link = res

            if part=='名詞' and \
                (typ=='一般' or typ=='固有名詞'): 
                reputation["object"]=word
            if part=='形容詞':
                reputation['adjective'] = word
                if reputation["object"]!=None:
                    flag=1
                    break
        if flag==1: break
        
    print reputation["object"]
    print reputation["adjective"]

def get_next_chunk(linkid, ex_part):
    if linkid=='-1': return None
    this_chunk =  ET_tree.find(".//chunk[@id='%s']" % linkid)
    #print this_chunk.attrib
    link = this_chunk.attrib["link"]
        
    tok = this_chunk.find('tok')
    feature = tok.attrib["feature"].strip().split(',')
    if ex_part=='名詞':
        if feature[0]=='名詞':
            return feature[0], feature[1], tok.text, link
        elif feature[0]=='動詞' or feature[0]=='形容詞':
            return feature[0], feature[1],  feature[6], link
    elif ex_part=='動詞':
        if feature[0]=='名詞':
            return feature[0], feature[1],  tok.text, link
    elif ex_part=='形容詞':
        if feature[0]=='名詞':
            return feature[0], feature[1],  tok.text, link
        
if __name__=='__main__':
    c = CaboCha.Parser('--charset=UTF8')
    
    sentence = "クーリエの６月号「楽しく学ぶ『教養』入門」で一番おもしろかったのは、池上英洋さんの記事。「絵画の見かた」って超絶大事だよね。"
    
    tree =  c.parse(sentence)
    #print tree.toString(CaboCha.FORMAT_TREE)
    #print tree.toString(CaboCha.FORMAT_LATTICE)
    print tree.toString(CaboCha.FORMAT_XML)
    ET_tree = ET.fromstring(tree.toString(CaboCha.FORMAT_XML))
    
    get_reputation(ET_tree)