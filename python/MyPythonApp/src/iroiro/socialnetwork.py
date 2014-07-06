import math
from PIL import *
import nn
import re
import csv
import sqlite3
import os

people=['buy' ,'new' ,'top' ,'cart' ,'entry' ,'login' ,'mypage' ,'search' ,'article' ,'comment' ,'inquiry' ,'ranking' ,'re_mail' ,'a_review' ,'category' ,'w_review' ,'a_favorite' ,'order_list' ,'w_favorite' ,'customer_del' ,'customer_reg' ,'inquiry_article' ,'mail_magazine_del' ,'mail_magazine_reg' ]


def get_db_conn(db_filename):
    if os.path.exists(db_filename):
        os.unlink(db_filename)
    
    db = sqlite3.connect(db_filename)
    db.text_factory=str
    return db

def import_data(db, csv_filename):
    db.execute("""create table verb
       (uid  varchar(15),
        last_verb varchar(50),
        post_verb varchar(50))""")
    
    i=1
    for uid, last_veb, post_veb in csv.reader(open(csv_filename), delimiter = '\t'):
        db.execute("insert into verb values (?, ?, ?)",
                   (uid, last_veb, post_veb))
        i+=1
    db.commit()

class SocialNetwork(object):
    db = None
    
    def __init__(self, db):
        self.db = db
    
    def crosscount(self, v):
    # Convert the number list into a dictionary of person:(x,y)
      loc=dict([(people[i],(v[i*2],v[i*2+1])) for i in range(0,len(people))])
      total=0
      
      # Loop through every pair of links
      cf = self.db.execute("select * from verb where post_verb <> ''")
      cs = self.db.execute("select * from verb where post_verb <> ''")
      for i, row in enumerate(cf):
        for n_row in cs:
          # Get the locations
          for k in range(0,i):
            cs.next()
    
          (x1,y1),(x2,y2)=loc[row[1]],loc[row[2]]
          (x3,y3),(x4,y4)=loc[n_row[1]],loc[n_row[2]]
          
          den=(y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)
    
          # den==0 if the lines are parallel
          if den==0: continue
    
          # Otherwise ua and ub are the fraction of the
          # line where they cross
          ua=((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/den
          ub=((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/den
          
          # If the fraction is between 0 and 1 for both lines
          # then they cross each other
          if ua>0 and ua<1 and ub>0 and ub<1:
            total+=1
    
      for i in range(len(people)):
        for j in range(i+1,len(people)):
          # Get the locations of the two nodes
          (x1,y1),(x2,y2)=loc[people[i]],loc[people[j]]
    
          # Find the distance between them
          dist=math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
          # Penalize any nodes closer than 50 pixels
          if dist<50:
            total+=(1.0-(dist/50.0))
    
      return total
    
    
    def drawnetwork(self, sol):
      # Create the image
      img=Image.new('RGB',(700,700),(255,255,255))
      draw=ImageDraw.Draw(img)
    
      # Create the position dict
      pos=dict([(people[i],(sol[i*2],sol[i*2+1])) for i in range(0,len(people))])
    
      c = self.db.execute("select * from verb where post_verb <> ''")
      for row in c:
        draw.line((pos[row[1]],pos[row[2]]),fill=(255,0,0))
    
      for n,p in pos.items():
        draw.text(p,n,(0,0,0))
    
      img.save("C:/Users/n_shimada/socialLow09-01_09-08.gif","GIF")

    def close(self):
      self.db.close()


def readfile(filename):
  lines=[line for line in file(filename)]
  
  # First line is the column titles
  #colnames=lines[0].strip().split('\t')[1:]
  #rownames=[]
  data=[]
  for line in lines[1:]:
    p=line.strip().split('\t')

    data.append([str(x) for x in p[1:]])
  return data

domain=[(10,670)]*(len(people)*2)
