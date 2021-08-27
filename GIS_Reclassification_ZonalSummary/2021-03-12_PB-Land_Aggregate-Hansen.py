# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os, csv
import time
import gdal, osr, ogr
import numpy as np
import baumiTools as bt
from joblib import Parallel, delayed
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")
# ####################################### SET TIME-COUNT ###################################################### #
if __name__ == '__main__':
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES FOR PROCESSING ##################### #
    hansen = "Z:/Warfare/_Variables/Forest/"
    ramankutty = "P:/data/Ramankutty_Pot_Veg/potential_veg_type.tif"
    gerten = "P:/data/LPJmL/gerten_biomes_proj.tif"
    biome = "P:/data/Olson_2001_Ecoregions-of-the-world/raster/OLSON_BIOME_ID.tif"
    ecome = "P:/data/Olson_2001_Ecoregions-of-the-world/raster/OLSON_ECOME_ID.tif"
    nr_cores = 10
    outFolder = "P:/data/FL_resample/TH_25_v02/"
# ####################################### PROCESSING ########################################################## #
# (1) Build job list
    jobList = []
    # Get the name of the tiles in one of the folder
    tileNames = bt.baumiFM.GetFilesInFolderWithEnding(hansen+"Forest2000/", ".tif", fullPath=False)
    for tile in tileNames:
        size = os.path.getsize(hansen + "Forest2000/" + tile)
        if not size == 13320378:
            job = {'id': tile,
                   'forest': "Forest2000",
                   'loss': "LossYear",
                   'hans': hansen,
                   'raman': ramankutty,
                   'didi': gerten,
                   'biome': biome,
                   'ecome': ecome,
                   'out': outFolder}
            jobList.append(job)

