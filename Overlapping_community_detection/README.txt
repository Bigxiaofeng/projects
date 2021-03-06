**Readme files for overlapping community detection using the label propagation algorithm**
**Sameet Sreenivasan** 9/2014

1) OLPA_communities.m is a function that implements the label propagation algorithm designed to discover overlapping communities as described in:

Steven Gregory,  'Finding overlapping communities in networks by label propagation', New Journal of Physics 12, 103018. 

2) testOLPA.m provides an example of using the OLPA_communities function using the Karate Club network data, and using nu = 2, T = 100 and with the belief-propagation-like modification turned on. Specifically, it attempts to detect the communities that each node belongs to, where each node is allowed to belong to at most 2 communities. 

Navigate into the directory containing 1) and 2), and type "testOLPA" at the Matlab console to see the OLPA_communities function in action. The output at the console shows the number of update steps that OLPA has currently completed, and the final line shows the labels of the communities present.