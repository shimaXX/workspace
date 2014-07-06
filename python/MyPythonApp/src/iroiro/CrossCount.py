'''
Created on 2012/10/23

@author: n_shimada
'''
import math
from PIL import *
import nn
import re
import csv
import sqlite3
import os
import networkx as nx
import matplotlib.pyplot as plt


verbs=['buy' ,'new' ,'top' ,'cart' ,'entry' ,'login' ,'mypage' ,'search' ,'article' ,'comment' ,'inquiry' ,'ranking' ,'re_mail' ,'a_review' ,'category' ,'w_review' ,'a_favorite' ,'order_list' ,'w_favorite' ,'customer_del' ,'customer_reg' ,'inquiry_article' ,'mail_magazine_del' ,'mail_magazine_reg' ]

# Create Directed Graph
g = nx.DiGraph()

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
        post_verb varchar(50),
        cnt int)""")
    
    i=1
    for uid, verb, cnt, cnt in csv.reader(open(csv_filename), delimiter = '\t'):
        db.execute("insert into count_verb values (?, ?, ?)",
                   (uid, verb, cnt))
        i+=1
    db.commit()

def create_db(crossDB_filename):
    if os.path.exists(crossDB_filename):
        os.unlink(crossDB_filename)
        
    crossDB = sqlite3.connect(crossDB_filename)
    crossDB.text_factory=str
    
    crossDB.execute("""create table CrossCount
       (buy integer ,new integer ,top integer ,cart integer ,entry integer ,login integer ,mypage integer ,
        search integer ,article integer ,comment integer ,inquiry integer ,ranking integer ,re_mail integer ,a_review integer ,
        category integer ,w_review integer ,a_favorite integer ,order_list integer ,w_favorite integer ,customer_del integer ,
        customer_reg integer ,inquiry_article integer ,mail_magazine_del integer ,
        mail_magazine_reg integer)""")
    crossDB.comit()
    
    return crossDB

class SocialNetwork(object):
    db = None
    
    def __init__(self, db, crossDB):
        self.db = db
        self.crossDB = crossDB
    
    def __del__(self, db):
        self.db.close()
        self.crossDB.close()
    
    def createGraph(self):
                
        #get dbData
        c = self.db.excute("select * from count_verb")
        
        
        for  row in c:
            for i in range(0, len(verbs)):
                if row[1] == verbs[i]:
                    self.crossDB.execute("insert into CrossCount values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                         (buy ,new ,top ,cart ,entry ,login ,mypage ,search ,article ,comment ,inquiry ,ranking ,re_mail ,a_review ,category ,w_review ,a_favorite ,order_list ,w_favorite ,customer_del ,customer_reg ,inquiry_article ,mail_magazine_del ,mail_magazine_reg ))
                    

                                    
                
                
        # create edge
        c = self.db.execute("select * from verb where post_verb <> ''")
        for row in c:
            g.add_edge(row[1], row[2], weight = row[3])
            #g.add_edge(row[1], row[2], weight = 1)

        estrong = [(u,v) for (u,v,d) in g.edges(data=True) if d["weight"] > 1]
        pos=nx.spring_layout(g) # positions for all nodes

        # nodes
        nx.draw_networkx_nodes(g,pos,node_size=500)
        
        # edges
        nx.draw_networkx_edges(g,pos,edgelist=estrong,width=2)
        #nx.draw_networkx_edges(g,pos,edgelist=esmall,width=6,alpha=0.5,edge_color='b',style='dashed')
        
        # labels
        nx.draw_networkx_labels(g,pos,font_size=15,font_family='sans-serif')

        fig=plt.figure(figsize =(10 ,10))
        nx.draw(g)
        plt.axis("tight")
        fig.savefig ("C:/Users/n_shimada/Documents/networkxGraphMonth8.pdf")
        plt.show()

    def close(self):
      self.db.close()