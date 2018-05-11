import os
import time
from ZumbaTools.Raster_Tools import *
from ZumbaTools.FileManagement_Tools import *
import tarfile
import gdal, osr, ogr
from gdalconst import *
import numpy as np
import shutil
from multiprocessing import Pool
import gzip
#import xml.etree.ElementTree as ET
# ############################################################################################################# #
def main():
# ####################################### SET TIME-COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOOTPRINTS ########################################################## #
# (1) GET LIST OF SCENES TO BE PROCESSED
    in_root = "H:/Baltrak/Andrey/L57_RAW/"
 # (1) BUILD LIST WITH UNIQUE SCENE-id-PATHS
    processList = [(in_root + b) for b in os.listdir(in_root) if b.endswith("tar.gz")]
    pool = Pool(processes=15)
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
    item = scenePaths
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
    out_root = "H:/Baltrak/Andrey/01_ReprojectedScenes/Landsat57/"
    ref_raster = "H:/Baltrak/Andrey/00_Code/PythonForPreprocessing/LC81600232015093LGN00_sr_band2.tif"
    # ####################################### START PROCESSING #################################################### #
    print("Unzipping, " + item)
    def unzip(filePath):
        # Create output-path
        outpath = filePath
        outpath = outpath.replace(".tar.gz", "")
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        tar = tarfile.open(filePath, "r")
        list = tar.getnames()
        for file in tar:
            tar.extract(file, outpath)
        tar.close()
        return outpath
    folder = unzip(item)
    # Check if GCP file is available in 'folder'
    GCPtrue = 0
    fileList = os.listdir(folder)
    for file in fileList:
        if file.find("GCP") >= 0:
            GCPtrue = 1

    if GCPtrue == 0:
        print("No GCP-file, skiping")
        shutil.rmtree(folder)
    else:
        print("Copying files to memory, " + item)
        b1 = OpenRasterToMemory([(folder + "/" + b) for b in os.listdir(folder) if b.endswith("band1.tif")][0])
        b2 = OpenRasterToMemory([(folder + "/" + b) for b in os.listdir(folder) if b.endswith("band2.tif")][0])
        b3 = OpenRasterToMemory([(folder + "/" + b) for b in os.listdir(folder) if b.endswith("band3.tif")][0])
        b4 = OpenRasterToMemory([(folder + "/" + b) for b in os.listdir(folder) if b.endswith("band4.tif")][0])
        b5 = OpenRasterToMemory([(folder + "/" + b) for b in os.listdir(folder) if b.endswith("band5.tif")][0])
        b7 = OpenRasterToMemory([(folder + "/" + b) for b in os.listdir(folder) if b.endswith("band7.tif")][0])
        aot = OpenRasterToMemory([(folder + "/" + b) for b in os.listdir(folder) if b.endswith("opacity.tif")][0])
        thermal = OpenRasterToMemory([(folder + "/" + b) for b in os.listdir(folder) if b.endswith("band6.tif")][0])
        f_mask = OpenRasterToMemory([(folder + "/" + b) for b in os.listdir(folder) if b.endswith("cfmask.tif")][0])
        # --> Geometric image properties
        cols = b1.RasterXSize
        rows = b1.RasterYSize
        gt = b1.GetGeoTransform()
        proj = b1.GetProjection()
        drvMemR = gdal.GetDriverByName('MEM')
        # Create folder-structure for output-file from MTL
        # # get the name of the xml file as a character
        # Get information from MTL-File
        mtl_open = open([folder + "/" + file for file in os.listdir(folder) if file.endswith('MTL.txt')][0], "r")
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
        # Create Output-folder and filenamePrefix
        out_folder = out_root + P + "_" + R + "/" + sceneID + "/"
        CreateFolder(out_folder)
        prefix = out_folder + PR + "_" + date_short + "_AndreyKAZ_SR"
        # Copy GCP, MTL
        GCP_in = [folder + "/" + file for file in os.listdir(folder) if file.endswith('GCP.txt')][0]
        GCP_out = prefix + "_GCP.txt"
        shutil.copy(GCP_in, GCP_out)
        MTL_in = [folder + "/" + file for file in os.listdir(folder) if file.endswith('MTL.txt')][0]
        MTL_out = prefix + "_MTL.txt"
        shutil.copy(MTL_in, MTL_out)


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
        # Check if scene needs to be reprojected
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
        nadir_dis = None
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
        f_mask_trans = Ctrans_MEM(f_mask, ref_raster)
        # (1-8) CLOUDDISTANCE
        print("Cloud distance, " + item)
        # Create file
        cloudist = drvMemR.Create('', cols, rows, 1, GDT_Int16)
        cloudist.SetProjection(proj)
        cloudist.SetGeoTransform(gt)
        # Load rasterbands from cloud and new clouddistfile, needed for distance operation
        fmask_band = f_mask.GetRasterBand(1)
        cloudist_band = cloudist.GetRasterBand(1)
        # calculate distance
        creationoptions = ['VALUES=2,3,4', 'DISTUNITS=PIXEL']
        gdal.ComputeProximity(fmask_band, cloudist_band, creationoptions)
        # Mask out areas outside of active area
        clouddist_array = cloudist_band.ReadAsArray(0, 0, cols, rows)
        clouddist_mask = np.empty([rows, cols])
        mask = aa.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
        np.putmask(clouddist_mask, mask == 1, clouddist_array)
        # Write outfile, transform to coordinate system
        cloudist.GetRasterBand(1).WriteArray(clouddist_mask, 0, 0)
        cloudist_trans = Ctrans_MEM(cloudist, ref_raster)
        cloudist = None
        # (1-9) WRITE NEW, PRE-PROCESSED FILES TO DISK
        print("Write files to disk, " + item)
        outDrv = gdal.GetDriverByName('ENVI')
        outDrv.CreateCopy(prefix + ".bsq", stack_trans)
        outDrv.CreateCopy(prefix + "_AA-mask.bsq", aa_trans)
        outDrv.CreateCopy(prefix + "_AOT.bsq", aot_trans)
        outDrv.CreateCopy(prefix + "_CMask.bsq", f_mask_trans)
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

        # (3) REMOVE LEDAPS-FMASK FOLDER FROM DISK
        print("Remove unzipped folder")
        shutil.rmtree(folder)


if __name__ == "__main__":
    main()