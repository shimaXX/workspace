# coding: utf8
#'''
#Created on 2012/10/25
#
#@author: n_shimada
#'''
from __future__ import with_statement
#
#verbs = ['article','buy','search','comment','top','new','category','cart','login','a_review','w_review','a_favorite','w_favorite','ranking','inquiry_article','order_list','customer_reg','mypage','mail_magazine_reg','entry','re_mail','mail_magazine_del','inquiry','customer_del','fes_past_movie','fes_past_plan','fes_photo','fes_puzzle','fes_matigai','fes_janken','janken_comp','fes_anniversary','fes_event','fes_yurusito','yurusito_comp','fes_shinkei','fes_bardiel']
#ColVerbs = ['a_favorite','article','buy','cart','category','comment','customer_del','customer_reg','entry','eva_movie','inquiry_article','login','mail_magazine_del','mail_magazine_reg','mypage','order_list','re_mail','realstore','search','top','w_favorite','fes_bardiel','fes_past_movie','fes_past_plan','fes_photo','fes_shinkei','fes_yurusito']
#
output = {}
badges = []
times = []
#verbs = []
#
with open('C:/HadoopPig/workspace/HadoopPig/works/output/Mining/Ci-LaboVerbPro_Kutikomi/Part-r-00000') as f:
    for line in f:
        cols = line.strip().split()
#
        if len(cols) > 1:
            time = cols[0]
            badge = cols[1]
            num = cols[2]
#
            if badge not in output:
                output[badge] = {}
                badges.append(str(badge))
            
            if time not in times:
                times.append(str(time))
            
            output[badge][time] = num
            
outfp = open('C:/Users/n_shimada/Desktop/Ci-LaboUM_kutikomi0123_pro.csv','w')
outfp.write(",".join(times)+"\n")
for rname in badges:
    nums = [str(output.get(rname, {}).get(x, 0)) for x in times]
    outfp.write(rname +","+ (",".join(nums))+"\n")
#
outfp.close()