# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr, osr
import csv
import baumiTools as bt
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES FOR PROCESSING ##################### #
rootFolder = "D:/OneDrive - Conservation Biogeography Lab/_RESEARCH/Publications/Commented_manuscripts/2020_Munteanu_Grazing_Corona_DataProcessingOnly/"
points = bt.baumiVT.CopyToMem(rootFolder + "sample_dates.shp")
out_file = rootFolder + "sample_dates_values_2020-09-22.csv"
raster = gdal.Open("L:/_DATA_ACCEPTED_PAPERS/2020_Dara_RSE/Data/Maps/Grazing_pressure.img")
# ####################################### START PROCESSING #################################################### #
#### (1) INSTANTIATE OUTPUT
valueList = [["Point_ID", "Year", "GP_mean", "GP_median", "GP_max", "GP_min", "GP_SD", "GP_centroid"]]

#### (2) OPEN THE LAYER; BUILD CS-rule, get px-size
lyr = points.GetLayer()
sourceSR = lyr.GetSpatialRef()
sourceSR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
targetSR = osr.SpatialReference()
targetSR.ImportFromWkt(raster.GetProjection())
targetSR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
srs_trans = osr.CoordinateTransformation(sourceSR, targetSR)
raster_gt = raster.GetGeoTransform()
pxSize = raster_gt[1]

#### (3) START LOOPING OVER THE ELEMENTS IN THE SHAPEFILE
feat = lyr.GetNextFeature()
while feat:
    # Get the geometry, apply the geo-transformation
    pointID = feat.GetField('ID')
    print("Processing ID:", str(pointID))
    geom = feat.GetGeometryRef()
    geom_cl = geom.Clone()
    geom_cl.Transform(srs_trans)
    # Build a memory raster from the new geometry
    geom_shp = ogr.GetDriverByName('Memory').CreateDataSource('')
    geom_lyr = geom_shp.CreateLayer('geom', targetSR, geom_type=ogr.wkbMultiPolygon)
    geom_lyrDefn = geom_lyr.GetLayerDefn()
    geom_feat = ogr.Feature(geom_lyrDefn)
    geom_feat.SetGeometry(geom_cl)
    geom_lyr.CreateFeature(geom_feat)
    #bt.baumiVT.CopySHPDisk(geom_shp, rootFolder + "px.shp")
    # Calculate the extent of the polygon, so that we know how large the raster should become
    x_min, x_max, y_min, y_max = geom_lyr.GetExtent()
    x_res = int((x_max - x_min) / pxSize)
    y_res = int((y_max - y_min) / pxSize)
    # Create an empty raster, and rasterize the geometry into it
    geom_ras = gdal.GetDriverByName('MEM').Create('', x_res, y_res, gdal.GDT_Byte)
    geom_ras.SetProjection(targetSR.ExportToWkt())
    geom_ras.SetGeoTransform((x_min, pxSize, 0, y_max, 0, -pxSize))
    gdal.RasterizeLayer(geom_ras, [1], geom_lyr, burn_values=[1])
    #bt.baumiRT.CopyMEMtoDisk(geom_ras, rootFolder + "geom_ras.tif")
    geom_np = np.array(geom_ras.GetRasterBand(1).ReadAsArray())
    # calculate the offsets of the smaller array in comparsion to the large array
    inv_gt = gdal.InvGeoTransform(raster_gt)
    offsets_ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)
    off_ul_x, off_ul_y = map(int, offsets_ul)
    # Now loop over the bands, and calculate the values
    for year, index in enumerate(range(raster.RasterCount), start=1985):
        #print(year, index+1)
        # Load the array
        band_arr = raster.GetRasterBand(index+1).ReadAsArray(off_ul_x, off_ul_y, x_res, y_res)
        # calculate the array statistics
        #mean = np.mean(band_arr[geom_np == 1])
        mean = round(band_arr[geom_np == 1].mean(), 4)
        median = round(np.median(band_arr[geom_np == 1]), 4)
        max = round(np.max(band_arr[geom_np == 1]), 4)
        min = round(np.min(band_arr[geom_np == 1]), 4)
        sd = round(np.std(band_arr[geom_np == 1]), 4)
        # calculate the value at the centroid
        center = geom_cl.Centroid()
        px = int((center.GetX() - raster_gt[0]) / raster_gt[1])
        py = int((center.GetY() - raster_gt[3]) / raster_gt[5])
        centroid = raster.GetRasterBand(index+1).ReadAsArray(px, py, 1, 1)
        # Append to output
        valueList.append([pointID, year, mean, median, max, min, sd, round(centroid[0,0], 4)])
    # Get the next feature
    feat = lyr.GetNextFeature()

#### (4) WRITE VALUES TO DISC
print("Write output")
with open(out_file, "w") as theFile:
    csv.register_dialect("custom", delimiter=";", skipinitialspace=True, lineterminator='\n')
    writer = csv.writer(theFile, dialect="custom")
    for element in valueList:
        writer.writerow(element)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)