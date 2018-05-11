pro stack_tm_imgs_and_organize_in_folders

;assumes all input tiff bands have same extent, projection, pixelsize etc.
;expects root dir to be named accoring to the compressed directors, e.g. LT51830281995151XXX01.tar is /LT51830281995151XXX01/
;has to be executed on server due to memory allocation restrictions on desktop PCs

;USER: provide path to directory containing single band tiff files

path = 'R:\daten\images\carpathians\landsat\+Download+\pg\184028\LT51840282009196MOR00\'
files = file_search(path + '*.tif', count=n_files)
all_files = file_search(path + '*')

if n_files eq 0 then begin
	print, 'No Tiff files found! Cancelling...'
	return
endif

;set bandn variables to individual resuts of file search
band1 = files[0]
band2 = files[1]
band3 = files[2]
band4 = files[3]
band5 = files[4]
band7 = files[6]
;***********************************************************************************************
;create base output directories and complete output path and name!
root_dir = strjoin( (strsplit(band1,'\',/EXTRACT))[0:8] ,'\')
;The EXTRACT keyword can be used to cause STRSPLIT to return an array containing the substrings
tmp = file_basename(band1)
subdir = strmid(tmp, 2,7) + strmid(tmp, 12,9) + 'L1T'
base_dir_path = filepath('',ROOT_DIR=root_dir,SUBDIRECTORY=subdir)
dir_array = ['geometrically corrected', 'radiometrically corrected', 'raw']
mypath_array = base_dir_path+dir_array
file_mkdir,mypath_array
stack_dir = base_dir_path + dir_array(0) + '\'
stack_dir_name = stack_dir + subdir + '.img'
raw_dir_path = base_dir_path + dir_array(2) + '\'
;***********************************************************************************************

dimss = lonarr(5, n_files)
fids = lonarr(n_files)
bnamess = strarr(n_files)
poss = lonarr(n_files)

for i_files=0,n_files-1 do begin
	envi_open_file, files[i_files], r_fid=i_fid
	fids[i_files]=i_fid
	envi_file_query, i_fid, dims=i_dims
	dimss[*,i_files]=i_dims			;alternativ [i,0:4]
	poss[i_files]=0
	bnamess[i_files]='band '+strmid(file_basename(files(i_files)),22,1)
endfor

;(!)laufvariable [i_files]
;example band name --> L5183028_02819910909_B10.TIF
;generic band names --> bnamess[i_files]='band ' + string(i_files)	; strmid

;only bands 1-5 and 7
index = [0,1,2,3,4,6]
dimss = dimss[*,index]
fids = fids[index]
bnamess = bnamess[index]
poss = poss[index]

out_proj = envi_get_projection(fid=fids[0],pixel_size=out_ps)

ENVI_DOIT, 'ENVI_LAYER_STACKING_DOIT',DIMS=dimss,/exclusive, $
  FID=fids, /IN_MEMORY,$
  INTERP=1, OUT_BNAME=bnamess, $
  out_ps=out_ps,out_proj=out_proj,pos=poss,$
  OUT_DT=1,R_FID=rfid

envi_file_query,rfid,dims=dims,ns=ns

ENVI_OUTPUT_TO_EXTERNAL_FORMAT,DIMS=dims,FID=rfid,$
         OUT_BNAME=bnamess, $
         OUT_NAME=stack_dir_name,/imagine

;move all generic files to 'raw' directory
file_move, all_files, raw_dir_path

end
