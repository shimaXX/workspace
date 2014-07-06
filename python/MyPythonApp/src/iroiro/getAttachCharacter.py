# coding: utf8
'''
Created on 2012/10/25

@author: n_shimada
'''


from __future__ import with_statement

characters = ['Rei', 'Asuka', 'Mari', 'Shinji', 'Kaoru', 'Misato', 'Eva']
#ColVerbs = ['top','comment','search','new','category','article','cart','login','buy','w_review','a_review','w_favorite','a_favorite','ranking','mypage','order_list','customer_reg','mail_reg','inquiry_article','entry','re_mail','mail_del','customer_del','inquiry']

output = {}
usrNames = []

THRESHOLD = 5   #threshold of user'attach.Average = 4

with open('C:/HadoopPig/workspace/HadoopPig/works/output/EVA/EvaCountCharacter/Part-r-00000') as f:
    for line in f:
        cols = line.strip().split()
        uid = cols[0]
        values = cols[1:]
        
        if len(values) != 0:
            
            print values
            vMax = max(values)
        else:
            vMax = None
        
        if uid not in output:
            usrNames.append(str(uid))
            
            if len(values) == 0:
                output[uid] = None
                
            else:
                for i in range(len(values)):
                    
                    if values[i] == vMax:
                        if vMax > THRESHOLD:
                            output[uid] = characters[i]
                            
                        else:
                            output[uid] = None
                            break

outfp = open("C:/Users/n_shimada/Desktop/EvaAttachCharacter.csv","w")
outfp.write(",".join(['uid','attach'])+"\n")
for rname in usrNames:
    nums = [str(output.get(rname, None))]
    outfp.write(rname +","+ (",".join(nums))+"\n")

outfp.close()
        

