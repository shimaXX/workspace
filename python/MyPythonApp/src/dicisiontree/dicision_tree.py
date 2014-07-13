# coding: utf-8

from collections import defaultdict
from math import log
import numpy as np

from dicision_node import DicisionNode

class DicisionTree:
    """rf化するときはL36あたりをイジる"""
    def __init__(self):
        self.dicision_node = DicisionNode
        self.width = 0

    def train(self, rows, scorefunc=None, mingain=0.1, \
                prune=True, gain_limit=0, limit_width=1e4):
        self.n_rows = len(rows)
        self.gain_limit = gain_limit
        self.limit_width = limit_width
        self.set_lower_bound_of_rows_in_set(rows[0][-1])
        
        # set score function
        if self.is_continuous_volume(rows[0][-1]):
            self.scorefunc = self.regression_risk
        else:
            self.scorefunc = scorefunc if scorefunc is not None else self.entropy
        
        tree = self.build_tree(rows)
        if prune==True:
            return self.prune(tree, mingain)
        else:
            return tree

    def set_lower_bound_of_rows_in_set(self, value): # stop criteria 2
        if self.is_continuous_volume(value):
            self.lower_bound_of_rows_in_set = 5
        else:
            self.lower_bound_of_rows_in_set = 1

    def is_continuous_volume(self, value):
        if isinstance(value,int) or isinstance(value,float):
            return True
        else:
            return False

    def build_tree(self, rows):
        #if self.width>=self.limit_width:return self.dicision_node() # stop criteria 3
        if len(rows)==0: return self.dicision_node()
        current_score = self.scorefunc(rows)
        
        # Set up some variables to track the best criteria
        """ rf化するときはrowsをrows[:][P_tld]としてランダムに選んだP個の変数を使用する
        _標本のサンプリングはクラスの外部で行う
        """
        best_gain, best_criteria, best_sets = \
                self.get_best_criteria(rows,current_score)

        # generate link
        if best_gain>self.gain_limit: # have the space to reduce information gain
            true_branch = self.build_tree(best_sets[0])
            false_branch = self.build_tree(best_sets[1])
            return self.dicision_node(col=best_criteria[0],value=best_criteria[1],
                                      tb=true_branch, fb=false_branch)
        else: # no space to reduce information gain
            self.width += 1
            return self.dicision_node(results=self.unique_counts(rows)) # leaf

    def get_best_criteria(self,rows,current_score):
        # Set up some variables to track the best criteria
        best_gain = 0.0
        best_criteria = None
        best_sets = None
        
        n_column = len(rows[0])-1 # except explained variable
        for col in xrange(n_column): # loop variables            
            v_column_dict = self.generate_all_value_dict(rows,col)
            for value in v_column_dict.keys():
                set1, set2 = self.divide_set(rows, col, value)
                gain = self.calculate_information_gain(rows, current_score, set1, set2)
                if gain>best_gain and len(set1)>=self.lower_bound_of_rows_in_set \
                        and len(set2)>=self.lower_bound_of_rows_in_set:
                    best_gain = gain
                    best_criteria = (col, value)
                    best_sets = (set1, set2)
        return best_gain, best_criteria, best_sets

    def calculate_information_gain(self, rows, current_score, set1, set2):
        p = float(len(set1))/len(rows)
        return current_score - p*self.scorefunc(set1) - (1-p)*self.scorefunc(set2)

    def generate_all_value_dict(self,rows,col):
        v_column_dict = defaultdict(int)
        for row in rows: # loop rows
            v_column_dict[row[col]]+=1
        return v_column_dict

    def divide_set(self, rows, column, value):
        """ Divide data sets on the basis of the column.
        Enable to process if the column is value or categorical data.
        at splitting node.
        """
        split_function = None
        if isinstance(value,int) or isinstance(value,float):
            split_function = lambda row:row[column]>=value
        else:
            split_function = lambda row:row[column]==value
        
        # Divide the rows into two sets and return them
        set1=[row for row in rows if split_function(row)] # numpy where で書き換え
        set2=[row for row in rows if not split_function(row)]
        return set1, set2

    def unique_counts(self, rows):
        """Create counts of possible results
        (the last column of each row is the result).
        at splitted node.
        """
        results = defaultdict(int)
        for row in rows: # numpy で書き換え
            # The result is the last column
            r = row[-1]
            results[r] += 1
        return results
    
    def gini_impurity(self, rows):
        """Probability that a randomly placed item will
        be in the wrong category.
        value at a node.
        at splitted node.
        """
        Nt = len(rows)
        n_of_categories = self.unique_counts(rows)
        
        imp = 0
        for category, count in n_of_categories.items():
            p_k = float(count)/Nt
            imp += p_k*(1-p_k)
        return imp
        
    def entropy(self, rows):
        """Entropy is the sum of p(x)log(p(x)) across all
        the different possible results.
        value at a node.
        at splitted node.
        """
        Nt = len(rows)
        n_of_categories = self.unique_counts(rows)

        entropy = 0
        for category, count in n_of_categories.items():
            p_k = float(count)/Nt
            entropy += p_k*log(p_k,2)
        return -entropy
    
    def error_rate(self, rows, category):
        """ Calculate error rate.
        value at a node.
        at splitted node.
        """
        Nt = len(rows)
        n_of_categories = self.unique_counts(rows)
        n_true =  n_of_categories[category]
        return float(n_true)/Nt
    
    def regression_risk(self, rows):
        regidual = np.array(rows[:][-1],dtype=np.float64)-self.mean(rows)
        return regidual/self.n_rows
        
    def mean(self, rows):
        return float(sum(rows[:][-1]))/len(rows)
    
    def prune(self, tree, mingain):
        # If the branches aren't leaves, then prune them
        if tree.tb.results is None:
            self.prune(tree.tb, mingain)
        if tree.fb.results is None:
            self.prune(tree.fb, mingain)
        
        # If both the subbranches are now leaves, see if they
        # should merged
        if tree.tb.results is not None and tree.fb.results is not None:
            # Build a combined dataset
            tb,fb=[],[]
            for v,c in tree.tb.results.items():
                tb+=[[v]]*c
            for v,c in tree.fb.results.items():
                fb+=[[v]]*c
          
            # Test the reduction in entropy
            delta = self.entropy(tb+fb)-(self.entropy(tb)+self.entropy(fb)/2)
            
            if delta<mingain:
                # Merge the branches
                tree.tb,tree.fb=None,None
                tree.results=self.unique_counts(tb+fb)
        return tree
    
    def printtree(self, tree, indent=' '):
        # Is this a leaf node?
        if tree.results!=None:
            print str(tree.results)
        else:
            # Print the criteria
            print str(tree.col)+':'+str(tree.value)+'? '
            
            # Print the branches
            print indent+'T->',
            self.printtree(tree.tb,indent+'  ')
            print indent+'F->',
            self.printtree(tree.fb,indent+'  ')

    
    
if __name__=='__main__':
    my_data=[['slashdot','USA','yes',18,'None'],
            ['google','France','yes',23,'Premium'],
            ['digg','USA','yes',24,'Basic'],
            ['kiwitobes','France','yes',23,'Basic'],
            ['google','UK','no',21,'Premium'],
            ['(direct)','New Zealand','no',12,'None'],
            ['(direct)','UK','no',21,'Basic'],
            ['google','USA','no',24,'Premium'],
            ['slashdot','France','yes',19,'None'],
            ['digg','USA','no',18,'None'],
            ['google','UK','no',18,'None'],
            ['kiwitobes','UK','no',19,'None'],
            ['digg','New Zealand','yes',12,'Basic'],
            ['slashdot','UK','no',21,'None'],
            ['google','UK','yes',18,'Basic'],
            ['kiwitobes','France','yes',19,'Basic']]

    dt = DicisionTree()
    tree = dt.train(my_data,prune=False,mingain=1,gain_limit=0.0,limit_width=2) #gain_limit=0, mingain=0.1, limit_width=1e4
    
    # print tree
    dt.printtree(tree)