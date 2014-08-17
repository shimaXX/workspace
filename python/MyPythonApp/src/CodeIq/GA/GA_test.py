# coding: utf-8

import random
from deap import base, creator, tools, algorithms
import numpy as np

class RoutOptimizer:
    def __init__(self,cost_list,rout_list,n_path,weights=1.0,cost=1000):
        self.cost_list = np.array(cost_list,np.int32)
        self.n_path = n_path
        self.weights = weights
        self.cost = cost
        
        self.select_list = np.array([j for j in xrange(n_path) for _ in xrange(n_path)])
        self.transform_list = np.array(range(n_path)*n_path)
        self.regist_toolbox()

    def regist_toolbox(self):
        creator.create("FitnessMax", base.Fitness, weights=(self.weights,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_bool", random.randint, 0, 1)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_bool, n=self.n_path**2)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self.eval_cost_min)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.10)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def eval_cost_min(self, individual):
        individual = np.array(individual,dtype=np.int32)
        cost = sum(individual*self.cost_list)
        cost += abs( self.n_path-sum(individual) )*self.cost
        selected_label = self.select_list[individual==1]
        cost += self.label_constraint_cost(selected_label)
        t_label = self.transform_list[individual==1]
        cost += self.label_constraint_cost(t_label)
        try:
            cost += self.rout_constraint_cost(t_label)
        except:
            pass
        return (float(-cost), )

    def label_constraint_cost(self, selected_label):
        cost = 0
        for label in selected_label:
            cost += sum( (selected_label==label)*1 ) - 1
        return cost*self.cost

    def rout_constraint_cost(self, t_label):
        cost = 0
        label = 0
        for i in xrange(len(t_label)):
            label = self.get_label(t_label,label)
            if i<5 and label==0:
                cost = self.cost
                return cost
        return cost

    def get_label(self, selected_label,label):
        return selected_label[label]

    def main(self,population_number,halloffame,cxpb=0.5,mutpb=0.2,ngen=500):
        pop = self.toolbox.population(n=population_number)
        hof = tools.HallOfFame(halloffame)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)
        
        pop, logbook = algorithms.eaSimple(pop, self.toolbox, cxpb=cxpb, mutpb=mutpb, ngen=ngen, stats=stats, halloffame=hof, verbose=True)
        
        return pop, logbook, hof

if __name__ == "__main__":
    cost_list = '100,7,12,8,11,7,3,100,10,7,13,2,4,8,100,9,12,3,6,6,9,100,10,7,7,7,11, \
                10,100,5,9,7,8,9,10,100'.split(',')
    n_path = 6
    rout_list = [str(i+1)+' -> '+str(j+1) for i in xrange(n_path) for j in xrange(n_path)]
    rout_list = np.array(rout_list)
    
    ro = RoutOptimizer(cost_list,rout_list,n_path,weights=1.0,cost=1000)
    
    population_number = 50
    halloffame = 1
    cost = -10000
    while cost<-1000: # repeat in case of not fulfilling constraints. 
        pop, log, hof = ro.main(population_number,halloffame,ngen=500)
        #print("Best individual is: %s\nwith fitness: %s" % (hof[0], hof[0].fitness))
        print "\ncost is", hof[0].fitness.values[0]*-1
        cost = hof[0].fitness.values[0]
    rout = rout_list[np.array(hof[0])==1]
    
    print "\nrout"
    for r in rout:
        print r