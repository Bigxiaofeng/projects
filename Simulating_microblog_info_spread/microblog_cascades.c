/*
 *  microblog_cascades.c
 
 *  Simulates the dynamics of message forwarding in a Twitter-like environment. Every user has
 *  multiple received messages in a queue. Users generate new messages with certain probability
 *  and forward messages on their queue with certain probability. Users pay attention only to 
 *  a fixed number of their most recently received messages. This competition for attention 
 *  plays a role in how far a message can/will spread.
 
 *  Created by Sameet Sreenivasan on 5/14/14.
 *  Copyright 2014. All rights reserved.
 *
 */



#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<time.h>


#define N 10000  // size of the network
#define sf_exponent 2.5  // power-law exponent of the degree distribution
#define avg_degree 10
#define p_n 0.45  // probability of new tweet generation
#define p_r 0.2   // probability with which a user retweets a tweet on his queue
#define MAX_REP 10 // number of realizations of network and dynamics
#define L 10 // memory length - the number of most recent messages that each user pays attention to
#define T 400000 // number of time steps for which node update dynamics is run 


FILE *outfile1;
FILE *outfile2;
FILE *outfile3;
FILE *outfile4;

static int starttracking;
static int trackedsize;
int **touched;
int **tweeted;
static int moved ;

typedef int Bool;

//Define the 'node' data structure
struct nodetype {
	int l; //prescribed degree	
	int k; //realized degree
	
	int *conn; //pointer to integer array storing neigjbors or "Connections"
	Bool flag; //Boolean variable useful for cluster counting etc.
};

struct nodetype node[N]; //define array of N nodes 




// Linked list implementation for memory and feed lists
struct post{
	int msg;
	//int tstamp;
	struct post *next;
};


//Linked lists per node for feed queue. N such linked lista
struct post *feedposts[N];

int *Lf;	//pointer to array storing length of feeds on each user's wall

int numcopies[T]; //counter storing number of copies of each tweet; used as an intermediate to calculate lifetime


double unif() 
{
	double r;
	
	r = (double)rand()/(double)RAND_MAX;
	
	return(r);
}

//Function samples continuous random variables from power law with given power-law exponent and average degree 
double sample_power_law(double gamma,double k_avg)
{
	double u,x;
	u = unif();
	//printf("u = %f \n",u);
	x = ((gamma-2)/(gamma-1))*k_avg*pow(1-u,(-1/(gamma-1)));
	return(x);
}


