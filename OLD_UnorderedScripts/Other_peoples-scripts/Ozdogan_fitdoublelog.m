function [yfit] = fitdoublelog(nptperyear,y);
% function to fit DL to timeseries data
% adapted from Timesat for doublelogistic only
% USAGE: [yfit = fitdoublelog(11,ndvi);


nyear=1;  % always one year
nts = 1; % always one season
ylu(1) = 0.0;
ylu(2) = 1.0;
amplitudecutoff = 0;
spikecutoff = 2;
seasonpar = 1;
nenvi = 3;
wfact = 2;
wfact = 1/wfact;
startcutoff = 20;
startcutoff = startcutoff/100;
npt = nyear*nptperyear;
w = ones(1,npt);

format long;
format compact;

%global nyear nptperyear npt nenvi print debug wfact win 


%---- Generate basis functions needed for in fitgauss and fitlogistic ---------

width = nptperyear/4;

x(3) = 3; 
x(5) = 3;
fact = [0.2 0.4 0.7 1 1.3 1.7 2.1];
t1 = [1:nptperyear]';
t2 = [nptperyear + 1:2*nptperyear]';
x(1) = nptperyear + 0.5;
for i = 1:7
  for j = 1:2
    x(2) = width*fact(i)/(j*log(2)^0.25);   
    x(4) = x(2);  
    exp1 = exp(-((x(1)-t1)/x(2)).^x(3));
    exp2 = exp(-((t2-x(1))/x(4)).^x(5));
    yag(1:2*nptperyear,i,j) = [exp1 ; exp2];
  end
end

x(2) = nptperyear/20;
x(4) = nptperyear/20;    
fact = [0.3 0.6 1 1.5 1.9];
t = [1:2*nptperyear]';
for i = 1:5
  for j = 1:2
    x(1) = nptperyear - width*fact(i)/j;
    x(3) = nptperyear + width*fact(i)/j;    
    exp1 = exp((x(1)-t)/x(2));
    exp2 = exp((x(3)-t)/x(4));
    ydl(1:2*nptperyear,i,j) = 1./(1+exp1) - 1./(1+exp2);
  end
end

%---- Start processing --------------------------------------------------------

for i = 1:nts

  j = i;                             % dummy variable

%---- Check if sensordata is in the specified range, if not assign weight zero --

  for k = 1:npt
    if (y(k) < ylu(1)) | (y(k) > ylu(2)) 
	  w(k) = 0;
    end
  end  

%---- Time-series with too many data values with zero weight are not processed

  missingdata = 0;

  if sum(w == 0) >= floor(3*npt/4) 
    missingdata = 1;
  end 
  for k = 1:npt-floor(nptperyear/3)
	if abs(sum( w(k:k+floor(nptperyear/3)))) == 0 
      missingdata = 1;
    end 
  end
  
  
%---- Only time-series with non-constant datavalues are processed ---------------

  for k = 1:npt-1
    diff(k) = abs(y(k) - y(k+1)); 
  end
%  if (sum(diff < 1.e-6) >= npt/4 ) 
  if (sum(diff < 1.e-6) >= 3*npt/4 ) % Duarte
    missingdata = 1;
  end
  
  if missingdata == 0
          
%---- Identify spikes in the time-series and set the corresponding weigths ------   
%     to zero. If plotflag is set plot time-series and weights
            
    [w, dummy] = myspike(i,j,y,w,spikecutoff,nptperyear);       
    
%---- Fit sine and cosine functions to determine the number of annual seasons ---  
%     The current version of the code only allows one or two annual seasons     
%     The function returns a vector s that defines the intervals for subsequent 
%     fits to local functions                                                   

    [s,minimum,dummy] = myseason(i,j,y,w,seasonpar,amplitudecutoff,npt,nptperyear);
    
    
    if length(s) > 0


%---- Iterative fits to double logistic functions
%-------------------------------      

      yfit = myfitlogistic(i,j,s,y,w,ydl,nptperyear,npt); 
   
      
    end  % end if length(s) < 1      
  end  % end if missing data   
end  % end loop over time-series              

%---- Close all files ----------------------------------------------------------


disp('  Processing finished  ') 

