# coding: utf-8

import random
from deap import base, creator, tools, algorithms
import numpy as np

class RoutOptimizer:
    def __init__(self,data,black_list,student_number,impartial_class_number,weights=1.0,cost=1000):
        self.data = data
        self.n_student = student_number
        self.black_list = black_list
        self.avg_student_number = int(student_number/impartial_class_number)
        self.n_class = self.avg_student_number+1 if student_number % impartial_class_number !=0 \
                        else self.avg_student_number
        self.weights = weights
        self.cost = cost
        
        self.select_list = np.array([np.random.randint(0,self.n_class) for _ in xrange(student_number)])
        self.regist_toolbox()

    def regist_toolbox(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,)) #weights=(self.weights,)
        creator.create("Individual", list, fitness=creator.FitnessMax)
        
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_bool", random.randint, 0, self.n_class-1) # define random integer range
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_bool, n=self.n_student)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self.eval_cost_min)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.10)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def eval_cost_min(self, individual):
        individual = np.array(individual,dtype=np.int32)
        #print "individual", individual
        cost = self.label_constraint_cost(individual)
        cost += self.combination_constraint_cost(individual)
        cost += self.test_constraint_cost(individual)
        return (float(-cost), )

    def label_constraint_cost(self,individual):
        cost = 0
        for label in xrange(self.n_class):
            class_s_number = len(individual[individual==label])
            diff = abs(self.avg_student_number - class_s_number)
            cost += 0 if diff<=1 else diff  
        return cost*self.cost*10

    def combination_constraint_cost(self,individual):
        cost = 0
        for label in xrange(self.n_class):
            class_list = individual[individual==label]
            for b_list in self.black_list:
                if b_list[0] in class_list and b_list[0] in class_list:
                    cost +=1 
        return cost*self.cost

    def test_constraint_cost(self,individual):
        sum_test = []
        for label in xrange(self.n_class):
            student_idx = np.where(individual==label)[0]
            sum_test.append( np.sum( self.data[student_idx,1:] ) )
        return ( max(sum_test) - min(sum_test) )*self.cost/10

    def get_label(self, selected_label,label):
        return selected_label[label]

    def main(self,population_number,halloffame,cxpb=0.5,mutpb=0.3,ngen=500):
        pop = self.toolbox.population(n=population_number)
        hof = tools.HallOfFame(halloffame)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)
        
        pop, logbook = algorithms.eaSimple(pop, self.toolbox, cxpb=cxpb, mutpb=mutpb, ngen=ngen, stats=stats, halloffame=hof, verbose=True)
        
        return pop, logbook, hof

if __name__ == "__main__":
    """
    cost_list = '100,7,12,8,11,7,3,100,10,7,13,2,4,8,100,9,12,3,6,6,9,100,10,7,7,7,11, \
                10,100,5,9,7,8,9,10,100'.split(',')
    rout_list = '1→1,1→2,1→3,1→4,1→5,1→6,2→1,2→2,2→3,2→4,2→5,2→6,3→1,3→2,3→3,3→4,3→5,3→6, \
                    4→1,4→2,4→3,4→4,4→5,4→6,5→1,5→2,5→3,5→4,5→5,5→6,6→1,6→2,6→3,6→4,6→5,6→6'.split(',')   
    rout_list = np.array(rout_list)
    
    n_path = 6
    """
    np.random.seed(555)
    
    subject_number = 5
    student_number = 183
    impartial_class_number = 40
    black_list = ((1,3),(1,4),(1,5),)
    data = np.array([[i]+[np.random.randint(1,100) for _ in xrange(subject_number) ] for i in xrange(student_number)]
                    ,dtype=np.float64)
    for i in xrange(1,len(data[0,:])):
        data[:,i] = np.float64( data[:,i]-np.mean(data[:,i]) )/np.std(data[:,i])
    
    ro = RoutOptimizer(data,black_list,student_number,impartial_class_number,weights=5.0,cost=100)
    
    population_number = 300
    halloffame = 1
    cost = -10000
    #while cost<-1000: # repeat in case of not fulfilling constraints. 
    pop, log, hof = ro.main(population_number,halloffame,ngen=500)
    print("Best individual is: %s\nwith fitness: %s" % (hof[0], hof[0].fitness))
    print "\ncost is", hof[0].fitness.values[0]*-1
    cost = hof[0].fitness.values[0]