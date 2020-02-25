# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os, csv
import time
import gdal, osr, ogr
from tqdm import tqdm
import numpy as np
import baumiTools as bt
import math
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
rootFolder = "P:/"
eco_shp = bt.baumiVT.CopyToMem("D:/baumamat/wwf_terr_ecos_roughDissolve.shp")
out_csv = "D:/baumamat/wwf_terr_ecos_roughDissolve/areaSummaries_ALL_20190122.csv"
forest = gdal.Open("D:/baumamat/Warfare/_Variables/Forest/Forest2000.vrt")
gain = gdal.Open("D:/baumamat/Warfare/_Variables/Forest/Gain.vrt")
loss = gdal.Open("D:/baumamat/Warfare/_Variables/Forest/LossYear.vrt")
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
epsg_to = 54009 # Mollweide
# ####################################### PROCESSING ########################################################## #
# Get layer of the ecoregions / intersections
eco_lyr = eco_shp.GetLayer()
# Create coordinate transformation rule
eco_SR = eco_lyr.GetSpatialRef()
target_SR = osr.SpatialReference()
target_SR.ImportFromEPSG(epsg_to)
trans = osr.CoordinateTransformation(eco_SR, target_SR)
# Build the output-list
outDS = [["UID", "baumi_ID",
          "F2000_km_th25", "F2000_km_th40", "FL2001_km", "FL2002_km", "FL2003_km", "FL2004_km", "FL2005_km",
          "FL2006_km", "FL2007_km", "FL2008_km", "FL2009_km", "FL2010_km", "FL2011_km", "FL2012_km","FL2013_km",
          "FL2014_km", "FL2015_km", "FL2016_km", "FL2017_km", "FL2018_km"]]
#for eco_feat in tqdm(eco_lyr):
eco_feat = eco_lyr.GetNextFeature()
while eco_feat:
# Get needed properties from the SHP-File, the take geometry, and transform to Target-EPSG
    ecoID = int(eco_feat.GetField("baumi"))
    print(ecoID)
    if not ecoID == 1:
        vals = [ecoID]
        ecoGEOM = eco_feat.GetGeometryRef()
        ecoGEOM.Transform(trans)
    # RASTERIZING THE GEOMETRY
        # Create new SHP-file in memory to which we copy the geometry
        ecoGEOM_shp = drvMemV.CreateDataSource('')
        ecoGEOM_lyr = ecoGEOM_shp.CreateLayer('ecoGEOM', target_SR, geom_type=ogr.wkbMultiPolygon)
        ecoGEOM_lyr_defn = ecoGEOM_lyr.GetLayerDefn()
        ecoGEOM_feat = ogr.Feature(ecoGEOM_lyr_defn)
        ecoGEOM_feat.SetGeometry(ecoGEOM)
        ecoGEOM_lyr.CreateFeature(ecoGEOM_feat)
        # Check if the geometry we are processing is larger than 1x1 pixel
        x_min, x_max, y_min, y_max = ecoGEOM_lyr.GetExtent()
        x_res = int((x_max - x_min) / 30)
        y_res = int((y_max - y_min) / 30)
        # Do the rest of the operation for this polygon only if x_res and y_res are >= 1
        if x_res > 0 and y_res > 0:
            ecoGEOM_ras = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
            ecoGEOM_ras.SetProjection(target_SR.ExportToWkt())
            ecoGEOM_ras.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
            ecoGEOM_rb = ecoGEOM_ras.GetRasterBand(1)
            ecoGEOM_rb.SetNoDataValue(255)
            gdal.RasterizeLayer(ecoGEOM_ras, [1], ecoGEOM_lyr, burn_values=[1])
            # Reproject the Hansen-Raster "into" the geometry-raster (ecoGEOM_ras)
            def ReprojectRaster(valRaster, GEOMraster):
                vasRaster_sub = drvMemR.Create('', GEOMraster.RasterXSize, GEOMraster.RasterYSize, 1, gdal.GDT_Byte)
                vasRaster_sub.SetGeoTransform(GEOMraster.GetGeoTransform())
                vasRaster_sub.SetProjection(GEOMraster.GetProjection())
                gdal.ReprojectImage(valRaster, vasRaster_sub, valRaster.GetProjection(), GEOMraster.GetProjection(), gdal.GRA_NearestNeighbour)
                return vasRaster_sub
            ecoGEOM_forest = ReprojectRaster(forest, ecoGEOM_ras)
            ecoGEOM_loss = ReprojectRaster(loss, ecoGEOM_ras)
            ecoGEOM_gain = ReprojectRaster(gain, ecoGEOM_ras)
            #bt.baumiRT.CopyMEMtoDisk(ecoGEOM_ras, rootFolder + "mask.tif")
            #bt.baumiRT.CopyMEMtoDisk(ecoGEOM_forest, rootFolder+"forest.tif")
            #bt.baumiRT.CopyMEMtoDisk(ecoGEOM_loss, rootFolder + "loss.tif")
            #bt.baumiRT.CopyMEMtoDisk(ecoGEOM_gain, rootFolder + "gain.tif")
            # Open all rasters into np-arrays
            geom_np = ecoGEOM_ras.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
            forest_np = ecoGEOM_forest.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
            loss_np = ecoGEOM_loss.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
            gain_np = ecoGEOM_gain.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
            # Now extract the summaries
            # Forest 2000 --> 25% and 40% canopy
            forest_np_25 = np.where((geom_np == 1) & (forest_np >= 25), 1, 0)
            forest_np_25 = forest_np_25.astype(np.uint8)
            f25 = forest_np_25.sum() * 30 * 30 / 1000000
            vals.append(format(f25, '.5f'))
            forest_np_40 = np.where((geom_np == 1) & (forest_np >= 40), 1, 0)
            forest_np_40 = forest_np_40.astype(np.uint8)
            f40 = forest_np_40.sum() * 30 * 30 / 1000000
            vals.append(format(f40, '.5f'))
            # Loss per year
            for yr in range(1, 19, 1):
                loss_np_yr = np.where((geom_np == 1) & (loss_np == yr), 1, 0)
                loss_np_yr = loss_np_yr.astype(np.uint8)
                loss_yr = loss_np_yr.sum() * 30 * 30 / 1000000
                vals.append(format(loss_yr, '.5f'))

        # If the polygon is < 1px in x- and y-direction, then write zeros for everything
        else:
            vals.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        # Append the values to the output-DS, then take the next feature
        outDS.append(vals)
    eco_feat = eco_lyr.GetNextFeature()