//Function to generate a directed graph
void Gen_graph()
{
	int i,j,kk,current,success,tries,list_modified,kpres;
	int sum_deg,kmax,endlist;
	int pick_in,pick_out,node_in,node_out;
	int *stubs; //pointer to array storing in-stubs
	int ktemp[N]; //pointer to array storing temporary degree of nodes during stub connection
	
	
	
	sum_deg = 0;

	//First: generate degree sequence
	
	for (i=0; i<N; ++i) {
		
		// generate in-degree
		kmax = ceil(sqrt(avg_degree*N));
		
		do {
			kpres = ceil(sample_power_law(sf_exponent,avg_degree));
		} while (kpres>kmax);
		
		node[i].l = kpres;
		sum_deg += kpres;
		
	}
	
	while(sum_deg%2 != 0){
			j = floor(unif()*N);
			sum_deg = sum_deg - node[j].l;
			// generate new in-degree and out-degree for selected node
			kmax = ceil(sqrt(avg_degree*N));
			do {
			kpres = ceil(sample_power_law(sf_exponent,avg_degree));
			} while (kpres>kmax);	
			node[j].l = kpres;
			sum_deg += kpres;
		}


	//Second: Create outgoing and incoming stub lists

	stubs = (int *)malloc(sum_deg * sizeof(int));
	if(!stubs) {
		printf("mem. req. failed \n");
		exit(1);
	}
	
	
	//Populate stub list with vertex copies	
	current = 0; //current position on list to be filled.	
	for(i=0; i < N; ++i) {
		for(j=0;j<node[i].l;++j) {
			stubs[current]=i;
			++current;
		}
	}
	

	
	//Third : Hook up in-stubs with out-stubs randomly
	
	//store the size or equivalently the position of last element on each list - these will be updated as the process 
	//continues


	endlist = sum_deg;
	 

	
	for(i = 0; i < N; ++i) {
		ktemp[i] = 0;
		
	}
	
	

	
	
	
	//hook up stubs until lists are exhausted
	success = 0;
	while(endlist>0) {
		
		//find a pair of stubs that are compatible
		tries = 0;
		do {
			++tries;
			
			//for convenience we call the pair of nodes (node_in,node_out) ; note that the graph is not directed
			pick_in = floor(unif()*endlist);
			node_in = stubs[pick_in];
			pick_out = floor(unif()*endlist);
			node_out = stubs[pick_out];
			
			if (node_in != node_out) {

				if(ktemp[node_in] == 0 || ktemp[node_out] == 0) //if node_in does not have neighbors yet or 
					//node_out does not have neighbors yet, then they can be paired.
					success = 1;
				else {  //otherwise check that they have not been paired before
					success = 1;
					for(kk=0;kk<ktemp[node_in];++kk)
					{
						if(node[node_in].conn[kk] == node_out) //if yes, prohibit connection
							success = 0;
						break;
					}
				}
			}
			else //node_in same as node_out
				success = 0;
			
			if(tries > 100*endlist)
				break;
			
		}while(!success);
		


		if(success) {
			
			++ktemp[node_in];
			++ktemp[node_out];
			
	
			//Update connections of node_in
			if(ktemp[node_in]==1)
				{
				
				node[node_in].conn = (int *)malloc(ktemp[node_in]*sizeof(int));
			
				}
			else{
				
				node[node_in].conn = (int *)realloc(node[node_in].conn, ktemp[node_in]*sizeof(int));
				}

			
			if(!node[node_in].conn) {
				printf("node_in.folls mem. req. failed \n");
				exit(1);
			}
			node[node_in].conn[ktemp[node_in]-1] = node_out;
			
			//Update connections of node_out
			if(ktemp[node_out]==1)
				node[node_out].conn = (int *)malloc(ktemp[node_out]*sizeof(int));
			else
				node[node_out].conn = (int *)realloc(node[node_out].conn,ktemp[node_out]*sizeof(int));
			

		
			if(!node[node_out].conn){
				printf("node_out mem. req. failed \n");
				exit(1);
			}
			node[node_out].conn[ktemp[node_out]-1] = node_in;
		
		
		list_modified = 0;
	 		if(pick_in != endlist-1) {

					if(pick_out != endlist-1){
						stubs[pick_in] = stubs[endlist-1];
						--endlist;
						}
					else{
							if(pick_in !=endlist-2){ //pick_in not endlist-2, pick_out equal to endlist-1
								stubs[pick_in]=stubs[endlist-2];
								endlist = endlist- 2;
								list_modified = 1;
								}
							else //pick_in equal to endlist-2, pickout equal to endlist -1
								endlist = endlist- 2;
							}
					}
				
			else // pick_in == endlist-1
				--endlist;
			
	
			if(!list_modified){
				if(pick_out != endlist-1) {
					stubs[pick_out] = stubs[endlist-1];
					--endlist;
					}
				else
					--endlist;
				}
			
		}
		else
			break;
		
	}
	

	for (i=0; i<N; ++i) {
		
		node[i].k = ktemp[i];
	}
	
	free(stubs);
	
}	
// Graph generation done!!
//---------------------------------------------------------------------------------------------------------------------------------------------


