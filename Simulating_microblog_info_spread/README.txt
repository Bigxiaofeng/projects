#Sameet Sreenivasan 2014

Simulates the dynamics of message forwarding in a Twitter-like environment. Every user has multiple received messages in a queue. Users generate new messages with certain probability and forward messages on their queue with certain probability. Users pay attention only to a fixed number of their most recently received messages. This competition for attention plays a role in how far a message can/will spread.

OUTPUT 
outfile 1 stores quantities related to the branching process as measured in simulation
outfile 2 stores lifetimes, number of copies etc for each tweet (in the observation period)
outfile 3 stores the number of samples i.e. simulated tweets that fell into the tracking period.


