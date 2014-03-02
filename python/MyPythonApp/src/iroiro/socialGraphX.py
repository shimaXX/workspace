import math
from PIL import *
import nn
import re
import csv
import sqlite3
import os
import networkx as nx
import matplotlib.pyplot as plt


people=['buy' ,'new' ,'top' ,'cart' ,'entry' ,'login' ,'mypage' ,'search' ,'article' ,'comment' ,'inquiry' ,'ranking' ,'re_mail' ,'a_review' ,'category' ,'w_review' ,'a_favorite' ,'order_list' ,'w_favorite' ,'customer_del' ,'customer_reg' ,'inquiry_article' ,'mail_magazine_del' ,'mail_magazine_reg' ]

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
    for uid, last_veb, post_veb, cnt in csv.reader(open(csv_filename), delimiter = '\t'):
        db.execute("insert into verb values (?, ?, ?, ?)",
                   (uid, last_veb, post_veb, cnt))
        i+=1
    db.commit()


class SocialNetwork(object):
    db = None
    
    def __init__(self, db):
        self.db = db
    
    def createGraph(self):
        # get node
        myNode = self.db.execute("select distinct disverb  from (select distinct last_verb as disverb from verb UNION ALL select distinct post_verb as disverb from verb)")
        # create_node
        for row in myNode:
            g.add_node(row[0])
        
        # create edge
        c = self.db.execute("select * from verb where post_verb <> ''")
        for row in c:
            g.add_edge(row[1], row[2], weight = row[3]/3000)
            #g.add_edge(row[1], row[2], weight = 1)

        estrong = [(u,v) for (u,v,d) in g.edges(data=True) if d["weight"] > 0.001]
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
        fig.savefig ("C:/Users/n_shimada/Documents/networkxGraphGal_onlyBuy.pdf")
        plt.show()

    def close(self):
      self.db.close()