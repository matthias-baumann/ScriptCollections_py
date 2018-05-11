addpath('X:\Processing\fmask\Fmask_1_6_3sav');

mainDir = ('X:\Processing\ledaps\_processed\processed_ca1995\');
cd(mainDir);
sz = size(dir,1)
nam = dir

n = 1
for i = 3:sz
   cd (strcat(mainDir,nam(i).name))
   temp = ls('*_MTLFmask_1_6_3sav')   %_MTLFmask_1_6_3sav
      if size(temp,1) == 0 
         autoFmask_1_6sav(6,6,10)     %dilate cloud, shadow (9 pixels seemed to much)
      end
   n = n+1
   nam(i).name
   %count=char(n);
   %count=cast(n,string)
   %count = num2string(n)
   %strcat(count,' -->files processed')
   %strcat(num2string(n,' -->files processed')
end
 
%n
    %ls('lndsr.*.hdf')

