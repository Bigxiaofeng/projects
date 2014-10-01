**Readme files for matlab streamgraph scripts**
**Sameet Sreenivasan** 9/2014

1) PlotStreamGraph.m is a function that plots n distinct timeseries with t data points each as streamgraph as defined in “Stacked Graphs – Geometry & Aesthetics” by Lee Byron & Martin Wattenberg. 

The function requires two arguments. 1) The time series data provided in an n x t matrix, and 2) A resolution parameter for smoothing the time series using spline interpolation.

2) The script 'teststreamgraph.m' provides an example of using the PlotStreamGraph function using data on a particular LastFM user's listening history.

Navigate into the directory containing 1) and 2), and type "teststreamgraph" at the Matlab console to see the PlotStreamGraph function in action.
