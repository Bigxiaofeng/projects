#!/usr/bin/env python

### SIM_BALANCE.PY ###
#Author: Sameet Sreenivasan, August 2014
#Code to simulate the dynamics of social balance on 1d and 2d small-world graphs (networks)

#The primary function is: STOCHASTIC_SIM_BALANCE which takes the following args:
# N: int, network size
# ndims: int, The embedding dimension of the initial network; can be 1 or 2
# beta: float, probability with which a node is chosen for rewiring to create a "small-world network"
#kavg: float, The desired average degree of the graph
#T: int, the number of update steps for which balance dynamics is run. Currently set to 100*N, but can be modified under if __name__==__'main'__:
#p: float, the probability with which an external centrism influence step occurs in the model
#alpha: float, the probability with which a centrist is chosen to balance an unbalanced triad
#MAX_REP: the number of realizations of the graph generation + balance dynamics that is run
#showplot: Boolean, turns plotting on or off 

#Parameters for which the simulation needs to be run are stored in a yaml file: 'balanceParams.yaml' which assumes that N,ndims,beta,p and alpha are
#obtained from a list of values.


from __future__ import division
import networkx as nx
import collections
import itertools
import random
import numpy
import math
import yaml
import matplotlib.pyplot as plt
import time
from datetime import datetime

state = collections.defaultdict(int)
triangles = collections.defaultdict(set)
rel = collections.defaultdict(int)
all_triangles = set()

#Makes a dict that stores for each node i , 2 permutations ((i,j,k) and i,k,j)) of every triangle (3-tuple) that it is part of
def find_triangles(H): 
    for n in H:
        nbrs = H.neighbors(n)
        common = []
        for i in range(0,len(nbrs)):
            for j in range(i+1,len(nbrs)):
                if H.has_edge(nbrs[i],nbrs[j]):
                    triangles[n].add((n,nbrs[i],nbrs[j]))
                    triangles[n].add((n,nbrs[j],nbrs[i]))    
                    all_triangles.add((n,nbrs[i],nbrs[j]))
                    all_triangles.add((n,nbrs[j],nbrs[i]))
                    
#Initializes the set of unbalanced triangles
def init_unbalanced(triangles,numnodes):
    for j in range(numnodes):
        for item in triangles[j]:
            list_states = [state[xx] for xx in item]
            
            if Bness(item) == -1:
                unbalanced.add(item)
    

#Computes the balancedness of a triangle
def Bness(triple): #balanced-ness of a triangle, returns 1 for balanced, -1 for unbalanced; takes a 3-tuple as an argument
    s1 = rel[(triple[0],triple[1])]
    s2 =  rel[(triple[1],triple[2])]
    s3 =  rel[(triple[0],triple[2])]
    return s1*s2*s3


#Updates states of links attached to node that has just flipped its state, and adds newly unbalanced triples to unbalanced set 
def update_after_flip(nn,H): 
    
    nbrs = H.neighbors(nn)
    non_centrists = [x for x in nbrs if state[x] != 0]
    if state[nn] == 0:
        for x in non_centrists:
            rel[(nn,x)] = 1
            rel[(x,nn)] = 1
    else:
        for x in non_centrists:
            rel[(nn,x)] = state[x]*state[nn]
            rel[(x,nn)] = state[x]*state[nn]
    
     
    

