#!/usr/bin/env python
#Sameet Sreenivasan August 2014

from imdb import IMDb
import collections
import networkx as nx
from networkx.algorithms import bipartite

#Function that extracts all movies of a given genre present in input file, along with release month and year, and writes them to outputfile
def filter_movs_by_genre(chosengenre,inputfile,outputfile):
    f = open(inputfile,'r');
    g = open(outputfile,'w')
    num_movies = 0
    for line in f:
        cols = line.split('\t')
        m_id = cols[0]
        year = cols[1]
        month = cols[2].strip('\n')
        m_obj = i.get_movie(m_id)
        print m_id
        i.update(m_obj)
        if m_obj.has_key('genre'):
            print m_obj['genre']
            if chosengenre in m_obj['genre']:
                num_movies += 1
                g.write(m_id+'\t'+year+'\t'+month+'\n' )
                
    f.close()
    g.close()
    return num_movies

def get_keywords(inputfile,outputfile,*args): #get keywords from movies which DON'T CONTAIN args in GENRE:
                                                #output file in format: movie_id, year, ratings, number of votes, keyword list
    f = open(inputfile,'r')
    g = open(outputfile,'w')
    global nummovies_written, nummovies_without_genre
    nummovies_written = 0
    nummovies_without_genre = 0
    
    for line in f:
        cols = line.split('\t')
        m_id = cols[0]
        year = cols[1]
        m_obj = i.get_movie(m_id)
        print m_id, year
        i.update(m_obj)
        if m_obj.has_key('genre'):
            No_unwanted_genres = not(any(item in m_obj['genre'] for item in args))
            if No_unwanted_genres:
                nummovies_written += 1
                
                
                if m_obj.has_key('keywords'):
                    m_kw = [item.encode('ascii','ignore') for item in m_obj['keywords']]
                else:
                    m_kw = []
                
                imdb_id = i.get_imdbID(m_obj)
                if imdb_id is None:
                    imdb_id = 'NULL'
                
                q.write(str(m_id)+'\t'+str(imdb_id)+'\n')
                
                g.write(imdb_id+'\t'+year)
                for kw in m_kw:
                    g.write('\t'+kw)
                g.write('\n')
    
                
        else:
            nummovies_without_genre += 1
    print "Total number of movies written to file:",nummovies_written
    print "Total number of movies without genre:", nummovies_without_genre
    g.close()
    q.close()

#Calculatesfor a given pair of roles (type1, type2) (example: director-cinematographer) the score for each person in each of the roles
#i.e. how many times that person has occupied the type1 and type2 roles respectively.
def find_type_overlap(inputfile,type1,type2):
    type1score = collections.defaultdict(int)
    type2score = collections.defaultdict(int)
    
    f = open(inputfile,'r')
    q = open('contributions_'+type1+'\t'+type2+'.txt','w')
    for line in f:
        cols = line.split('\t')
        m_id = cols[0]
        print m_id
        m_obj = i.get_movie(m_id)
        i.update(m_obj)
        if m_obj.has_key(type1) and m_obj.has_key(type2):
            type1peeps = m_obj[type1]
            type2peeps = m_obj[type2]
            for mems1 in type1peeps:
                type1score[mems1.personID] += 1
            for mems2 in type2peeps:
                type2score[mems2.personID] += 1
    set1 = set(type1score.keys())
    set2 = set(type2score.keys())
    unique_members = set1.union(set2)
    print 'Number of unique persons: ', len(unique_members)
    dual_roles = set1.intersection(set2)
    print 'Number of nodes with dual roles:', len(dual_roles)
    for pp in dual_roles:
        q.write(str(type1score[pp])+'\t'+str(type2score[pp])+'\n')
    q.close()
        
#Builds a bipartite graph of relationships between people in specific behind-the-scenes roles (ex: director and editor , editor and composer etc)
# each link connects two individuals that have worked on at least one film together each occupying one of the two roles. The weight on the link indicates
# the number of films that they have worked on together.

def Build_Bipartite(inputfile,type1,type2):
    set1 = set()
    set2 = set()
    f = open(inputfile,'r')
    B=nx.Graph() #stores the bipartite affiliation graph between node types 1 and 2
    edgeweight = collections.defaultdict(int)
    numpairs = 0
    num_accepted_pairs = 0
    for line in f:
        cols = line.split('\t')
        m_id = cols[0]
        print m_id
        m_obj = i.get_movie(m_id)
        i.update(m_obj)
        if m_obj.has_key(type1) and m_obj.has_key(type2):
            type1peeps = m_obj[type1]
            type2peeps = m_obj[type2]
            
            for mems1 in type1peeps:
                set1.add(mems1)
                for mems2 in type2peeps:
                    set2.add(mems2)
                    numpairs += 1
                    if mems1 != mems2 and mems1 not in set2 and mems2 not in set1: #if both roles aren't filled by same person, and persons don't take on different roles
                        num_accepted_pairs += 1
                        
                        B.add_node(mems1.personID,bipartite=0)
                        B.add_node(mems2.personID,bipartite=1)
                        edgeweight[(mems1.personID,mems2.personID)] += 1
                        B.add_edge(mems1.personID,mems2.personID,weight = edgeweight[(mems1.personID,mems2.personID)])
            #print B.nodes(),B.edges()
            
    print 'Num_pairs = ', numpairs
    print 'Num accepted pairs =', num_accepted_pairs
        
    f.close()               
    return B


if __name__ == '__main__':
    i = IMDb('sql',uri='mysql://root@localhost/imdb') #connect to local SQL DB holding IMDb data
    H = Build_Bipartite('movs_eng_us_txt','director','cinematographer')
    
  