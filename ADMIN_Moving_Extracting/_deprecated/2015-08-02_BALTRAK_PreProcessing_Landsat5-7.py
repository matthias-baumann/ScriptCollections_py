import os
import time
from ZumbaTools._Raster_Tools import *
from ZumbaTools._FileManagement_Tools import *
import tarfile
import gdal, osr, ogr
from gdalconst import *
import numpy as np
import shutil
from multiprocessing import Pool
import gzip
# ############################################################################################################# #
def main():
# ####################################### SET TIME-COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOOTPRINTS ########################################################## #
# (1) GET LIST OF SCENES TO BE PROCESSED
    in_root = "G:/BALTRAK_NewScenes/"
 # (1) BUILD LIST WITH UNIQUE SCENE-id-PATHS
    processList = []
    PR_list = os.listdir(in_root)
    for PR in PR_list:
        PR_folder = in_root + PR + "/"
        sceneList = os.listdir(PR_folder)
        for scene in sceneList:
            scenePath = PR_folder + scene + "/"
            processList.append(scenePath)
    pool = Pool(processes=10)
    pool.map(WorkerFunction, processList)
    pool.close()
    pool.join()
# ####################################### END TIME-COUNT AND PRINT TIME STATS ################################# #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: ", starttime)
    print("end: ", endtime)
    print("")

