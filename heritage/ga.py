from __future__ import division
"""
A genetic algorithm implementation

Created on 17/12/2011

@author: peter
"""

import os
import random
from math import *

def LOG(s):
    print s

WEIGHT_RATIO = 0.8

def apply_weights(roulette):
    """ Add 'idx' and 'weight' keys to elements in a roulette dict 
        Weights are based on 'score' keys.
        NOTE: This returns a copy of roulette. It does NOT modify roulette in-place
        For use in roulette_wheel() 
    """
    # Store the original order in 'idx' key
    for i,x in enumerate(roulette):
        x['idx'] = i
    
    # Sort by score 
    roulette = sorted(roulette, key = lambda x: -x['score'])
    
    # Set weight based on score order
    for i,x in enumerate(roulette):
        x['weight'] = WEIGHT_RATIO**(i+1)
    total = float(sum([x['weight'] for x in roulette]))
    for x in roulette:
        x['weight'] = x['weight']/total
        
    # Check results     
    if False:
        print 'len(roulette) =', len(roulette)
        print 'sum weights =', sum([x['weight'] for x in roulette])
    assert(abs(sum([x['weight'] for x in roulette]) - 1.0) < 1e-6)
    
    # Return. No particular need to sort
    return sorted(roulette, key = lambda x: -x['weight'])

def spin_roulette_wheel(roulette):
    """ Find the roulette wheel winner
        <roulette> is a list of dicts with key 'score'
        Returns an index with probability proportional to dict's 'weight'
        which is based on score. See apply_weights()
    """
    # Add 'weight' based on 'score' to each element in roulette list
    roulette = apply_weights(roulette)
    
    # Spin 
    v = random.random()
    base = 0.0
    for x in roulette:
        top = base + float(x['weight'])
        if v <= top:
            return x['idx']
        base = top
        
    raise RuntimeError('Cannot be here')

def spin_roulette_wheel_twice(roulette):
    """" Spin the roulette wheel twice and return 2 different values """
    while True:
        i1 = spin_roulette_wheel(roulette)
        i2 = spin_roulette_wheel(roulette)
        if i1 != i2:
            return (i1,i2)

def make_shuffle_list(size, max_val):
    """ Return a list of <size> unique random values in range [0,<max_val>) """
    assert(size <= max_val)
    shuffle_list = []
    while len(shuffle_list) < size:
        i = random.randrange(max_val)
        if not i in shuffle_list:
            shuffle_list.append(i)
    return shuffle_list

def cross_over(c1, c2):
    """ Swap half the elements in lists <c1> and <c2> """
    assert(len(c1) == len(c2))
    assert(len(c1) > 0)
    assert(len(c2) > 0)
    n = len(c1)

    # Find elements that are not in both lists
    d1 = sorted(c1, key = lambda x: x in c2)
    d2 = sorted(c2, key = lambda x: x in c1)
    for i1,x in enumerate(d1):
        if x in d2:
            break
    for i2,x in enumerate(d2):
        if x in d1:
            break
    m = min(i1, i2)  # number of non-shared elements

    shuffle_list = make_shuffle_list(2*(m//2), 2*(m//2))
    swaps = [(shuffle_list[i*2],shuffle_list[i*2+1]) for i in range(len(shuffle_list)//2)]

    for i,s in enumerate(swaps):
        assert(s[0] < 2* len(swaps))
        assert(s[1] < 2* len(swaps))
        d1[s[0]], d2[s[1]] = d2[s[1]], d1[s[0]] 

    return (sorted(d1), sorted(d2))

def get_eval_result(eval_func, genome):
    """ Returns a dict that shows results of running <eval_func> classfier on
        <genome> """
    score = eval_func(genome)
    result = {'genome':genome, 'score':score}
    LOG('get_eval_result => genome=%s, score=%s' % (result['genome'], result['score']))
    return result
    
def make_random_genome(genome_len, allowed_values):
    genome = set([])
    while len(genome) < genome_len:
        genome.add(random.choice(allowed_values))
    return sorted(genome)

NUM_ROUNDS = 1000
NUM_INITIAL_GENOMES = 100
NUM_ROULETTE_TRYS = 1000
# Test for convergence. Top CONVERGENCE_NUMBER scores are the same
CONVERGENCE_NUMBER = 10

def run_ga(eval_func, genome_len, allowed_values):  
    """Run GA to find genome for which eval_func(genome) give highest score.
        A genome is a list of unique integers (could be a set).
        New genomes are created by cross-over of the starting genomes
    """
    # Set random seed so that each run gives same results
    random.seed(555)

    results = []
    existing_genomes = []
    history_of_best = []

    def get_new_genomes(): 
        """Spin roulette wheel repeatedly in search of a new binary vector"""
        for j in range(NUM_ROULETTE_TRYS):
            i1,i2 = spin_roulette_wheel_twice(results)
            g1,g2 = cross_over(results[i1]['subset'], results[i2]['subset'])
            if g1 in existing_genomes: g1 = None
            if g2 in existing_genomes: g2 = None
            if g1 or g2: return g1,g2
        return None, None

    def add_genome(genome):
        if genome:
            if not genome in existing_genomes:
                r = get_eval_result(eval_func, genome)
                results.append(r)
                existing_genomes.append(genome)
                results.sort(key = lambda x: -x['score'])  

    def has_converged():            
        """Test for convergence. Top CONVERGENCE_NUMBER scores are the same"""
      
        LOG(str(['%.1f%%' % x['score'] for x in results[:CONVERGENCE_NUMBER]]))
        history_of_best.append(results[0]['score'])
        LOG('history_of_best: %s => %s' % (results[0]['score'], history_of_best[:CONVERGENCE_NUMBER]))
        history_of_best.sort(key = lambda x: -x)
        if len(history_of_best) >= convergence_number:
            LOG('history_of_best = %s' % history_of_best[:CONVERGENCE_NUMBER])
        converged = True
        for i in range(1, CONVERGENCE_NUMBER):
            if history_of_best[i] != history_of_best[0]:
                converged = False
                break
        return converged
  
    def make_initial_genomes(genome_len, allowed_values):
        while len(existing_genomes) < NUM_INITIAL_GENOMES:
            add_genome(make_random_genome(genome_len, allowed_values))
    
    make_initial_genomes(genome_len, allowed_values)
    for cnt in range(NUM_ROUNDS):
        g1,g2 = get_new_genomes()
        if not (g1 or g2):
            print '1. Converged after %d GA rounds. No more untested genomes' % cnt
            break
        add_genome(g1)
        add_genome(g2)
        if has_converged():
            print '2. Converged after %d GA rounds. Top %d genomes have same score' % (cnt, CONVERGENCE_NUMBER)
            break

    print results
    return results

if __name__ == '__main__':
    def eval_func(chromosome):
        return sum(chromosome)
    genome_len = 5 
    allowed_values = range(100)   
    results = run_ga(eval_func, genome_len, allowed_values)
    