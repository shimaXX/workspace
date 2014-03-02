# coding: utf-8 

from __future__ import with_statement
from numpy import *
import re

# define constant
NUM_OF_EXTRACT_ELEMENTS = 27
NUM_OF_SHOW_ARTICLES = 1
NUM_OF_SHOW_PATTERNS = 3

def get_input_data(input_filename):
    #create count list of words
    verbs = ['a_favorite','article','buy','cart','category','comment','customer_del','customer_reg','entry','eva_movie','inquiry_article','login','mail_magazine_del','mail_magazine_reg','mypage','order_list','re_mail','realstore','search','top','w_favorite','fes_bardiel','fes_past_movie','fes_past_plan','fes_photo','fes_shinkei','fes_yurusito']
    
    allverbs = {}
    output = {}
    usr_names = []

    with open(input_filename) as f:
        for line in f:
            cols = line.strip().split()
            
            uid = cols[0]
            verb = cols[1]
            num = cols[2]
                            
            if uid not in output:
                output[uid] = {}
                usr_names.append(str(uid))            
            
            if verb not in allverbs:
                allverbs.setdefault(verb,0)     
            output[uid][verb] = num
            allverbs[verb] += int(num)  
    
    #create action matrix
    l1=[[(verb in output[uid] and double(output[uid][verb]) or 0.0) for verb in verbs] for uid in usr_names]
    return allverbs, output, l1, verbs, usr_names

def showfeatures(w,h,titles,wordvec,out='C:/Users/n_shimada/Desktop/features.txt'): 
    outfile=file(out,'w')  
    pc,wc=shape(h)
    toppatterns=[[] for i in range(len(titles))]
    patternnames=[]
  
    # Loop over all the features
    for i in range(pc):
        slist=[]
        # Create a list of words and their weights
        for j in range(wc):
            slist.append((h[i,j],wordvec[j]))
        # Reverse sort the word list
        slist.sort()
        slist.reverse()
        
        # Print the first six elements
        n=[s[1] for s in slist[0:int(NUM_OF_EXTRACT_ELEMENTS)]]
        outfile.write(str(n)+'\n')
        patternnames.append(n)
    
        # Create a list of articles for this feature
        flist=[]
        for j in range(len(titles)):
            # Add the article with its weight
            flist.append((w[j,i],titles[j]))
            toppatterns[j].append((w[j,i],i,titles[j]))
    
        # Reverse sort the list
        flist.sort()
        flist.reverse()
    
        # Show the top 3 articles
        for f in flist[0:int(NUM_OF_SHOW_ARTICLES)]:
            outfile.write(str(f)+'\n')
        outfile.write('\n')

    outfile.close()
    # Return the pattern names for later use
    return toppatterns,patternnames

def showarticles(titles,toppatterns,patternnames,out='C:/Users/n_shimada/Desktop/article.txt'):
    outfile=file(out,'w')  
    
    # Loop over all the articles
    for j in range(len(titles)):
        outfile.write(titles[j].encode('utf8')+'\n')
        
        # Get the top features for this article and
        # reverse sort them
        toppatterns[j].sort()
        toppatterns[j].reverse()
        
        # Print the top three patterns
        for i in range(int(NUM_OF_SHOW_PATTERNS)):
            outfile.write(str(toppatterns[j][i][0])+' '+
                    str(patternnames[toppatterns[j][i][1]])+'\n')
        outfile.write('\n')
    
    outfile.close()