# coding: utf8
'''
Created on 2013/05/24

@author: n_shimada
'''
import sqlite3 as sqlite

def main():
    c_db = create_db('votefeeling.db')
    c_db.add_data()


class create_db(object):
    def __init__(self, db):
        self.con = sqlite.connect(db)
        
    def __del__(self):
        self.con.close()
        
    def db_commit(self):
        self.con.commit()

    def add_data(self):
        # 画像urlが記載されているファイルを読んでDBに登録する
        itr = 1
        with open('image_url.txt', 'r') as f:            
            for imname_raw in f:
                imname = imname_raw.strip()
                self.con.execute("insert into Votes_vote(id,image_fname,vote_hand,vote_tip,total_vote,hand_flag) \
                    values (?,?,?,?,?,?)", (itr,imname,0,0,0,0))
                self.db_commit()
                itr += 1

if __name__ == '__main__':
    main()