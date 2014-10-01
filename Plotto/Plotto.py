#!/usr/bin/env python
#Sameet Sreenivasan Aug 2014

import numpy
import networkx as nx
import os
import time
import json
import sys
import random
import pickle
from easygui import *
import sys

inv_root_ind = pickle.load(open("index_to_keyword.pkl","rb")) # Read in a dict that maps indices to keywords
occ = pickle.load(open("root_occurrence_prob.pkl","rb")) #Read in occurrence probability in imdb data for the root-keywords of the distinct keyword trees
part = pickle.load(open("keyword_network_partition.pkl","rb")) #Read in dict of lists which stores the partition of the nodes of the network into communities
G = nx.read_gpickle("root_keyword_network.gpickle") #Read in the networkx graph object storing the network between root-keywords


#REMOVE INDEPENDENT-FILM FROM LIST
G.remove_node(17) #remove Independent-Film ...too high a probability and useless to boot!

all_nodes = G.nodes()
num_movies_considered = 2826

#Make dict mapping inds to community labels:
comm={}
for keys in part:
    for nodes in part[keys]:
        comm[nodes] =  keys
        

ind_film_comm = comm[17] #community of independent film
new_part = part[ind_film_comm]
new_part.remove(17)
part[ind_film_comm] = new_part



def generate_keywords(L,p_rand,p_repeatlink):
    #Pick the first keyword randomly 
    nw = 0 #stores number of keywords picked
    inds_so_far = []
    pick = random.randrange(0,len(G.nodes()))
    inds_so_far.append(pick)
    nw += 1
    while nw<L:
        if random.random() < p_rand:
            while True:
                pick_ind = random.randrange(0,len(G.nodes()))
                pick = all_nodes[pick_ind]
                if pick not in inds_so_far:
                    break
            inds_so_far.append(pick)
            nw += 1 
        else:
            if random.random()  < p_repeatlink: #pick an existing node in list, and pick one of its neighbors i.e. create a repeat link
                
                while True:
                    
                    pick_cur = random.randrange(0,nw)
                    nbrs = G.neighbors(inds_so_far[pick_cur]) #neighbors of pick cur
                    pick = nbrs[random.randrange(0,len(nbrs))]
                    if pick not in inds_so_far:
                        break
                inds_so_far.append(pick)
                nw += 1
            else: #pick an existing node in list, and pick a node in a distinct community
                
                
                
                pick_cur = inds_so_far[random.randrange(0,nw)]
                
                comm_to_avoid = comm[pick_cur] #community label of pick cur
                list_of_commchoices = range(0,len(part))
                
                list_of_commchoices.remove(comm_to_avoid)
                    
                pick_com = list_of_commchoices[random.randrange(0,len(list_of_commchoices))]
                tries = 0
                flag = 0
                while True:
                        
                    
                    tries += 1
                    comm_choice = part[pick_com]
                    pick = comm_choice[random.randrange(0,len(comm_choice))]
                    if pick not in inds_so_far:
                        flag = 1
                        break
                    if tries>10*L:
                        break
                if flag ==1:
                    inds_so_far.append(pick)
                    nw +=1
    
    kwlist = [inv_root_ind[ii]+'\t'+'\t'+'\t'+'Cliche-score:'+'\t'+str(occ[inds_so_far[ii]]) for ii in range(len(inds_so_far))]
    return kwlist

while 1:
    
    while True:
        msg = "How many plot elements do you require? Enter an integer between 1 and 20: "
        L = enterbox(msg, title='', default='', strip=True)
        if L:
            try:
                L=int(L)
                break
            except:
                textbox(msg='', title='', text='Please enter an INTEGER value', codebox=0)
        else:
            sys.exit(0)
        
    
    
    while True:
        msg = "How often do you want to pick a random plot-element? Enter a decimal number between 0 and 1: "
        p_rand = enterbox(msg, title='', default='', strip=True)
        if p_rand:
            try:
                p_rand = float(p_rand)
                if p_rand >=0.0 and p_rand <= 1.0:
                    p_rand = float(p_rand)
                    break
                else:
                    textbox(msg='', title='', text='Please enter a DECIMAL value between 0 and 1', codebox=0)
                '''
                if float(p_rand) >=0.0 and float(p_rand)<=1.0:
                    break
                '''
            except:
               textbox(msg='', title='', text='Oops!Something went wrong...Please enter a DECIMAL value between 0 and 1', codebox=0) 
        else:
            sys.exit(0)
            
        
    
    
    
    
    while True:
        msg = "How familiar do you want plot-element combinations to be? Enter a decimal number between 0 and 1: "
        p_repeatlink = enterbox(msg, title='', default='', strip=True)
        
        if p_repeatlink:
            try:
                p_repeatlink = float(p_repeatlink)
                if p_repeatlink >=0.0 and p_repeatlink <= 1.0:
                    p_repeatlink = float(p_repeatlink)
                    break
                else:
                    textbox(msg='', title='', text='Please enter a DECIMAL value between 0 and 1', codebox=0)
            except:
                textbox(msg='', title='', text='Oops!Something went wrong...Please enter a DECIMAL value between 0 and 1', codebox=0)
        else:
            sys.exit(0)
    
    
    list_of_keywords = '\n'.join(generate_keywords(L,p_rand,p_repeatlink))
    
    
    
    #print list_of_keywords
    textbox(msg='Your chosen keywords are:', title='Movie plot element ideas', text=list_of_keywords, codebox=0)

    

    msg = "Do you want to continue spinning the wheel?"
    title = "Please Confirm"
    if ccbox(msg, title):# show a Continue/Cancel dialog
        pass  # user chose Continue
    else:
        sys.exit(0) # user chose Cancel