def WorkerFunction(scenePaths):
    # ####################################### GLOBAL FUNCTIONS #################################################### #
    def Ctrans_MEM(inband_MEM, file_t_srs):
        # Function to convert into new coordinate system, for instructions, see http://jgomezdans.github.io/gdal_notes/reprojection.html
        def GetExtent(inband_MEM):
            # Get geotransform, get cols, get rows
            gt = inband_MEM.GetGeoTransform()
            cols = inband_MEM.RasterXSize
            rows = inband_MEM.RasterYSize
            # Get extent from gt und cols,rows.
            # found at http://gis.stackexchange.com/questions/57834/how-to-get-raster-corner-coordinates-using-python-gdal-bindings
            # Format is: [[UpperLeft],[LowerLeft],[LowerRight],[UpperRight]]
            ext=[]
            xarr=[0,cols]
            yarr=[0,rows]
            for px in xarr:
                for py in yarr:
                    x=gt[0]+(px*gt[1])+(py*gt[2])
                    y=gt[3]+(px*gt[4])+(py*gt[5])
                    ext.append([x,y])
                yarr.reverse()
            return ext
        def TransformCorners(extent, transformation):
            extent_transform = []
            for corner in extent:
                (x, y, z) = transformation.TransformPoint(corner[0], corner[1])
                corner_t = [x,y]
                extent_transform.append(corner_t)
            return extent_transform
        # (1) Define projection rule for output-projection
        # (1-1) Get properties from input-band
        cols = inband_MEM.RasterXSize
        rows = inband_MEM.RasterYSize
        inbands = inband_MEM.RasterCount
        in_proj = inband_MEM.GetProjection()
        in_geotrans = inband_MEM.GetGeoTransform()
        in_datatype = inband_MEM.GetRasterBand(1).DataType
        # (1-2) Get properties of projection to be projected into --> comes from file_t_srs
        s_srs_raster = gdal.Open(file_t_srs, GA_ReadOnly)
        out_proj = s_srs_raster.GetProjection()
        # (1-3) Build the coordinate transformation
        source_SR = osr.SpatialReference()
        source_SR.ImportFromWkt(in_proj)
        target_SR = osr.SpatialReference()
        target_SR.ImportFromWkt(out_proj)
        transgeo = osr.CoordinateTransformation(source_SR, target_SR)
        # (1-4) GET ALL FOUR CORNER COORDINATES OF THE IMAGE, transform, make largest new extent
        cornercords = GetExtent(inband_MEM)
        cornercords_t = TransformCorners(cornercords, transgeo)
        UL = [min([x[0] for x in cornercords_t]),max([x[1] for x in cornercords_t])]
        LR = [max([x[0] for x in cornercords_t]),min([x[1] for x in cornercords_t])]
        # (2-1) Generate new GeoTrans
        out_geotrans = (UL[0], 30.0, in_geotrans[2], UL[1], in_geotrans[4], -30.0)
        # (2-2) Update Number of cols and rows, which may be different after the coordinate transformation
        new_cols = int((LR[0] - UL[0]) / 30.0)
        new_rows = int((UL[1] - LR[1]) / 30.0)
        # (3) Generate output-file, and do the transformation
        drvMemR = gdal.GetDriverByName('MEM')
        out_MEM = drvMemR.Create('', new_cols, new_rows, inbands, in_datatype)
        out_MEM.SetProjection(out_proj)
        out_MEM.SetGeoTransform(out_geotrans)
        res = gdal.ReprojectImage(inband_MEM, out_MEM, source_SR.ExportToWkt(), target_SR.ExportToWkt(),
                                  gdal.GRA_NearestNeighbour)
        return out_MEM
    # ####################################### GLOBAL PATHS ######################################################## #
    out_root = "G:/BALTRAK_NewScenes_PP/"
    LedapsFmaskOut = "G:/BALTRAK_NewScenes_Ledaps/"
    ref_raster = "X:/Baltrak/02_Compositing_NEW/00_OutputData/PBC_container_BALTRAK_multiYear_2013-2015.bsq"
    # ####################################### START PROCESSING #################################################### #
    item = scenePaths # this line is the remnant from programming it first non-parallel
    # Get files of interest
    lndsr = [item + file for file in os.listdir(item) if file.startswith('lndsr') and file.find(".txt")<0]
    fmask = [item + file for file in os.listdir(item) if file.startswith('fmask')]
    # (1-1) COPY THE BANDS INTO MEMORY
    print("Copying files to memory, " + item)
    # --> from the hdf-file
    b1 = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:band1")
    b2 = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:band2")
    b3 = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:band3")
    b4 = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:band4")
    b5 = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:band5")
    b7 = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:band7")
    aot = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:atmos_opacity")
    acca_cloud = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:cloud_QA")
    acca_shadow = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:cloud_shadow_QA")
    acca_snow = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:snow_QA")
    thermal = OpenRasterToMemory('HDF4_EOS:EOS_GRID:' + lndsr[0] + ":Grid:band6")
    # --> fmask-file
    f_mask = OpenRasterToMemory(fmask[0])
    # --> Geometric image properties
    cols = b1.RasterXSize
    rows = b1.RasterYSize
    gt = b1.GetGeoTransform()
    proj = b1.GetProjection()
    drvMemR = gdal.GetDriverByName('MEM')
    # (1-2) CALCULATE ACTIVE AREA
    print("Active area, " + item)
    # Calculate active area
    def masking(band):
        cols = band.RasterXSize
        rows = band.RasterYSize
        b_array = band.ReadAsArray(0, 0, cols, rows)
        out_array = np.empty([rows, cols])
        np.putmask(out_array, b_array > 0, 1)
        return out_array
    b1_mask = masking(b1)
    b2_mask = masking(b2)
    b3_mask = masking(b3)
    b4_mask = masking(b4)
    b5_mask = masking(b5)
    b7_mask = masking(b7)
    mask = (b1_mask + b2_mask + b3_mask + b4_mask + b5_mask + b7_mask)/6
    aa = drvMemR.Create('', cols, rows, 1, GDT_Byte)
    aa.SetProjection(proj)
    aa.SetGeoTransform(gt)
    aa.GetRasterBand(1).WriteArray(mask, 0, 0)
    # Transform into new coordinate-system
    aa_trans = Ctrans_MEM(aa, ref_raster)
    # (1-3) LAYER STACKING
    print("Layer stacking, " + item)
    # convert -9999 values from input file to 0 in output file, do it on-the-fly with the function below
    def Convert9999to0(band, c, r):
        array = band.ReadAsArray(0, 0, c, r)
        mask = array
        np.putmask(mask, array == -9999, 0)
        return(mask)
    # --> stacking
    stack_mem = drvMemR.Create('', cols, rows, 6, 3)  # '3' is for 16-bit signed integer
    stack_mem.SetProjection(proj)
    stack_mem.SetGeoTransform(gt)
    stack_mem.GetRasterBand(1).WriteArray(Convert9999to0(b1, cols, rows), 0, 0)
    stack_mem.GetRasterBand(2).WriteArray(Convert9999to0(b2, cols, rows), 0, 0)
    stack_mem.GetRasterBand(3).WriteArray(Convert9999to0(b3, cols, rows), 0, 0)
    stack_mem.GetRasterBand(4).WriteArray(Convert9999to0(b4, cols, rows), 0, 0)
    stack_mem.GetRasterBand(5).WriteArray(Convert9999to0(b5, cols, rows), 0, 0)
    stack_mem.GetRasterBand(6).WriteArray(Convert9999to0(b7, cols, rows), 0, 0)
    # --> Transform into new coordinate-system
    stack_trans = Ctrans_MEM(stack_mem, ref_raster)
    stack_mem = None
    # (1-4) DISTANCE TO NADIR
    # Get active area file
    print("Nadir distance, " + item)
    aa_array = aa.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    # Get the upper left point of the area mas
    for row in range(rows):
        for col in range(cols):
            px_val = aa_array[row, col]
            if px_val == 1:
                UL = [row, col]
                break
        else:
            continue
        break
    # Get the lower left
    for col in range(cols):
        for row in reversed(range(rows)):
            px_val = aa_array[row, col]
            if px_val == 1:
                LL = [row, col]
                break
        else:
            continue
        break
    # Get the upper right point
    for col in reversed(range(cols)):
        for row in range(rows):
            px_val = aa_array[row, col]
            if px_val == 1:
                UR = [row, col]
                break
        else:
            continue
        break
    # Get the lower right point
    for row in reversed(range(rows)):
        for col in reversed(range(cols)):
            px_val = aa_array[row, col]
            if px_val == 1:
                LR = [row, col]
                break
        else:
            continue
        break
    # Get the x-coordinates for the nadir
    nadirTopX = (UR[1] + UL[1]) / 2
    nadirBottomX = (LR[1] + LL[1]) / 2
    # Get the nadirTopY
    for row in range(rows):
        px = aa_array[row, nadirTopX]
        if px == 1:
            nadirTopY = row
            break
    # Get the nadirBottomY
    for row in reversed(range(rows)):
        px = aa_array[row, nadirBottomX]
        if px == 1:
            nadirBottomY = row
            break
    # Write points into shapefile in Memory
    # Create shp-file with all properties
    drvMemV = ogr.GetDriverByName('Memory')
    shp_srs = osr.SpatialReference()
    shp_srs.ImportFromWkt(proj)
    shp_mem = drvMemV.CreateDataSource('')
    # Add nadirTop
    NT_x = nadirBottomX * gt[1] + gt[0] + (gt[1] / 2)
    NT_y = nadirBottomY * gt[5] + gt[3] + (gt[5] / 2)
    # Add nadirBottom
    NB_x = nadirTopX * gt[1] + gt[0] + (gt[1] / 2)
    NB_y = nadirTopY * gt[5] + gt[3] + (gt[5] / 2)
    # Write into shapefile
    lyr = shp_mem.CreateLayer('', shp_srs, ogr.wkbLineString)
    lyrDef = lyr.GetLayerDefn()
    fieldDefn = ogr.FieldDefn('ID', ogr.OFTInteger)
    lyr.CreateField(fieldDefn)
    line = ogr.Geometry(ogr.wkbLineString)
    line.AddPoint(NT_x, NT_y)
    line.AddPoint(NB_x, NB_y)
    feat = ogr.Feature(lyrDef)
    feat.SetGeometry(line)
    feat.SetField('ID', 1)
    lyr.CreateFeature(feat)
    # Create raster, rasterize line-shp
    nadir = drvMemR.Create('', cols, rows, 1, GDT_Byte)
    nadir.SetProjection(proj)
    nadir.SetGeoTransform(gt)
    rasterize = gdal.RasterizeLayer(nadir, [1], lyr, burn_values=[1])
    # CALCULATE DISTANCE TO NADIR
    # Create raster
    nadir_dis = drvMemR.Create('', cols, rows, 1, GDT_Int16)
    nadir_dis.SetProjection(proj)
    nadir_dis.SetGeoTransform(gt)
    nadir_dis_band = nadir_dis.GetRasterBand(1)
    nadir_band = nadir.GetRasterBand(1)
    # Set options and run the distance
    creationoptions = ['VALUES=1', 'DISTUNITS=PIXEL']
    gdal.ComputeProximity(nadir_band, nadir_dis_band, creationoptions)
    # Mask out active area
    nadir_dis_array = nadir_dis_band.ReadAsArray(0, 0, cols, rows)
    mask = aa.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    np.putmask(nadir_dis_array, mask == 1, nadir_dis_array)
    nadir_dis.GetRasterBand(1).WriteArray(nadir_dis_array, 0, 0)
    # --> Geo-Transform nadir-dis to new CS
    nadir_dis_trans = Ctrans_MEM(nadir_dis, ref_raster)
    # (1-5) ATMOSPHERIC OPTICAL THICKNESS
    print("AOT, " + item)
    aot_trans = Ctrans_MEM(aot, ref_raster)
    aot = None
    # (1-6) THERMAL INFRARED
    print("TIR, " + item)
    thermal_trans = Ctrans_MEM(thermal, ref_raster)
    thermal = None
    # (1-7) CLOUDMASK
    print("Cloud mask, " + item)
    cloud = drvMemR.Create('', cols, rows, 1, GDT_Byte)
    cloud.SetProjection(proj)
    cloud.SetGeoTransform(gt)
    # --> first stage: fmask output (values to mask: 2, 3, 4)
    fmask_cloudarray = f_mask.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    # --> second stage: ACCA
    acca_cloudarray = acca_cloud.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    acca_shadowarray = acca_shadow.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    acca_snowarray = acca_snow.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    # --> third stage: merge into single, combined cloudmask, fmask is basis
    outmask = fmask_cloudarray
    np.putmask(outmask, acca_cloudarray > 0, 40)
    np.putmask(outmask, acca_shadowarray > 0, 20)
    np.putmask(outmask, acca_snowarray > 0, 30)
    # --> write to file, transform coordinate system
    cloud.GetRasterBand(1).WriteArray(outmask, 0, 0)
    cloud_trans = Ctrans_MEM(cloud, ref_raster)
    # (1-8) CLOUD-DISTANCE
    print("Cloud distance, " + item)
    # Create file
    cloudist = drvMemR.Create('', cols, rows, 1, GDT_Int16)
    cloudist.SetProjection(proj)
    cloudist.SetGeoTransform(gt)
    # Load rasterbands from cloud and new clouddistfile, needed for distance operation
    cloudband = cloud.GetRasterBand(1)
    cloudist_band = cloudist.GetRasterBand(1)
    # calculate distance
    creationoptions = ['VALUES=2,3,4,20,30,40', 'DISTUNITS=PIXEL']
    gdal.ComputeProximity(cloudband, cloudist_band, creationoptions)
    # Mask out areas outside of active area
    clouddist_array = cloudist_band.ReadAsArray(0, 0, cols, rows)
    clouddist_mask = np.empty([rows, cols])
    mask = aa.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    np.putmask(clouddist_mask, mask == 1, clouddist_array)
    # Write outfile, transform to coordinate system
    cloudist.GetRasterBand(1).WriteArray(clouddist_mask, 0, 0)
    cloudist_trans = Ctrans_MEM(cloudist, ref_raster)
    # (1-9) WRITE NEW, PRE-PROCESSED FILES TO DISK
    print("Write files to disk, " + item)
    # Get information from MTL-File
    mtl_open = open([item + file for file in os.listdir(item) if file.endswith('MTL.txt')][0], "r")
    for line in mtl_open:
        if line.find("LANDSAT_SCENE_ID") >= 0:
            p = line.find('"')
            sceneID = line[p+1:-2]
            P = line[p+4:p+7]
            R = line[p+7:p+10]
            PR = P + R
        if line.find("DATE_ACQUIRED") >= 0:
            p = line.find("=")
            date_long = line[p+2:-1]
            date_short = date_long[2:4] + date_long[5:7] + date_long[8:10]
    mtl_open.close()
    # Generate-Filename-Prefix
    prefix = out_root + P + "_" + R + "/" + sceneID + "/" + PR + "_" + date_short + "_HERCULES_SR"
    # Create Output-folder and filenamePrefix
    out_folder = out_root + P + "_" + R + "/" + sceneID + "/"
    CreateFolder(out_folder)
    prefix = out_folder + PR + "_" + date_short + "_HERCULES_SR"
    # Write files to disk
    outDrv = gdal.GetDriverByName('ENVI')
    outDrv.CreateCopy(prefix + ".bsq", stack_trans)
    outDrv.CreateCopy(prefix + "_AA-mask.bsq", aa_trans)
    outDrv.CreateCopy(prefix + "_AOT.bsq", aot_trans)
    outDrv.CreateCopy(prefix + "_CMask.bsq", cloud_trans)
    outDrv.CreateCopy(prefix + "_CMask_Dist.bsq", cloudist_trans)
    outDrv.CreateCopy(prefix + "_Nadir_Dist.bsq", nadir_dis_trans)
    outDrv.CreateCopy(prefix + "_TIR.bsq", thermal_trans)
    # Compress new envi files
    print("Compress ENVI files, " + item)
    def CompressENVI(ENVIfilePath):
        # do gzip compression on ENVI-file
        # add in the last line of hdr file the line "file compression = 1"
        tmp_path = ENVIfilePath
        tmp_path = tmp_path.replace(".bsq","_tmp.bsq")
        f_in = open(ENVIfilePath, 'rb')
        f_out = gzip.open(tmp_path, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        # Delete old file
        os.remove(ENVIfilePath)
        # Rename new file, delete tmpfile
        os.rename(tmp_path, ENVIfilePath)
        # Add compression-info to hdr-file
        hdrpath = ENVIfilePath
        hdrpath = hdrpath.replace(".bsq", ".hdr")
        with open(hdrpath, 'a') as file:
            file.write("file compression = 1")
    CompressENVI(prefix + "_AA-mask.bsq")
    CompressENVI(prefix + "_AOT.bsq")
    CompressENVI(prefix + "_CMask.bsq")
    CompressENVI(prefix + "_CMask_Dist.bsq")
    CompressENVI(prefix + "_Nadir_Dist.bsq")
    CompressENVI(prefix + "_TIR.bsq")

    # Copy GCP, MTL
    GCP_in = [item + file for file in os.listdir(item) if file.endswith('GCP.txt')][0]
    GCP_out = prefix + "_GCP.txt"
    shutil.copy(GCP_in, GCP_out)
    MTL_in = [item + file for file in os.listdir(item) if file.endswith('MTL.txt')][0]
    MTL_out = prefix + "_MTL.txt"
    shutil.copy(MTL_in, MTL_out)

    # (2) TAR.GZ Ledaps/Fmask output
    print("Compress LEDAPS/Fmask output, " + item)
    def tar_gz(in_folder, out_file):
        fileList = os.listdir(in_folder)
        selection = ["lndsr", "fmask", "GCP", "MTL", "metadata"]
        # Only compress files that match the selection-criteria
        tar = tarfile.open(out_file, "w:gz")
        for file in fileList:
            if any(sel in file for sel in selection):
                compr = in_folder + file
                tar.add(compr, arcname = file)
        tar.close()
    # Create PathRow output folder
    pr_folder = LedapsFmaskOut + P + "_" + R + "/"
    CreateFolder(pr_folder)
    # Do tar-gz
    storeFile = pr_folder + sceneID + ".tar.gz"
    tar_gz(item, storeFile)

    # (3) REMOVE LEDAPS-FMASK FOLDER FROM DISK
    print("Remove LEDAPS/Fmask output, " + item)
    shutil.rmtree(item)


if __name__ == "__main__":
    main()