

% 11 dates and 6 sites
b3 = zeros(11,6);
b4 = zeros(11,6);
ndvi = zeros(11,6);

days = [62,118,134,150,182,198,206,230,238,278,302];

% observed fPAR
% day, aprs1, pars2, pars3, pars4, pars5, par6
f = load('fpar.txt');


for i = 1:6
    name = strcat('pars',num2str(i),'_band3.txt');
    tmp = load(name);
    b3(:,i) = tmp(:,2);
    clear name tmp;
    name = strcat('pars',num2str(i),'_band4.txt');
    tmp = load(name);
    b4(:,i) =  tmp(:,2);
    clear name tmp;
    
    ndvi(:,i) = (b4(:,i)-b3(:,i))./(b4(:,i)+b3(:,i));  %this is single color index that ranges from 0-1
    
    %figure;
    %plot(days,ndvi(:,i),'ok');
    %ylim([0 1]);
    %hold on;
    %plot(days,ndvi(:,i),':k');
    
    %plot(f(:,1),f(:,i+1),'.');
    
    %title(strcat('pars',num2str(i)));
    
    
end

%{
dy = [1,33,49,57,81,89];
xy = zeros(36,2);
l=1;
for i = 1:6:36
    xy(i:i+5,1) = ndvi(4:9,l);
    xy(i:i+5,2) = f(dy,l+1);
    l = l+1;
end
%}

%{
% parameters for PARS1
vb = 0.1;
ve = 0.1;
k = 0.6;
c = 0.3;
d = 0.3;
p = 165;
q = 240;

% parameters for PARS2
vb = 0.15;
ve = 0.15;
k = 0.6;
c = 0.3;
d = 0.2;
p = 167;
q = 238;

% parameters for PARS3
vb = 0.1;
ve = 0.15;
k = 0.65;
c = 0.3;
d = 0.2;
p = 160;
q = 238;

% parameters for PARS4
vb = 0.1;
ve = 0.15;
k = 0.65;
c = 0.3;
d = 0.2;
p = 180;
q = 240;

% parameters for PARS5
vb = 0.1;
ve = 0.15;
k = 0.65;
c = 0.2;
d = 0.3;
p = 180;
q = 245;

% parameters for PARS6
vb = 0.1;
ve = 0.1;
k = 0.65;
c = 0.2;
d = 0.2;
p = 180;
q = 245;
%}

vb = [0.1,0.15,0.1,0.1,0.1,0.1];
ve = [0.1,0.15,0.15,0.15,0.15,0.1];
k = [0.6,0.6,0.65,0.65,0.65,0.65];
c = [0.3,0.3,0.3,0.3,0.2,0.2];
d = [0.3,0.2,0.2,0.2,0.3,0.2];
p = [165,167,160,180,180,180];
q = [240,238,238,240,245,245];


locs = {'PARS1 Corn','PARS2 Corn','PARS3 Corn','PARS4 Bean','PARS5 Bean','PARS6 Bean'};

site=1;

for i = 1:365
    out(i,1) = doublelog(i,k(site),vb(site),ve(site),c(site),d(site),p(site),q(site));
end

figure;
plot(days,ndvi(:,site),'or','LineWidth',2);
hold on;
plot(1:365,out,'.k');
plot(f(:,1),f(:,site+1),'xb','LineWidth',1.5);
ylim([0 1]);
xlim([120 300]);
set(gca,'FontSize',12);
xlabel('day of the year');
ylabel('NDVI and fPAR');
title(char(locs(site)));
print -djpeg -r200 plot.jpg

%{
figure;
plot(out(f(:,1)),f(:,site+1),'.k');
axis square;
xlim([0 1]);
ylim([0 1]);
set(gca,'FontSize',12);
xlabel('NDVI');
ylabel('fPAR');
title(char(locs(site)));

XY = zeros(11,2,6);
for p = 1:6 % 6 sites
    for i = 1:11
        s = find(f(:,1) == days(i));
        if(isempty(s) == 0)
            XY(i,1,p) = ndvi(i,p);
            XY(i,2,p) = f(s,p+1);
        else
            XY(i,:,p) = NaN;
        end
        clear s;
    end
end
        
tt = [squeeze(XY(:,:,1));squeeze(XY(:,:,2));squeeze(XY(:,:,3));squeeze(XY(:,:,4));squeeze(XY(:,:,5));squeeze(XY(:,:,6))];
%}


