# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os, csv
import time
import gdal, osr, ogr
import numpy as np
import baumiTools as bt
from joblib import Parallel, delayed
from tqdm import tqdm
import warnings
import math
warnings.filterwarnings("ignore")
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES FOR PROCESSING ##################### #
LC_tiles = "G:/Baumann/_ANALYSES/AnnualLandCoverChange_CHACO-CHIQUI_EarthEngine/01_F_C_P_OV_O/05_MapProducts/Run10/output_LandCover/"
vrt = "G:/Baumann/_ANALYSES/AnnualLandCoverChange_CHACO-CHIQUI_EarthEngine/01_F_C_P_OV_O/05_MapProducts/Run10/output_LandCover.vrt"
shp = bt.baumiVT.CopyToMem("G:/Baumann/OneDrive - Conservation Biogeography Lab/_RESEARCH/Publications/Publications-in-preparation/Torres-etal_Peccari-Habitat-LandCover/New_Analysis/occurrences_2kmBuff.shp")
out = "G:/Baumann/OneDrive - Conservation Biogeography Lab/_RESEARCH/Publications/Publications-in-preparation/Torres-etal_Peccari-Habitat-LandCover/New_Analysis/occurrences_2kmBuff_summaries.csv"
# ####################################### FUNTIONS ############################################################ #
def BuildVRT(folder, outfile):
    fileList = bt.baumiFM.GetFilesInFolderWithEnding(folder, ".tif", fullPath=True)
    vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False)  # , bandList=[35])
    vrt = gdal.BuildVRT(outfile, fileList, options=vrt_options)
    vrt = None
    return outfile

def Geom_Raster_to_np(geom, raster, band):
    '''
    Function that takes a geometry from a polygon shapefile and a rasterfile, and returns both features as 2d-arryas
    in the size of the geom --> can be later used for masking.
    Function does a coordinate transformation implicitely!

    PARAMETERS
    -----------
    geom : geom object (required)
        geometry of the feature
    raster: gdal object (required)
        raster as a gdal-object (through gdal.Open())
    band: integer (required)
        the band value to take from the raster

    RETURNS
    -------
    Two numpy-arrays
    (1) np-array of the geometry as binary feature --> values inside the geometry have value '1', values outside '0'
    (2) np-array of the raster in the same size (i.e., as a subset of the raster) of the geometry

    '''
    # Make a coordinate transformation of the geom-srs to the raster-srs
    #pol_srs = geom.GetSpatialReference()
    #print(pol_srs)
    #ras_srs = raster.GetProjection()
    #print(ras_srs)
    #exit(0)
    #target_SR = osr.SpatialReference()
    #target_SR.ImportFromWkt(ras_srs)
    #srs_trans = osr.CoordinateTransformation(pol_srs, target_SR)
    #geom.Transform(srs_trans)
    # Create a memory shp/lyr to rasterize in
    geom_shp = ogr.GetDriverByName('Memory').CreateDataSource('')
    geom_lyr = geom_shp.CreateLayer('geom_shp', srs=geom.GetSpatialReference())
    geom_feat = ogr.Feature(geom_lyr.GetLayerDefn())
    geom_feat.SetGeometryDirectly(ogr.Geometry(wkt=str(geom)))
    geom_lyr.CreateFeature(geom_feat)
    # Rasterize the layer, open in numpy
    #bt.baumiVT.CopySHPDisk(geom_shp, "D:/baumamat/Warfare/_Variables/Forest/_tryout.shp")
    x_min, x_max, y_min, y_max = geom.GetEnvelope()
    gt = raster.GetGeoTransform()
    pr = raster.GetProjection()
    x_res = math.ceil((abs(x_max - x_min)) / gt[1])
    y_res = math.ceil((abs(y_max - y_min)) / gt[1])
    new_gt = (x_min, gt[1], 0, y_max, 0, -gt[1])
    lyr_ras = gdal.GetDriverByName('MEM').Create('', x_res, y_res, 1, gdal.GDT_Byte)
    #lyr_ras.GetRasterBand(1).SetNoDataValue(0)
    lyr_ras.SetProjection(pr)
    lyr_ras.SetGeoTransform(new_gt)
    gdal.RasterizeLayer(lyr_ras, [1], geom_lyr, burn_values=[1], options = ['ALL_TOUCHED=TRUE'])
    geom_np = np.array(lyr_ras.GetRasterBand(1).ReadAsArray())
    # Now load the raster into the array --> only take the area that is 1:1 the geom-layer (see Garrard p.195)
    inv_gt = gdal.InvGeoTransform(gt)
    offsets_ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)
    off_ul_x, off_ul_y = map(int, offsets_ul)
    raster_np = np.array(raster.GetRasterBand(band).ReadAsArray(off_ul_x, off_ul_y, x_res, y_res))
    ## Just for checking if the output is correct --> write it to disc. Outcommented here
    val_ras = gdal.GetDriverByName('MEM').Create('', x_res, y_res, 1, gdal.GDT_UInt16)
    val_ras.SetProjection(pr)
    val_ras.SetGeoTransform(new_gt)
    val_ras.GetRasterBand(1).WriteArray(raster_np, 0, 0)
    #bt.baumiRT.CopyMEMtoDisk(lyr_ras, "G:/Baumann/_ANALYSES/AnnualLandCoverChange_CHACO-CHIQUI_EarthEngine/01_F_C_P_OV_O/05_MapProducts/Run10/geom.tif")
    #bt.baumiRT.CopyMEMtoDisk(val_ras, "G:/Baumann/_ANALYSES/AnnualLandCoverChange_CHACO-CHIQUI_EarthEngine/01_F_C_P_OV_O/05_MapProducts/Run10/raster.tif")
    #exit(0)
    return geom_np, raster_np

# ####################################### PROCESSING ########################################################## #
# (1) Merge tiles
vrt = BuildVRT(LC_tiles, vrt)
ras = gdal.Open(vrt)
# (2) Create output
outList = [["ID", "Year", "WL_km2", "ONV_km2", "C_km2", "P_km2"]]
# (3) Open the layer
lyr = shp.GetLayer()
feat = lyr.GetNextFeature()
while feat:
    # Get the field ID
    id = feat.GetField("ID")
    print("Processing ID:", str(id))
    geom = feat.GetGeometryRef()
    geom_cl = geom.Clone()
    # Loop through the years
    for band, year in enumerate(range(1985, 2019+1), start=1):
        print(year)
        # Get the np arrays
        geom_np, ras_np = Geom_Raster_to_np(geom_cl, ras, band)
        # Woodland
        wl_km2 = np.where(np.logical_and(geom_np==1, ras_np==1), 1, 0).sum()
        wl_km2 = wl_km2 * 30 * 30 / 1000000
        # ONV
        onv_km2 = np.where(np.logical_and(geom_np==1, ras_np==2), 1, 0).sum()
        onv_km2 = onv_km2 * 30 * 30 / 1000000
        # C
        c_km2 = np.where(np.logical_and(geom_np == 1, ras_np == 3), 1, 0).sum()
        c_km2 = c_km2 * 30 * 30 / 1000000
        # P
        p_km2 = np.where(np.logical_and(geom_np == 1, ras_np == 4), 1, 0).sum()
        p_km2 = p_km2 * 30 * 30 / 1000000
        # append to output
        outList.append([id, year, wl_km2, onv_km2, c_km2, p_km2])
    # Get the next feature
    feat = lyr.GetNextFeature()

# Write things to output
print("Write output")
with open(out, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in outList:
        writer.writerow(element)


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")