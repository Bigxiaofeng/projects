%A streamgraph is a type of stacked graph. From the Lee Byron and Martin Wattenberg paper: The main idea behind a stacked graph follows Tufte?s macro/
%micro principle: the twin goals are to show many individual time series, while also conveying their sum

%Function to plot smoothened streamgraphs from multiple time series
%Input:
%1)  g: matrix that stores a time series; each row is a distinct time series
% consisting of non-negative values
% 2) res: resolution at which the time series is interpolated


%
% Uses the min-weighted wiggle implementation described in:  ?Stacked Graphs ? Geometry & Aesthetics? by Lee Byron & Martin Wattenberg


function PlotStreamGraph(g,res)

t = 1:size(g,2); %time steps
tt = 1:res:size(g,2); % finer time steps at resolution "res"
f = zeros(size(g,1),size(tt,2)); %stores new data obtained by spline interpolation at finer resolution
for i = 1:size(g,1)
    yy = spline(t,g(i,:),tt); %do spline interp.
    f(i,:) = yy;
end 


%%%For time steps where every time series simultaneously had zero activity, replace zeros by a very small positive value
zrows = find(all(f == 0,1));
f(:,zrows) = realmin*ones(size(f,1),length(zrows));
%%%

f =  f'; %transpose the time series
num_series = size(f,2); %number of distinct time series
length_series = size(f,1); %length of each interpolated time series

%Sometimes the interpolation can give rise to negative data points, but the implementation requires the data to be positive  - as pointed out in http://klab.wdfiles.com/local--files/ian-stevenson/streamGraph_wrapper.m
%Make each time series positive
for i=1:size(f,2)
   f(:,i) = f(:,i)+abs(min(f(:,i)));
end


%%% Implement the weighted-wiggle streamgraph 
f_prime = diff(f);  
g0_prime = zeros(length_series-1,1);
sumf = 1./sum(f(1:end-1,:),2); 

for i = 1:num_series
  g0_prime = g0_prime + (0.5*f_prime(:,i) + sum(f_prime(:,1:i-1),2)).*f(1:end-1,i);  
end

g0_prime = -sumf.*g0_prime;
g0 = cumsum([0;g0_prime]);

f_new = cumsum(f,2)+kron(ones(1,num_series),g0); 
%%%%%

%Plot it
figure;
whitebg(1,'k');
colors=hsv(size(f_new,2));
x = 1:size(f_new,1);
patch([x fliplr(x)],[f_new(:,1); flipud(g0)]',colors(1,:),'FaceAlpha',1,'EdgeAlpha',0.3);
for i=2:size(f_new,2)
    patch([x fliplr(x)],[f_new(:,i); flipud(f_new(:,i-1))]',colors(i,:),'FaceAlpha',1,'EdgeAlpha',0.3);
end
set(gca,'Xtick',[]);
set(gca,'Ytick',[]);
xlim([0 size(f_new,1)]);






