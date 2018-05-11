# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import gdal, osr, ogr
from ZumbaTools._Vector_Tools import *
from gdalconst import *
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
shape = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/LePolainDeWaroux-etal_Review-LCLUC-Chaco/00_Shapefiles/CHACO_Hexagon3km_LAEA.shp"
classification = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_Chaco-LCLUC_Carbon/run12_classification_full_masked_clump-eliminate4px_reclass_V02.img"
# ####################################### PROCESSING ########################################################## #
# ADD FIELDS WE NEED TO THE SHAPEFILE
AddFieldToSHP(shape, "Area_km2", "float")
AddFieldToSHP(shape, "F_85_km2", "float")
AddFieldToSHP(shape, "F_00_km2", "float")
AddFieldToSHP(shape, "F_13_km2", "float")
AddFieldToSHP(shape, "F_85_per", "float")
AddFieldToSHP(shape, "F_00_per", "float")
AddFieldToSHP(shape, "F_13_per", "float")
AddFieldToSHP(shape, "P_85_per", "float")
AddFieldToSHP(shape, "P_00_per", "float")
AddFieldToSHP(shape, "P_13_per", "float")
AddFieldToSHP(shape, "C_85_per", "float")
AddFieldToSHP(shape, "C_00_per", "float")
AddFieldToSHP(shape, "C_13_per", "float")
AddFieldToSHP(shape, "D_8500_km2", "float")
AddFieldToSHP(shape, "D_8500_per", "float")
AddFieldToSHP(shape, "D_0013_km2", "float")
AddFieldToSHP(shape, "D_0013_per", "float")
AddFieldToSHP(shape, "D_8513_km2", "float")
AddFieldToSHP(shape, "D_8513_per", "float")
# LOAD DRIVERS ETC.
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvR = gdal.GetDriverByName('ENVI')
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
# OPEN FILES
# Shapefile
sh_open = ogr.Open(shape, 1)
lyr = sh_open.GetLayer()
pol_srs = lyr.GetSpatialRef()
# Rasterfile
ras_open = gdal.Open(classification, GA_ReadOnly)
gt = ras_open.GetGeoTransform()
pr = ras_open.GetProjection()
cols = ras_open.RasterXSize
rows = ras_open.RasterYSize
ras_srs = ras_open.GetProjection()
# BUILD COORDINATE-TRANSFORMATION --> not 100% needed because raster/shape have some CS, but routinely generated
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(ras_srs)
transform = osr.CoordinateTransformation(pol_srs, target_SR)
# LOOP THROUGH POLYGON FEATURES
feat = lyr.GetNextFeature()
while feat:
    # Get id-field for print-statement
    id = feat.GetField("Id")
    print("Processing polygon with Unique-ID:", id)
    # Create a geometry and apply the coordinate transformation
    geom = feat.GetGeometryRef()
    hexa_area = geom.GetArea() / 1000000
    #geom.Transform(transform)
    # Create new SHP-file in memory to which we copy the geometry
    shpMem = drvMemV.CreateDataSource('')
    shpMem_lyr = shpMem.CreateLayer('shpMem', target_SR, geom_type = ogr.wkbMultiPolygon)
    shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
    shpMem_feat = ogr.Feature(shpMem_lyr_defn)
    shpMem_feat.SetGeometry(geom.Clone())
    shpMem_lyr.CreateFeature(shpMem_feat)
    # Load new SHP-file into array
    x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
    x_res = int((x_max - x_min) / 30)
    y_res = int((y_max - y_min) / 30)
    shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
    shpMem_asRaster.SetProjection(ras_srs)
    shpMem_asRaster.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
    shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
    shpMem_asRaster_b.SetNoDataValue(255)
    gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
    shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
    # Subset the classification raster and load it into the array
    rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, gdal.GDT_Byte)
    rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
    rasMem.SetProjection(shpMem_asRaster.GetProjection())
    gdal.ReprojectImage(ras_open, rasMem, pr, shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
    rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
    # Mask out areas outside the hexagon, assign value of 99
    hexaMask_array = rasMem_array
    np.putmask(hexaMask_array, shpMem_array == 0, 999)
    ##### OPERATIONS FOR DATA EXTRACTION, AND ADDITION TO SHAPEFILE
    # "Area_km2"
    feat.SetField("Area_km2", hexa_area)
    # "F_85_km2"
    nrPX_F85_1 = np.count_nonzero(hexaMask_array == 1)
    nrPX_F85_2 = np.count_nonzero(hexaMask_array == 10)
    nrPX_F85_3 = np.count_nonzero(hexaMask_array == 11)
    nrPX_F85_4 = np.count_nonzero(hexaMask_array == 12)
    nrPX_F85_5 = np.count_nonzero(hexaMask_array == 13)
    nrPX_F85_6 = np.count_nonzero(hexaMask_array == 14)
    nrPX_F85_7 = np.count_nonzero(hexaMask_array == 17)
    nrPX_F85_total = nrPX_F85_1 + nrPX_F85_2 + nrPX_F85_3 + nrPX_F85_4 + nrPX_F85_5 + nrPX_F85_6 + nrPX_F85_7
    F85_km2 = (nrPX_F85_total * 900) / 1000000
    feat.SetField("F_85_km2", F85_km2)
    # "F_85_per"
    f85per = F85_km2/hexa_area
    feat.SetField("F_85_per", f85per)
    # "F_00_km2"
    nrPX_F00_1 = np.count_nonzero(hexaMask_array == 1)
    nrPX_F00_2 = np.count_nonzero(hexaMask_array == 12)
    nrPX_F00_3 = np.count_nonzero(hexaMask_array == 13)
    nrPX_F00_4 = np.count_nonzero(hexaMask_array == 17)
    nrPX_F00_total = nrPX_F00_1 + nrPX_F00_2 + nrPX_F00_3 + nrPX_F00_4
    F00_km2 = (nrPX_F00_total * 900) / 1000000
    feat.SetField("F_00_km2", F00_km2)
    # "F_00_per"
    f00per = F00_km2/hexa_area
    feat.SetField("F_00_per", f00per)
    # "F_13_km2"
    nrPX_F13_1 = np.count_nonzero(hexaMask_array == 1)
    nrPX_F13_2 = np.count_nonzero(hexaMask_array == 17)
    nrPX_F13_total = nrPX_F13_1 + nrPX_F13_2
    F13_km2 = (nrPX_F13_total * 900) / 1000000
    feat.SetField("F_13_km2", F13_km2)
    # "F_13_per"
    f13per = F13_km2/hexa_area
    feat.SetField("F_13_per", f13per)
    # "P_85_per"
    nrPX_P85_1 = np.count_nonzero(hexaMask_array == 5)
    nrPX_P85_2 = np.count_nonzero(hexaMask_array == 20)
    nrPX_P85_3 = np.count_nonzero(hexaMask_array == 21)
    nrPX_P85_total = nrPX_P85_1 + nrPX_P85_2 + nrPX_P85_3
    P85_km2 = (nrPX_P85_total * 900) / 1000000
    P85_perc = P85_km2/hexa_area
    feat.SetField("P_85_per", P85_perc)
    # "P_00_per"
    nrPX_P00_1 = np.count_nonzero(hexaMask_array == 5)
    nrPX_P00_2 = np.count_nonzero(hexaMask_array == 11)
    nrPX_P00_3 = np.count_nonzero(hexaMask_array == 14)
    nrPX_P00_4 = np.count_nonzero(hexaMask_array == 21)
    nrPX_P00_total = nrPX_P00_1 + nrPX_P00_2 + nrPX_P00_3 + nrPX_P00_4
    P00_km2 = (nrPX_P00_total * 900) / 1000000
    P00_perc = P00_km2/hexa_area
    feat.SetField("P_00_per", P00_perc)
    # "P_13_per"
    nrPX_P13_1 = np.count_nonzero(hexaMask_array == 5)
    nrPX_P13_2 = np.count_nonzero(hexaMask_array == 11)
    nrPX_P13_3 = np.count_nonzero(hexaMask_array == 13)
    nrPX_P13_total = nrPX_P13_1 + nrPX_P13_2 + nrPX_P13_3
    P13_km2 = (nrPX_P13_total * 900) / 1000000
    P13_perc = P13_km2/hexa_area
    feat.SetField("P_13_per", P13_perc)
    # "C_85_per"
    nrPX_C85_1 = np.count_nonzero(hexaMask_array == 4)
    C85_km2 = (nrPX_C85_1 * 900) / 1000000
    C85_perc = C85_km2/hexa_area
    feat.SetField("C_85_per", C85_perc)
    # "C_00_per"
    nrPX_C00_1 = np.count_nonzero(hexaMask_array == 4)
    nrPX_C00_2 = np.count_nonzero(hexaMask_array == 10)
    nrPX_C00_3 = np.count_nonzero(hexaMask_array == 20)
    nrPX_C00_total = nrPX_C00_1 + nrPX_C00_2 + nrPX_C00_3
    C00_km2 = (nrPX_C00_total * 900) / 1000000
    C00_perc = C00_km2/hexa_area
    feat.SetField("C_00_per", C00_perc)
    # "C_13_per"
    nrPX_C13_1 = np.count_nonzero(hexaMask_array == 4)
    nrPX_C13_2 = np.count_nonzero(hexaMask_array == 10)
    nrPX_C13_3 = np.count_nonzero(hexaMask_array == 12)
    nrPX_C13_4 = np.count_nonzero(hexaMask_array == 14)
    nrPX_C13_5 = np.count_nonzero(hexaMask_array == 20)
    nrPX_C13_6 = np.count_nonzero(hexaMask_array == 21)
    nrPX_C13_total = nrPX_C13_1 + nrPX_C13_2 + nrPX_C13_3 + nrPX_C13_4 + nrPX_C13_5 + nrPX_C13_6
    C13_km2 = (nrPX_C13_total * 900) / 1000000
    C13_perc = C13_km2/hexa_area
    feat.SetField("C_13_per", C13_perc)
    # "D_8500_km2"
    nrPX_FP_8500 = np.count_nonzero(hexaMask_array == 11)
    nrPX_FC_8500 = np.count_nonzero(hexaMask_array == 10)
    nrPX_FPC_8500 = np.count_nonzero(hexaMask_array == 14)
    d8500km2 = ((nrPX_FP_8500 + nrPX_FC_8500 + nrPX_FPC_8500) * 900) / 1000000
    feat.SetField("D_8500_km2", d8500km2)
    # "D_0013_km2"
    nrPX_FP_0013 = np.count_nonzero(hexaMask_array == 13)
    nrPX_FC_0013 = np.count_nonzero(hexaMask_array == 12)
    d0013km2 = ((nrPX_FP_0013 + nrPX_FC_0013) * 900) / 1000000
    feat.SetField("D_0013_km2", d0013km2)
    # D_8513_km2"
    d8513km2 = d8500km2 + d0013km2
    feat.SetField("D_8513_km2", d8513km2)
    # D_8500_per"
    if F85_km2 > 0:
        defRate_8500 = d8500km2 / F85_km2
        defRate_8500_annual = defRate_8500 / 15
    else:
        defRate_8500_annual = 0
    feat.SetField("D_8500_per", defRate_8500_annual)
    # D_0013_per"
    if F00_km2 > 0:
        defRate_0013 = d0013km2 / F00_km2
        defRate_0013_annual = defRate_0013 / 13
    else:
        defRate_0013_annual = 0
    feat.SetField("D_0013_per", defRate_0013_annual)
    # D_8513_per"
    if F85_km2 > 0:
        defRate_8513 = (d8500km2 + d0013km2) / F85_km2
        defRate_8513_annual = defRate_8513 / 28
    else:
        defRate_8513_annual = 0
    feat.SetField("D_8513_per", defRate_8513_annual)
    #### SET THE FEATURE (APPLY CHANGES) AND GO TO NEXT FEATURE
    lyr.SetFeature(feat)
    feat = lyr.GetNextFeature()
# RESET READING AND CLOSE FILES
lyr.ResetReading()
lyr = None
sh_open = None

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")