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
outFile = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/SummaryDataset_V04_Stream_20160428.csv"
skipIDs = ["05315125", "51313108"]
# ####################################### OPEN FILES, BUILD COORDINATE TRANSFORMATION ######################### #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
parcel = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/00_Parcel.shp"),'')
stream = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/11_Streams_AllDissolve_1.shp"),'')
streamfield = "Id"
#streamDist = drvMemR.CreateCopy('',gdal.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/11_Streams_DistanceToStream_15m.tif"))
streamDist = drvMemR.CreateCopy('',gdal.Open("D:/test2.tif"))
parcelLYR = parcel.GetLayer()
streamLYR = stream.GetLayer()
# Build the coordinate transformation
streamLYR_SR = streamLYR.GetSpatialRef()
parcelLYR_SR = parcelLYR.GetSpatialRef()
ras_srs = streamDist.GetProjection()
transform = osr.CoordinateTransformation(parcelLYR_SR, streamLYR_SR)
# ####################################### CREATE THE OUTPUT-LISTS, ADD VARIABLE NAMES FIRST ################# #
outList = []
header = ["APN", "Dist"]
#streamFeat = streamLYR.GetNextFeature()
#while streamFeat:
#    name = "y_" + str(streamFeat.GetField(streamfield))
#    header.append(name)
#    thpFeat = streamLYR.GetNextFeature()
#streamLYR.ResetReading()
outList.append(header)
# ####################################### LOOP THROUGH PARCELS ############################################## #
parcelFeat = parcelLYR.GetNextFeature()
while parcelFeat:
# Get APN identifier, check if in skip-feature
    ID = parcelFeat.GetField("APN")
    if not ID in skipIDs:
        print("Processing APN " + str(ID))
        vals = []
        vals.append(ID)
# Get the Geometry of the feature, transform to stream-coordinate systems
        geomParcel = parcelFeat.GetGeometryRef()
        geomParcel.Transform(transform)
# Now loop through the features of the stream layer
        streamFeat = streamLYR.GetNextFeature()
        while streamFeat:
            geomStream = streamFeat.GetGeometryRef()
            intersection = geomParcel.Intersection(geomStream)
# Check if the intersection is of length > 0 (= stream goes through parcel), if so, then value is 0, otherwise calculate mean distance
            if intersection.Length() > 0:
                vals.append(0)
            else:
    # Build shp-file in memory from geom_zone
                target_SR = osr.SpatialReference()
                target_SR.ImportFromWkt(streamDist.GetProjection())
                shpMem = drvMemV.CreateDataSource('')
                shpMem_lyr = shpMem.CreateLayer('shpMem', target_SR, geom_type = ogr.wkbMultiPolygon)
                shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
                shpMem_feat = ogr.Feature(shpMem_lyr_defn)
                shpMem_feat.SetGeometry(geomParcel)
                shpMem_lyr.CreateFeature(shpMem_feat)
    # Load new SHP-file into array
                x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
                x_res = int((x_max - x_min) / 11)
                y_res = int((y_max - y_min) / 11)
                if x_res > 0 and y_res > 0:
                    shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
                    shpMem_asRaster.SetProjection(ras_srs)
                    shpMem_asRaster.SetGeoTransform((x_min, 11, 0, y_max, 0, -11))
                    shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
                    shpMem_asRaster_b.SetNoDataValue(0)
                    gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
                    shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
    # Subset the distance raster and load it into the array
                    rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, gdal.GDT_Float32)
                    rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
                    rasMem.SetProjection(shpMem_asRaster.GetProjection())
                    gdal.ReprojectImage(streamDist, rasMem, ras_srs, shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
                    rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
                    mean = np.mean(rasMem_array)
# Now mask out the areas outside (shpMem_array = 0)
                    inBuff_array = rasMem_array
                    np.putmask(inBuff_array, shpMem_array == 0, 0)
                    meanDist = np.mean(inBuff_array)
                    vals.append(meanDist)
                else:
                    meanDist = "NA"
                    vals.append(meanDist)
            streamFeat = streamLYR.GetNextFeature()
# Append vals to outlist, reset reading of THP-Layer
        outList.append(vals)
        streamLYR.ResetReading()
        parcelFeat = parcelLYR.GetNextFeature()
    else:
        parcelFeat = parcelLYR.GetNextFeature()


# ####################################### WRITE OUTPUT ################################################## #
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