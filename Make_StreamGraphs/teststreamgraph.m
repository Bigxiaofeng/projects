%Test code for PlotStreamGraph.m
%Uses LastFM listening data from https://github.com/jsundram/streamgraph.js/blob/master/examples/data/lastfm.js
clear all;
close all;

lastfm_series = load('lastfmdata.txt');
PlotStreamGraph(lastfm_series,0.1);

