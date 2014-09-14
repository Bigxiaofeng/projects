function comm_labels = OLPA_communities(A,nu,T,bp_on)


N = size(A,1); % network size


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%get list of nbrs for each node from adjacency matrix

%first determine max degree
maxdeg = 0;
for i= 1:N
    k = length(find(A(i,:)~=0));
    if k>maxdeg
        maxdeg = k;
    end
end

%then make nbr list
nbr_list = zeros(N,maxdeg);    
deg = zeros(N,1);

for i = 1:N
    nbrs = find(A(i,:)==1);
    deg(i)= length(nbrs);
    nbr_list(i,1:length(nbrs)) = nbrs;
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%Label Propagation for overlapping communities (COPRA //steven gregory)
%with and without the Belief Propagation like modification 

old_labels = diag(ones(N,1)); % each node has weight 1 for its onw label


t = 0;
while(t < T)
    new_labels = zeros(N);    
    switch bp_on
        case 1 %BP inspired OLPA 
            for i = 1:N %sending messages to each node's neighbors
                if deg(i) >0
                    nbrs = nbr_list(i,1:deg(i)); %row vector of neighbor ids
                    for j = 1:length(nbrs)
                        %send message to jth neighbor
                        new_labels(nbrs(j),:) = new_labels(nbrs(j),:)+ sum(old_labels(nbrs',:),1) - old_labels(nbrs(j),:);
                     end   %for all neighbors
                 end   %for nodes with degree > 0 
            end  %for all nodes
        
        case 0   %Vanilla OLPA
             for i = 1:N %sending messages to each node's neighbors
                if deg(i) >0
                    nbrs = nbr_list(i,1:deg(i)); %row vector of neighbor ids
                    for j = 1:length(nbrs)
                        new_labels(nbrs(j),:) = new_labels(nbrs(j),:)+ sum(old_labels(nbrs',:),1);
                     end   %for all neighbors
                 end   %for nodes with degree > 0 
            end  %for all nodes
    end % END SWITCH     
    
    for i = 1:N
        if ~any(new_labels(i,:))
            new_labels(i,i) = 1;
        end
    end
    
    
    old_labels = new_labels./repmat(sum(new_labels,2),1,N);
    
    
    
    for i = 1:N
        iw = find(old_labels(i,:)<(1/nu));
        if length(iw) == N
            maxvalids = find(old_labels(i,:) == max(old_labels(i,:)));
            rr = ceil(rand(1)*length(maxvalids));
            saved = maxvalids(rr);
            old_labels(i,iw) = 0;
            old_labels(i,saved) = 1;
        else
            old_labels(i,iw) = 0;
        end
        old_labels(i,:) = old_labels(i,:)./sum(old_labels(i,:),2);
    end
    
    
    if mod(t,10)==0
        disp(strcat('olpa_time_steps = ',int2str(t)));
    end
    
    
t = t + 1;

end
comm_labels = old_labels;