#Primary function that does MAX_REP realizations of graph generation and T steps of balance dynamics
def stochastic_sim_balance(N,ndims,T,MAX_REP,p,alpha,beta,kavg,showplot):
    
    print "Curently running:","N="+str(N), "alpha="+str(alpha),"beta = "+str(beta), "p="+str(p), "ndims = " + str(ndims)
    random.seed(25)
    starttime = datetime.now()
    
   
    
    cc = [] #list that holds average clustering coefficient for every realization of the graph
    surv = MAX_REP #holds the fraction of MAX_REP runs that reach centrist consensus
    
    reps = 0
    avg_degree = {} #dict that holds average degree per rep
    
    while reps < MAX_REP:
        print reps
        
        #outfile = 'demographics_vs_t'+'_p'+str(p)+'_a'+str(alpha)+'_b'+str(beta)+'_'+str(ndims)+'D'+'_R'+str(reps)+'.txt'
        outfile = 'dumdum.txt'
        g = open(outfile,'w')
        
        
        ##2D (RGG) small world graph with node rewiring probability beta
        if ndims == 2:
            while True:
                while True:
                    rr = math.sqrt(kavg/(math.pi*N))
                    G = nx.random_geometric_graph(N,rr)
                    avg_degree[reps] = sum(G.degree(range(N)).values())/N
                    if nx.is_connected(G):
                        break
                   
                if beta > 0:
                    for u in range(N):
                        if G.degree(u) ==0: #If the graph has gotten disconnected in the process
                            break
                        else:
                            if random.random() < beta: #one of u's links will be rewired
                                old_nbr = random.choice(G.neighbors(u))
                                new_nbr = old_nbr
                                while new_nbr==old_nbr or (u,new_nbr) in G.edges() or new_nbr == u:
                                    new_nbr = random.randint(0,N-1)
                                G.add_edge(u,new_nbr)
                                G.remove_edge(u,old_nbr)
                if nx.is_connected(G):
                    break
                
            
        
        else:
        
        #1D (cycle) small-world graph with node rewiring probability beta:
            while True:
                z = int(math.floor(kavg/2))
                G = nx.cycle_graph(N)
                for n1 in range(N):
                    for j in range(2,z+1):
                        #edges to the right
                        n2 = numpy.mod(n1+j,N)
                        G.add_edge(n1,n2)
                    
            
                #choose nodes and rewire one of their links with prob beta
                if beta > 0:
                    for u in range(N):
                        if random.random() < beta: #one of u's links will be rewired
                            old_nbr = random.choice(G.neighbors(u))
                            new_nbr = old_nbr
                            while new_nbr==old_nbr or (u,new_nbr) in G.edges() or new_nbr == u:
                                new_nbr = random.randint(0,N-1)
                            G.add_edge(u,new_nbr)
                            G.remove_edge(u,old_nbr)
                if nx.is_connected(G):
                    break
                
                
        #compute average degree of this graph realization
        avg_degree[reps] = sum(G.degree(range(N)).values())/N
        print "Graph construction done"
        
        #store the clustering coefficient of this graph realization
        cc.append(nx.average_clustering(G))
        
    
        #INITIALIZE THINGS FOR THE BALANCING DYNAMICS
    
        #initialize node states (-1: leftist, 0: centrist, 1: rightist)
        for i in range(N):
            state[i] = random.randint(-1,1)
            
        find_triangles(G)
    
    
        #initial link (relationship) states (-1: negative, 1: positive)
        for e in G.edges():
            if state[e[0]]*state[e[1]] == 0:
                rel[(e[0],e[1])] = 1
                rel[(e[1],e[0])] = 1
            else:
                rel[(e[0],e[1])] = state[e[0]]*state[e[1]]
                rel[(e[1],e[0])] = state[e[0]]*state[e[1]]
    
    
        # Run update dynamics
        #list storing numbers of centrists,leftists for plotting
        nc=[]
        nl=[]
        
        t = 0
        #Record state at t = 0
        num_centrists = len([x for x in G.nodes() if state[x]==0 ])
        num_leftists = len([x for x in G.nodes() if state[x]==-1 ])
        num_rightists  = N - (num_centrists + num_leftists)
        
        nc.append(num_centrists/N)
        nl.append(num_leftists/N)
        
        g.write(str(t)+'\t'+str(num_centrists)+'\t'+str(num_leftists)+'\n')
        
        
        while t <= T:
            t += 1
        
            
            #Updates
            r_node = None #if any node state update occurs, this variable stores the index of updated node
            if random.random()<p:
                r_node = random.randint(0,N-1)
                state[r_node] = 0
            else:
                #Pick random unbalanced triangle
                chosen_tr = random.sample(all_triangles,1)[0]
                bb = Bness(chosen_tr) #balanced-ness of triangle
                
                if bb == -1: #if triangle is unbalanced    
                    # Get indices of leftist, rightist and centrist in the triangle
                    l = [x for x in chosen_tr if state[x]==-1][0]
                    r = [x for x in chosen_tr if state[x]==1][0]
                    c = [x for x in chosen_tr if state[x]==0][0]
                    
                
                    # Update node state according to balancing rules
                    if random.random() < alpha:
                        state[c] = random.choice([-1,1])
                        r_node = c
                    else:
                        r_node = random.choice([l,r])
                        state[r_node] =0
                
           
            #Update link states and unbalanced triad list, if a node state was updated
            if r_node is not None:
                update_after_flip(r_node,G)
        
        
            #count numbers of different node kinds
            num_centrists = len([x for x in G.nodes() if state[x]==0 ])
            num_leftists = len([x for x in G.nodes() if state[x]==-1 ])
            num_rightists  = N - (num_centrists + num_leftists)
            
            
            nc.append(num_centrists/N)
            nl.append(num_leftists/N)
            
            #get demographics
            if num_centrists == N: #implies centrist consensus is reached
                surv -= 1
                break
           
            #print t
            g.write(str(t)+'\t'+str(num_centrists)+'\t'+str(num_leftists)+'\n')
            
            
        
        tt = range(t+1)
        #print len(tt),len(nc)
        plt.plot(tt,nc,'r-',tt,nl,'g-')
        plt.xlabel('time')
        plt.ylabel('population fraction')
        plt.legend(['fraction of centrists','fraction of leftists'],loc='center right')
        
        state.clear()
        rel.clear()
        triangles.clear()
        all_triangles.clear()
       
        
        g.close()
        reps += 1
    plt.ylim((0,1))
    
    #See if plot is requested
    if showplot:
        plt.show()
    
    
    #Write output files
    outfile = 'clusteringcoeff_N'+str(N)+'_p'+str(p)+'_a'+str(alpha)+'_b'+str(beta)+'_'+str(ndims)+'D.txt'
    q = open(outfile,'w')
    for rr in range(len(cc)):
        q.write(str(rr)+'\t'+str(cc[rr])+'\n')
    q.close()
    
    
    outfile = 'avg_degrees_N'+str(N)+'_p'+str(p)+'_a'+str(alpha)+'_b'+str(beta)+'_'+str(ndims)+'D.txt'
    q = open(outfile,'w')
    for rr in avg_degree:
        q.write(str(rr)+'\t'+str(avg_degree[rr])+'\n')
    q.close()
    
    outfile = 'survprob_N'+str(N)+'_p'+str(p)+'_a'+str(alpha)+'_b'+str(beta)+'_'+str(ndims)+'D.txt'
    q = open(outfile,'w')
    q.write(str(surv/MAX_REP))
    q.close()
    
    #print how long the simulation took
    print 'Time for execution:',(datetime.now()-starttime)
    
if __name__ == '__main__':
    with open('balanceParams.yaml','r') as f:
        params = yaml.load(f)
        
    MAX_REP = params['MAX_REP']
    kavg = params['k_avg']
    splot=params['Plotting']
    timesteps = params['timesteps']
    for dim in params['ndims']:
        ndims = dim
        for n in params['Nvals']:
            N = n
            T = timesteps*N
            for pval in params['Pvals']:
                p = pval
                for b in params['Bvals']:
                    beta = b
                    for a in params['Avals']:
                        alpha = a
                            
                            
                        stochastic_sim_balance(N,ndims,T,MAX_REP,p,alpha,beta,kavg,splot)
    