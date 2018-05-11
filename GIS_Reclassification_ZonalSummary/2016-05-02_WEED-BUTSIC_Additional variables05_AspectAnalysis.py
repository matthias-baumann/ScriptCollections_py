# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, osr
from ZumbaTools._Vector_Tools import *
from ZumbaTools._Raster_Tools import *
import csv
import gdal
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
outFile = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/SummaryDataset_V05_PercentFacingSouth_20160502.csv"
skipIDs = ["05315125"]
# ####################################### OPEN FILES, BUILD COORDINATE TRANSFORMATION ######################### #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
parcel = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/00_Parcel.shp"),'')
ocean = drvMemR.CreateCopy('',gdal.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/DEM_Humboldt_aspect.tif"))
#ocean = gdal.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/DistanceToOcean_5m.tif")
gt = ocean.GetGeoTransform()
pr = ocean.GetProjection()
cols = ocean.RasterXSize
rows = ocean.RasterYSize
parcelLYR = parcel.GetLayer()
# Build the coordinate transformation
pol_srs = parcelLYR.GetSpatialRef()
ras_srs = ocean.GetProjection()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(ras_srs)
transform = osr.CoordinateTransformation(pol_srs, target_SR)

# ####################################### GET THE FIRST FEATURE OF THE ZONE-FILE, THEN LOOP ################### #
outList = []
header = ["APN", "S_Per", "SW-S_Per", "S-SE_Per", "SW-S-SE_Per"]
outList.append(header)
zone_feat = parcelLYR.GetNextFeature()
while zone_feat:
    #### Check if object in skipList
    ID = zone_feat.GetField("APN")
    if not ID in skipIDs:
        print("Processing APN " + str(ID))
    # Append value
        vals = []
        vals.append(ID)
    # Get the Geometry, make clone
        geom = zone_feat.GetGeometryRef()
# Transform (here not necessary, as the two files have the same coordinate system)
        geom.Transform(transform)
# Create new SHP-file in memory to which we copy the geometry
        shpMem = drvMemV.CreateDataSource('')
        shpMem_lyr = shpMem.CreateLayer('shpMem', target_SR, geom_type = ogr.wkbMultiPolygon)
        shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
        shpMem_feat = ogr.Feature(shpMem_lyr_defn)
        shpMem_feat.SetGeometry(geom.Clone())
        shpMem_lyr.CreateFeature(shpMem_feat)
# Load new SHP-file into array
        x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
        x_res = int((x_max - x_min) / 5)
        y_res = int((y_max - y_min) / 5)
# Polygon has to be at least one pixel wide or long
        if x_res > 0 and y_res > 0:
            shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
            shpMem_asRaster.SetProjection(ras_srs)
            shpMem_asRaster.SetGeoTransform((x_min, 5, 0, y_max, 0, -5))
            shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
            shpMem_asRaster_b.SetNoDataValue(0)
            gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
            shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
            #CopyMEMtoDisk(shpMem_asRaster, "D:/shp.tif")
# Subset the classification raster and load it into the array
            rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, gdal.GDT_Float32)
            rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
            rasMem.SetProjection(shpMem_asRaster.GetProjection())
            gdal.ReprojectImage(ocean, rasMem, pr, shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
            rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
            #CopyMEMtoDisk(rasMem, "D:/dist.tif")
# Now mask out the areas outside (shpMem_array = 0), then do the evaluation
            percList = []
            inBuff_array = rasMem_array
            np.putmask(inBuff_array, shpMem_array == 0, 0)
            unique, counts = np.unique(inBuff_array, return_counts=True)
            hist = np.asarray((unique, counts)).T
            allPX = np.sum(hist, axis=0)[1]
        # South Only --> 157.5 - 202.5
            sumS = 0
            for i in hist:
                if i[0] >= 157.5 and i[0] <= 202.5:
                    sumS = sumS + i[1]
            sumS_perc = sumS/allPX
            percList.append(sumS_perc)
        # SW-S --> 157.5 - 247.5
            sumSSW = 0
            for i in hist:
                if i[0] >= 157.5 and i[0] <= 247.5:
                    sumSSW = sumSSW + i[1]
            sumSSW_perc = sumSSW/allPX
            percList.append(sumSSW_perc)
        # S-SE --> 112.5-202.5
            sumSSE = 0
            for i in hist:
                if i[0] >= 112.5 and i[0] <= 202.5:
                    sumSSE = sumSSE + i[1]
            sumSSE_perc = sumSSE/allPX
            percList.append(sumSSE_perc)
        # SW-S-SE --> 112.5-247.5
            sumSSESW = 0
            for i in hist:
                if i[0] >= 112.5 and i[0] <= 247.5:
                    sumSSESW = sumSSESW + i[1]
            sumSSESW_perc = sumSSESW/allPX
            percList.append(sumSSESW_perc)
        else:
            percList = ["NA", "NA", "NA", "NA"]

        for p in percList:
            vals.append(p)
# Add the values to the output-list, go to next feature
        outList.append(vals)
        zone_feat = parcelLYR.GetNextFeature()
    else:
        zone_feat = parcelLYR.GetNextFeature()


# Write output-file
print("Write output")
with open(outFile, "w") as theFile:
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