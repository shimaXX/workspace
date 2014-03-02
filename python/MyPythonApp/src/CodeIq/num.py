# coding: utf-8
'''
Created on 2014/02/17

@author: nahki
'''

def checkio(data):
    res = []
    calc(data,res)
    print res
    if '0' in res: return 0
    else: return int(''.join(res[::-1]))
#    return calc(data,res)

def calc(data,res):
    max_x = 1
    for x in range(2,10):
        if data % x == 0 and x > max_x:
            max_x = x
    if max_x>1: res.append(str(max_x))
    tmp = int(data/max_x)

    if data == tmp:
        res.append('0')
        return 0
    elif tmp > 1:
        calc(tmp,res)
    else:
        out = ''.join(res[::-1])
        return int(out)
"""
リスト 8 : 順列の生成（再帰版）

# 順列を格納するリスト
perm = []

# 順列の生成
def make_perm(n, m = 0):
    if n == m: print perm
    else:
        for x in range(1, n + 1):
            if x in perm: continue
            perm.append(x)
            make_perm(n, m + 1)
            perm.pop()
"""


#These "asserts" using only for self-checking and not necessary for auto-testing
if __name__ == '__main__':
    assert checkio(20) == 45, "1st example"
    assert checkio(21) == 37, "2nd example"
    assert checkio(17) == 0, "3rd example"
    assert checkio(33) == 0, "4th example"
    assert checkio(5) == 5, "5th example"
