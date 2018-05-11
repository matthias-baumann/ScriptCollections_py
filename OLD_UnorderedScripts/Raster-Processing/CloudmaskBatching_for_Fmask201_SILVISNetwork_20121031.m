addpath('E:\kirkdata\mbaumann\Landsat_Processing\Fmask_2_1sav\');

mainDir = ('E:\kirkdata\mbaumann\Landsat_Processing\forLinux\');
cd(mainDir);
sz = size(dir,1)
nam = dir

n = 1
for i = 3:sz
   cd (strcat(mainDir,nam(i).name))
   temp = ls('*_Fmask_2_1_sav')   
      if size(temp,1) == 0 
         autoFmask_2_1sav(6,6,8)     %dilate cloud, shadow (9 pixels seemed to much)        
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

