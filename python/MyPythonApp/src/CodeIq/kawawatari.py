#coding: utf-8

class SOLVE(object):
    def __init__(self,sn,gn):
        self.left = [sn,gn] # 1次元目が兵士の数、2次元目が巨人の数
        self.right = [0,0]
        
    def transport(self):
        self.print_state()
        while self.left[0]+self.left[1]!=0:
            self.left_to_right()
            self.print_state()            
            if self.left[0]+self.left[1]!=0:            
                self.right_to_left()
                self.print_state()             
    
    def left_to_right(self):
        """
                  左岸に兵士がいる場合は兵士を優先して移動させる
                  移動の組み合わせは、兵士2, 兵士1巨人1, 巨人2の順に優先度が高い
        """ 
        # 兵士を2人移動させられるかチェック
        trans_s = 2
        trans_g = 0
        if self.check_logic_left(trans_s,trans_g):
            self.left[0] -= trans_s
            self.left[1] -= trans_g
            self.right[0] += trans_s
            self.right[1] += trans_g            
            return
                        
        # 兵士と巨人を1名づつ移動させられるかチェック
        trans_s = 1
        trans_g = 1
        if self.check_logic_left(trans_s,trans_g):
            self.left[0] -= trans_s
            self.left[1] -= trans_g
            self.right[0] += trans_s
            self.right[1] += trans_g            
            return

        # 巨人を2名移動させられるかチェック
        trans_s = 0
        trans_g = 2
        if self.check_logic_left(trans_s,trans_g):
            self.left[0] -= trans_s
            self.left[1] -= trans_g
            self.right[0] += trans_s
            self.right[1] += trans_g            
            return

    def right_to_left(self):
        """
                  右岸に巨人がいる場合は巨人を優先して移動させる                  
                  移動の組み合わせは、巨人1, 兵士1, 兵士1巨人1の順に優先度が高い
        """
        # 巨人を1人移動させられるかチェック
        trans_s = 0
        trans_g = 1
        if self.check_logic_right(trans_s,trans_g):
            self.left[0] += trans_s
            self.left[1] += trans_g
            self.right[0] -= trans_s
            self.right[1] -= trans_g            
            return
            
        # 兵士を1名移動させられるかチェック
        trans_s = 1
        trans_g = 0
        if self.check_logic_right(trans_s,trans_g):
            self.left[0] += trans_s
            self.left[1] += trans_g
            self.right[0] -= trans_s
            self.right[1] -= trans_g            
            return    

        # 各1名移動させられるかチェック
        trans_s = 1
        trans_g = 1
        if self.check_logic_right(trans_s,trans_g):
            self.left[0] += trans_s
            self.left[1] += trans_g
            self.right[0] -= trans_s
            self.right[1] -= trans_g            
            return    
            
    def check_logic_left(self,sn,gn):
        if self.calculate_diff(self.left[0]-sn, self.left[1]-gn)>=0 and \
            self.calculate_diff(self.right[0]+sn,self.right[1]+gn)>=0:
            return True
        elif self.calculate_diff(self.left[0]-sn, self.left[1]-gn)>=0 and \
            (self.right[0]+sn==0 or self.right[1]+gn==0):
            return True
        elif (self.left[0]-sn==0 or self.left[1]-gn==0) and \
            self.calculate_diff(self.right[0]+sn, self.right[1]+gn)>=0:
            return True        
        else:
            return False        
            
    def check_logic_right(self,sn,gn):
        if self.calculate_diff(self.left[0]+sn, self.left[1]+gn)>=0 and \
            self.calculate_diff(self.right[0]-sn,self.right[1]-gn)>=0:
            return True
        elif self.calculate_diff(self.left[0]+sn, self.left[1]+gn)>=0 and \
            (self.right[0]-sn==0 or self.right[1]-gn==0):
            return True
        elif (self.left[0]+sn==0 or self.left[1]+gn==0) and \
            self.calculate_diff(self.right[0]-sn, self.right[1]-gn)>=0:
            return True
        else:
            return False
            
    def calculate_diff(self,sn,gn):
        return sn - gn
        
    def print_state(self):
        print 'S'*self.left[0]+'T'*self.left[1]+'/'+ \
                'S'*self.right[0]+'T'*self.right[1]

if __name__=='__main__':
    solve = SOLVE(3,3)
    solve.transport()