# Write output to disc
time.sleep(1)
print("Write output")
with open(out_csv, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in outDS:
        writer.writerow(element)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")



# # Reproject the raster layers into the ecoGEOM_ras
# ecoGEOM_forest = ReprojectRaster(forest, ecoGEOM_ras)
# ecoGEOM_loss = ReprojectRaster(loss, ecoGEOM_ras)
# ecoGEOM_gain = ReprojectRaster(gain, ecoGEOM_ras)
# # Extrat the summaries through numpy arrays
# geom_np, forest_np = bt.baumiRT.Geom_Raster_to_np(ecoGEOM, ecoGEOM_forest)
# geom_np, loss_np = bt.baumiRT.Geom_Raster_to_np(ecoGEOM, ecoGEOM_loss)
# geom_np, gain_np = bt.baumiRT.Geom_Raster_to_np(ecoGEOM, ecoGEOM_gain)
# # Now extract the summaries
# # Forest 2000
# forest_np_25 = np.where((geom_np == 1) & (forest_np >= 25), 1, 0)
# f25 = forest_np_25.sum() * 30 * 30 / 1000000
# vals.append(format(f25, '.5f'))
# forest_np_40 = np.where((geom_np == 1) & (forest_np >= 40), 1, 0)
# f40 = forest_np_40.sum() * 30 * 30 / 1000000
# vals.append(format(f40, '.5f'))
# # Loss per year
# for yr in range(1, 18, 1):
# loss_np_yr = np.where((geom_np == 1) & (loss_np == yr), 1, 0)
# loss_yr = loss_np_yr.sum() * 30 * 30 / 1000000
# vals.append(format(loss_yr, '.5f'))
# # gain
# gain_np_mask = np.where((geom_np == 1) & (gain_np == 1), 1, 0)
# gn = gain_np_mask.sum() * 30 * 30 / 1000000
# vals.append(format(gn, '.5f'))
# #print(UID)
# except:
# vals.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
# outDS.append(vals)