# (2) Build Worker_Function
    def ResampleFunc(job):
        drvMemR = gdal.GetDriverByName('MEM')
    # Open the ramkutty layer, get information on the pixel size
        rm = gdal.Open(job['raman'])
        rm_pr = rm.GetProjection()
        rm_gt = rm.GetGeoTransform()
        rm_px = rm_gt[1]
    # Open hansen Forest2000 and lossYr
        f = bt.baumiRT.OpenRasterToMemory(job['hans'] + job['forest'] + "/" + job['id'])#"30S_120E.tif") #
        f_arr = f.GetRasterBand(1).ReadAsArray()

    # Make a check here: if there is no forest in here, skip this tile
        f_test = np.where(f_arr >= 5, 1, 0)
        if np.sum(f_test) < 1000:
            print("Skipping tile", job['id'], "because it does not contain forest")
        else:
            print("processing tile", job['id'])

            lYR = bt.baumiRT.OpenRasterToMemory(job['hans'] + job['loss'] + "/" + job['id'])#"30S_120E.tif") #
            LYR_arr = lYR.GetRasterBand(1).ReadAsArray()
        # Make a binary forest layer
            f_bin = np.where(f_arr >= 25, 1, 0) # edit later to 5
            f_bin_file = drvMemR.Create('', f.RasterXSize, f.RasterYSize, 1, gdal.GDT_Byte)
            f_bin_file.SetProjection(f.GetProjection())
            f_bin_file.SetGeoTransform(f.GetGeoTransform())
            f_bin_file.GetRasterBand(1).WriteArray(f_bin)

        # Create the dimensions for the output-file(s)
            f_gt = f.GetGeoTransform()
            maxX = f.RasterXSize * f_gt[1] + f_gt[0]
            minY = f.RasterYSize * f_gt[5] + f_gt[3]
            px_X = int((maxX - f_gt[0]) / rm_px)
            px_Y = int((f_gt[3] - minY) / rm_px)
            out_gt = (f_gt[0], rm_px, 0, f_gt[3], 0, -rm_px)
        # Build the output-File
            # b1: Ramankutty, b2: Gerten, b3: Olson ECOME, b4: Olson BIOME, b5: F2000, b6-24: F_loss
            outRas = drvMemR.Create('', px_X, px_Y, 24, gdal.GDT_UInt32)
            outRas.SetProjection(rm_pr)
            outRas.SetGeoTransform(out_gt)
            outArr = np.zeros((px_X, px_Y, 24))

        # Start resampling the layers and build the stack
        # (1) Forest
            warp_options = gdal.WarpOptions(outputType=gdal.GDT_UInt32, xRes=rm_px, yRes=rm_px,
                                            srcSRS=rm_pr, dstSRS=rm_pr,
                                            resampleAlg='sum',
                                            creationOptions=['COMPRESS=LZW'])
            F_res = drvMemR.Create('', px_X, px_Y, 1, gdal.GDT_UInt32)
            F_res.SetProjection(rm_pr)
            F_res.SetGeoTransform(out_gt)
            gdal.Warp(destNameOrDestDS=F_res, srcDSOrSrcDSTab=f_bin_file, options=warp_options)
            F_arr = F_res.GetRasterBand(1).ReadAsArray()
            F_arr1 = np.sum(F_arr)


            outArr[:,:,4] = F_res.GetRasterBand(1).ReadAsArray()
        # (2) Ramankutty
            inv_gt = gdal.InvGeoTransform(rm_gt)
            offsets_ul = gdal.ApplyGeoTransform(inv_gt, out_gt[0], out_gt[3])
            off_ul_x, off_ul_y = map(int, offsets_ul)
            raman_np = np.array(rm.GetRasterBand(1).ReadAsArray(off_ul_x, off_ul_y, px_X, px_Y))
            outArr[:, :, 0] = raman_np
        # (3) Gerten
            didi_ds = bt.baumiRT.OpenRasterToMemory(job['didi'])
            didi_out = drvMemR.Create('', px_X, px_Y, 1, gdal.GDT_Byte)
            didi_out.SetProjection(rm_pr)
            didi_out.SetGeoTransform(out_gt)
            warp_didi = gdal.WarpOptions(outputType=gdal.GDT_UInt32, xRes=rm_px, yRes=rm_px,
                                            srcSRS=rm_pr, dstSRS=rm_pr,
                                            resampleAlg='nearest',
                                            creationOptions=['COMPRESS=LZW'])
            gdal.Warp(destNameOrDestDS=didi_out, srcDSOrSrcDSTab=didi_ds, options=warp_didi)
            outArr[:, :, 1] = didi_out.GetRasterBand(1).ReadAsArray()
        # (4) Olson BIOME
            biome_ds = gdal.Open(job['biome'])
            inv_gt = gdal.InvGeoTransform(biome_ds.GetGeoTransform())
            offsets_ul = gdal.ApplyGeoTransform(inv_gt, out_gt[0], out_gt[3])
            off_ul_x, off_ul_y = map(int, offsets_ul)
            biome_np = np.array(biome_ds.GetRasterBand(1).ReadAsArray(off_ul_x, off_ul_y, px_X, px_Y))
            outArr[:, :, 2] = biome_np
        # (5) Olson ECOM
            eco_ds = gdal.Open(job['ecome'])
            inv_gt = gdal.InvGeoTransform(eco_ds.GetGeoTransform())
            offsets_ul = gdal.ApplyGeoTransform(inv_gt, out_gt[0], out_gt[3])
            off_ul_x, off_ul_y = map(int, offsets_ul)
            eco_np = np.array(eco_ds.GetRasterBand(1).ReadAsArray(off_ul_x, off_ul_y, px_X, px_Y))
            outArr[:, :, 3] = eco_np
        # (6) Yearly Forest loss
            for arrIndex, rasVal in enumerate(range(1, 19 + 1), start=5):
                #print(rasVal, arrIndex)
                # Build the mask based on the binary forest and the forest loss of that year
                fl_yr_bin = np.where(np.logical_and(LYR_arr == rasVal, f_bin == 1), 1, 0)
                # Write this into a file in memory
                lYR_bin_file = drvMemR.Create('', lYR.RasterXSize, lYR.RasterYSize, 1, gdal.GDT_Byte)
                lYR_bin_file.SetProjection(lYR.GetProjection())
                lYR_bin_file.SetGeoTransform(lYR.GetGeoTransform())
                lYR_bin_file.GetRasterBand(1).WriteArray(fl_yr_bin)
                # Resample
                lYR_res = drvMemR.Create('', px_X, px_Y, 1, gdal.GDT_UInt32)
                lYR_res.SetProjection(rm_pr)
                lYR_res.SetGeoTransform(out_gt)
                gdal.Warp(destNameOrDestDS=lYR_res, srcDSOrSrcDSTab=lYR_bin_file, options=warp_options)
                # Write into the correct array dimention
                outArr[:, :, arrIndex] = lYR_res.GetRasterBand(1).ReadAsArray()

        # (7) Write everything into the output-file
            # Create a set of bandnames
            bandNames = ["Ramankutty", "Gerten", "Olson_BIOME", "Olson_ECO", "F2000_25perc"]
            for yr in range(1, 19 + 1):
                string = "FL_" + str("{:02d}".format(yr))
                bandNames.append(string)
            # Now do the writing
            for arrIndex, band in enumerate(range(1,24+1), start=0):
                rb = outRas.GetRasterBand(band)
                rb.WriteArray(outArr[:,:,arrIndex])
                #print(bandNames[arrIndex])
                rb.SetDescription(bandNames[arrIndex])

        # Write output to disc
            bt.baumiRT.CopyMEMtoDisk(outRas, job['out'] + job['id'])

# (3) Execute the Worker_Funtion parallel
    #job_results = Parallel(n_jobs=nr_cores)(delayed(ResampleFunc)(i) for i in tqdm(jobList))
    for job in jobList:
       list = ResampleFunc(job)
    exit(0)

# (4) Merge tiles
    def BuildVRT(folder, outfile):
        fileList = bt.baumiFM.GetFilesInFolderWithEnding(folder, ".tif", fullPath=True)
        vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False)#, bandList=[35])
        vrt = gdal.BuildVRT(outfile, fileList, options=vrt_options)
        vrt = None
        return outfile
    BuildVRT(outFolder, "P:/data/FL_resample/TH25_v02☼_merged.vrt")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")