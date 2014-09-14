%example for usage of the OLPA_communities function
%uses "Zachary's karate club network"as a test example.


clear all;
close all;

A = load('karate.csv');
l = OLPA_communities(A,2,100,1); %each node can belong to at most two communities
labels_used = find(any(l>0,1));

%Display the labels that are actually used by the nodes - this is equal to
%the number of distinct communities
disp('The labels with non-zero participation coefficients are:');
disp(labels_used);
