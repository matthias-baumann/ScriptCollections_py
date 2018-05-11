function out = doublelog(t,k,vb,ve,c,d,p,q);
% double logistic function
% inputs:
% t     time
% k     asymptotic value of NDVI
% vb    NDVI value at the beginning of the season
% ve    NDVI value at the end of the season
% c     slope at the first inflection point
% d     slope at the second inflection point
% p     date of the first inflection point
% q     date of the second inflection point


out = vb+((k/(1+exp(-c*(t-p))))-((k+vb-ve)/(1+exp(-d*(t-q)))));