/******************************************************************************************/
void Construct_Graph(int nodes, int links)
{
  int no_links,id1,id2,dg,fl,nn,nc,nbr1,nbr2;
  double weight;
  
  no_links = 0;
    
  while(no_links < links)
    {
      id1 = (int)(unif() * N);
      id2 = id1;
      
      while(id2 == id1)
	id2 = (int)(unif() * N);
    
      dg = node[id1].k;
     
      
      fl = 0;
            
      for(nn = 0; nn < dg; ++nn)
	{
	  if(node[id1].conn[nn] == id2)
	    fl = 1;
	}
           
      
      if(!fl)
	{
	  node[id1].k = node[id1].k + 1;
	  
	  if(node[id1].k == 1)
	     {
	       
	       node[id1].conn = (int *)malloc(1 * sizeof(int));
	       
		
	    }
	      else
	    {
	      
	      nc = node[id1].k;
	      node[id1].conn = (int *)realloc(node[id1].conn,nc * sizeof(int));
	    
	    }
	   
	  if(!node[id1].conn) 
	    {
	      printf("mem req failed\n");
	      exit(1);
	    }
	  
	  nbr1 = node[id1].k - 1;
	
	  node[id1].conn[nbr1] = id2;
	  
	  node[id2].k = node[id2].k + 1;
	  
	  if(node[id2].k == 1)
	    node[id2].conn = (int *)malloc(1*sizeof(int));
	  else
	    {
	      nc = node[id2].k;
	      node[id2].conn = (int *)realloc(node[id2].conn,nc * sizeof(int));
	    }
	  
	  if(!node[id2].conn) 
	    {
	      printf("mem req failed\n");
	      exit(1);
	    }
	   
	  nbr2 = node[id2].k - 1;
	  node[id2].conn[nbr2] = id1;
	  
	  
	
	  ++no_links;
	}
    }       

   
}
/*******************************************************************************************************/

//Function that adds message m to feedposts of u's followers 
void Tweet(int u, int m, int tt) 
{
	int lstnr,j;
	int queuepos,removed_meme;
	struct post *newfeedpost;
	struct post *cur,*prev;
		
	
	//Spread message to followers, 
	
	for(j=0;j<node[u].k;++j) {
		
	       
		  
		lstnr = node[u].conn[j];
		
		
		++Lf[lstnr]; //increment listener's feed queue.
		
		newfeedpost = malloc(sizeof(struct post));
		if(!newfeedpost){
			printf("newfeedpost mem. req. failed \n");
			exit(1);
		}
		newfeedpost->msg = m;
		newfeedpost->next = feedposts[lstnr];
		feedposts[lstnr]=newfeedpost;
		newfeedpost = NULL;
		
		++numcopies[m];
		
		
		if(m-starttracking>=0 && m-starttracking<trackedsize)
		  if(touched[lstnr][m-starttracking]!=-3)//if lstnr is not the originator of m 
			touched[lstnr][m-starttracking]=1; //indicates that message has touched lstnr
			
		
		
		//If queue size just exceeded L, remove L+1 th element
		
		if(Lf[lstnr]>L){
			
		  
			for(cur=feedposts[lstnr],prev=NULL,queuepos=0;cur!=NULL && queuepos<L;prev=cur,cur=cur->next,++queuepos);//find L+1 th element (i.e. there are L indices(0..L-1) before it)
		
			
			prev->next = NULL;
			removed_meme = cur->msg;
				
			--numcopies[removed_meme];
			
			free(cur);
			--Lf[lstnr];
			
				
		}
	}
	
	
}




//-------------------------------------------------------------------------------------------------------------------------------------------------

