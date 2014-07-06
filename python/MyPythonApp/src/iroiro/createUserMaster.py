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
CiLaboVerbs = ['bingo','buy','buy_cancel','cart','cart:favorite','cart:item','hadapoly','login','mail:bihada','mail:labolabo','mail:member','mail_cancel','pmp_commu:best_answer','pmp_commu:best_answer_select','pmp_commu:buzz','pmp_commu:comment','pmp_commu:counter','pmp_commu:diary','pmp_commu:onayami','pmp_register_image','pmp_view:counter',
               'pmp_view:diary','pmp_view:seiza','register','register_card','register_name','view:copy','view:cp','view:detail','view:favorite','view:goods','view:guide','view:kuchikomi','view:lp','view:media','view:news','view:news_detail','view:peko','view:peko_my','view:ranking','view:register_form','view:sample','view:search_item',
               'view:search_onayami','view:search_result','view:search_seibun','view:summary','view:support','view:teiki','view:tenki_app','view:wallpaper','view:welcome']
#
output = {}
usrNames = []
#verbs = []
#
with open('C:/HadoopPig/workspace/HadoopPig/works/output/Mining/Ci-LaboVerbPro_Kutikomi/Part-r-00000') as f:
    for line in f:
        cols = line.strip().split()
#
        if len(cols) > 1:
            uid = cols[0]
            verb = cols[1]
            num = cols[2]
#
            if uid not in output:
                output[uid] = {}
                usrNames.append(str(uid))
#
            output[uid][verb] = num
#
        else:
            uid = cols[0]
#
            if uid not in output:
                output[uid] = {}
                usrNames.append(str(uid))
#
            output[uid]['buy'] = 0
#
outfp = open('C:/Users/n_shimada/Desktop/Ci-LaboUM_kutikomi_pro.csv','w')
outfp.write(",".join(CiLaboVerbs)+"\n")
for rname in usrNames:
    nums = [str(output.get(rname, {}).get(x, 0)) for x in CiLaboVerbs]
    outfp.write(rname +","+ (",".join(nums))+"\n")
#
outfp.close()