main()
{
	
	int i,j,usr,new_meme,rt_meme,num_lines[MAX_REP],E_t;
	int tid; //tweet id or number of tweets that have been generated
	int mindeg,maxdeg,sumofdegs;
	int reps,t;
	int num_distinct_tweets,eligs,ssamples;
	double sumeligs;
	struct post *f,*g,*temp;
	double avdeg;
	int not_survived,survived,total_tweeted,total_touched,total_branching;
	int sum_ones, sum_twos, sum_threes,all_touched,numtweeted;
	
	starttracking = ceil(p_n*10*N);
	
	trackedsize = 10000; //number of tweets that are monitored 
	
	//printf("%d %d \n",starttracking,trackedsize);
	
	E_t = ceil(p_n*T + 0.2*p_n*T);
	
	
	//Allocate memory for "lifetime" array
	int *lifetime = (int *)malloc(sizeof(int)*E_t);
	
	
	//Allocate memory for "times_rt" array
	int *times_rt = (int *)malloc(sizeof(int)*E_t);
	
		
	//Allocate memory for "branchng" array
	//int *branching = (int *)malloc(sizeof(int)*E_t);
	
	
	
	//Allocate pointer to array of N int pointers which store "retweeted" status of msgs per node
	tweeted = (int **)malloc(sizeof(int *)*N);
	
		
	//Allocate pointer to array of N int pointers which store "touched" status of msgs per node
	touched = (int **)malloc(sizeof(int *)*N);
	
	

	srand((unsigned)time(NULL));

	//srand(27636); //SEED TO USE WHILE DEBUGGING
	
	reps = 0;
	
	outfile1 = fopen("distributions.txt","w"); //store quantities measured for general tweets
	outfile2 = fopen("probabilities.txt","w");
	outfile3 = fopen("samplesperrun.txt","w");
	

	
	while(reps < MAX_REP)
	{
		printf("%d \n",reps);
		
		Gen_graph();
		// Now comes the meme dynamics
		
		//Degree statistics - append degrees of all nodes to file
		outfile4 = fopen("sample_degrees.txt","a");
		for(i=0;i<N;++i)
		fprintf(outfile4,"%d \n",node[i].k);
		fclose(outfile4);
		
		
		
		mindeg = N;
		maxdeg=0;
		sumofdegs = 0;
		for(i=0;i<N;++i){
			sumofdegs += node[i].k;
			if(node[i].k<mindeg)
				mindeg=node[i].k;
			if(node[i].k>maxdeg)
				maxdeg=node[i].k;
					}
		avdeg = (double)sumofdegs/(double)N;
		
		
		printf(" Gen graph done. Average degree is %f \n",avdeg);
		
		
		//Initialize stuff
		
		//////CALLOCING TWEETED FLAGS AND TOUCHED FLAGS
		for(i=0;i<N;++i){
			tweeted[i]=(int *)calloc(T,sizeof(int));
			if(!tweeted[i]){
				printf("mem. req.failed at retweet matrix alloc. \n");
				exit(1);
			}
		}
		
		for(i=0;i<N;++i){
			touched[i]=(int *)calloc(10000,sizeof(int));
			if(!touched[i]){
				printf("mem. req.failed at retweet matrix alloc. \n");
				exit(1);
			}
		}
		
		Lf = malloc(N*sizeof(int));	//pointer to array storing length of feeds on each user's wall
		
		for(i=0;i<N;++i){
			
			Lf[i]=0;
			feedposts[i]=NULL;
			
		}
		printf("callocing and mallocing done \n");
		//////////////////////////////////////////////////
		
		for(t=0;t<E_t;++t){
			lifetime[t]=-1;
			numcopies[t]=-1;
			times_rt[t] = 0;
		}
		
		printf("initializing done \n");
		
		
		t = 0;
		num_distinct_tweets=0;
		tid = 0;
		
		sumeligs=0;
		ssamples = 0;
		eligs = 0;
		while(t < T) {
			
			if(t%50000 == 0)
				printf("%d \n",t);
			

			
			usr = floor(unif()*N); //pick random user
			
			if(unif()<p_n) {
				new_meme = tid;
				Tweet(usr,new_meme,t);
				tweeted[usr][new_meme]=1;
				if(new_meme-starttracking>=0 && new_meme-starttracking<trackedsize)
				  touched[usr][new_meme-starttracking]=-3; //indicates that this meme is being tracked and originated at "usr"
				//lifetime and number of times retweeted are now "initialized" to 0
				++lifetime[new_meme];
				++numcopies[new_meme];
				++num_distinct_tweets;
				++tid;
			}
			
			//user scrolls through his feed
				
			f = feedposts[usr];
				
			while(f != NULL){//consider each post in usr's current feed if the user hasn't gotten bored and quit scrolling
					
				rt_meme = f->msg;

				if (unif()< p_r) { //if post catches usr's attention,
			
				  if(tweeted[usr][rt_meme] != 1){ //and he has not retweeted it before
					Tweet(usr,rt_meme,t);
					++times_rt[rt_meme]; //increment times retweeted
					tweeted[usr][rt_meme]=1;
					 }
				}
				else
				  {
				    if(tweeted[usr][rt_meme]!=1) {
				     
					tweeted[usr][rt_meme]=-2;//signifies that the msg has been considered for retweet at least once
					
					
				    }
				  }
					
				f = f->next;
			}
				
			
			//Update lifetimes for tweets:
			for(i=0;i<tid;++i){ //existing tweets can have a maximal index of tid
				if(numcopies[i]!=-1 && numcopies[i]!=-2){ //tweet i has been birthed, and has not yet died
					if(numcopies[i]==0) //died in this step
						numcopies[i]=-2; //set to dead
					else 
						++lifetime[i];//meme survived this time step: add one to its lifetime.
				}
			}
			// DONE UPDATING LIFETIMES
			++t;
		}
		
		printf("dynamics done \n");
		
		
		
		num_lines[reps] = 0;
		//Record everything of significance from this realization
		survived = 0; // counter for message that indicates on how many node queues its copy "survived" long enough to be considered at least once for forwarding
		total_tweeted = -1;
		total_touched = 0;
		total_branching = 0;
		sum_ones = 0;
		sum_twos = 0;
		sum_threes = 0;
		all_touched = 0;
		for(i=starttracking; i<starttracking+trackedsize;++i){ // for tracked tweets
		  for(j=0;j<N;++j){
		    
		    if(touched[j][i-starttracking]==1 && (tweeted[j][i]==1 || tweeted[j][i]==-2))
		      ++survived;
		    if(tweeted[j][i]==1 && touched[j][i-starttracking]==1){	
		      ++total_tweeted;
		      total_branching += node[j].k - 1;
		    }
		    
		    if(touched[j][i-starttracking]==1)
		      ++total_touched;
		     
		    
		  }
		}
	

		fprintf(outfile2,"%f %f %f %f \n",(double)(survived)/(double)(total_touched),(double)(total_tweeted)/(double)(survived),(double)(total_branching)/(double)(total_tweeted),(double)(total_branching)/(double)(total_touched));
		
		  
		for(i=starttracking;i<tid;++i){
		  survived = -1; //counter for message that indicates how many nodes received a copy of the message
		  numtweeted  = 0;
		  for(j=0;j<N;++j)
		    if(tweeted[j][i]==1)
		      ++numtweeted;
		  if(i<starttracking+trackedsize){
		    survived = 0;
		    for(j=0;j<N;++j){
		      if(touched[j][i-starttracking]==1)
			 ++survived; //number that "saw" tweet i 
		    }
		  }
		  fprintf(outfile1," %d %d %d %d %d\n",numcopies[i],times_rt[i],survived,lifetime[i],numtweeted);				  
		}
		    num_lines[reps] = tid-starttracking; //number of tweets gathered for observation in this repetition
	
		
		
	
	/*******************************/
	//FREE ALLOCATED MEMORY		
	
	//Free linked lists
		for(i=0;i<N;++i){
		
			if(Lf[i]>0){
				g=feedposts[i];
				while(g!=NULL){
					temp = g;
					g=g->next;
					free(temp);
				}
			}
		}
	
		//Free counter
		free(Lf);
	
		//Free graph related memalloc
		for(i=0;i<N;++i){
			if(node[i].k>0)
				free(node[i].conn);
		
		}
		
		//Free tracking and tweeting memalloc
		for(i=0;i<N;++i){
			free(tweeted[i]);
			free(touched[i]);		
		}
	
	/*********************************/
	

		++reps;
	}	
	
	fclose(outfile1);	
	fclose(outfile2);

	for(reps=0;reps<MAX_REP;++reps)
		fprintf(outfile3,"%d \n",num_lines[reps]);
	fclose(outfile3);
	
	
}	








