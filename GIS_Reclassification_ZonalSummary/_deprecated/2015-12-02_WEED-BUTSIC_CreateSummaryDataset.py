# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, osr
from ZumbaTools._Vector_Tools import *
from ZumbaTools._Raster_Tools import *
from gdalconst import *
import gdal
import numpy as np
import csv
# ############################################################################################################# #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
outFile = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/SummaryDataset_V03_20160420.csv"
# ############################################################################################################# #
pxSize = 1
#skipIDs = [45613, 10189, 10193, 19859, 19878, 49969, 49991, 49992, 50001, 50007, 50011, 50015, 50029, 50030,
          # 50031, 62445, 64199, 64208, 64210, 64211, 64772, 69106, 51968]
#skipIDs = [51968, 10203]
# ####################################### OPEN ALL FILES THAT WE WILL SUMMARIZE ############################### #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
drvMemV = ogr.GetDriverByName('Memory')
print("Load files to memory")
parcel = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/00_Parcel.shp"),'')
parcelLYR = parcel.GetLayer()
grows = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/01_Grows.shp"),'')
growsLYR = grows.GetLayer()
chinook = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/02_Chinook.shp"),'')
chinookLYR = chinook.GetLayer()
steelhead = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/03_Steelhead.shp"),'')
steelheadLYR = steelhead.GetLayer()
agLand = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/04_AgriLands.shp"),'')
agLandLYR = agLand.GetLayer()
pubLand = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/04_AgriLands.shp"),'')
pubLandLYR = pubLand.GetLayer()
watershed = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/07_Watershed.shp"),'')
watershedLYR = watershed.GetLayer()
williams = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/08_Willamsont.shp"),'')
williamsLYR = williams.GetLayer()
roads = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/09_Roads.shp"),'')
roadsLYR = roads.GetLayer()
cities = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/10_Cities.shp"),'')
citiesLYR = cities.GetLayer()
veg = drvMemR.CreateCopy('',gdal.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/Veg_AsRaster_30m.tif"))
slope = drvMemR.CreateCopy('',gdal.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/DEM_Humboldt_slope.tif"))
road_dis = drvMemR.CreateCopy('',gdal.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/DistanceToRoads.tif"))
# ####################################### ADD FIELDS TO OUTPUT-LAYER ########################################## #
outList = []
header = [
    # Unique identifier
    "Unique_ID",
    # Variables from teh shapefile
    "APN", "AREA","EXLU4","BKPG","NEIGHCODE","TRA","GEN_PLAN","ZONING","ZONEDATE","CZ","CJ","FZ","FR","AC_SQFT","AQ","SS","AOB","AIRPORT","SRA","MULTI_SIT","APN_12",
    # Calculated variables
    "Grow_YN", "GH_YN", "NRplants", "NRplantsGH", "Chinook_YN","Chinook_km","Steelh_YN","AgLand_p","City_p","Pub_YN",
    "SlopeMean","MIX_p","HDW_p","SHB_p","CON_p","BAR_p","HEB_p","MajWTS_N","MajWTS_p","Will_YN","LocRoad_km","MayColl_km",
    "MinColl_km","MinArt_km","PrinArt_km","Priv_km","Uncl_km","RoadDis_km"]
outList.append(header)
# ####################################### BUILD THE COORDINATE TRANSFORMATIONS ################################ #
print("Build coordinate transformation")
parcel_grows_tr = CoordinateTransform_Vector(parcelLYR, growsLYR)
parcel_chinook_tr = CoordinateTransform_Vector(parcelLYR, chinookLYR)
parcel_steelhead_tr = CoordinateTransform_Vector(parcelLYR, steelheadLYR)
parcel_agLand_tr = CoordinateTransform_Vector(parcelLYR, agLandLYR)
parcel_pubLand_tr = CoordinateTransform_Vector(parcelLYR, pubLandLYR)
parcel_watershed_tr = CoordinateTransform_Vector(parcelLYR, watershedLYR)
parcel_williams_tr = CoordinateTransform_Vector(parcelLYR, williamsLYR)
parcel_roads_tr = CoordinateTransform_Vector(parcelLYR, roadsLYR)
parcel_cities_tr = CoordinateTransform_Vector(parcelLYR, citiesLYR)
parcel_slope_tr = CoordinateTransform_Raster(slope, parcelLYR)
parcel_veg_tr = CoordinateTransform_Raster(veg, parcelLYR)
parcel_roaddist_tr = CoordinateTransform_Raster(road_dis, parcelLYR)
# ####################################### GET THE FIRST FEATURE OF THE ZONE-FILE, THEN LOOP ################### #
zone_feat = parcelLYR.GetNextFeature()
while zone_feat:
# (0a) Get unique identifier, then add it to the outvals
    ID = zone_feat.GetField("UniqueID")
    #if not ID in skipIDs:
    try:
        print("Processing UniqueID " + str(ID))
        vals = []
        vals.append(ID)
# (0b) Get the fields from the shapefile
        vals.append(zone_feat.GetField("APN"))
        vals.append(zone_feat.GetField("AREA"))
        vals.append(zone_feat.GetField("EXLU4"))
        vals.append(zone_feat.GetField("BKPG"))
        vals.append(zone_feat.GetField("NEIGHCODE"))
        vals.append(zone_feat.GetField("TRA"))
        vals.append(zone_feat.GetField("GEN_PLAN"))
        vals.append(zone_feat.GetField("ZONING"))
        vals.append(zone_feat.GetField("ZONEDATE"))
        vals.append(zone_feat.GetField("CZ"))
        vals.append(zone_feat.GetField("CJ"))
        vals.append(zone_feat.GetField("FZ"))
        vals.append(zone_feat.GetField("FR"))
        vals.append(zone_feat.GetField("AC_SQFT"))
        vals.append(zone_feat.GetField("AQ"))
        vals.append(zone_feat.GetField("SS"))
        vals.append(zone_feat.GetField("AOB"))
        vals.append(zone_feat.GetField("AIRPORT"))
        vals.append(zone_feat.GetField("SRA"))
        vals.append(zone_feat.GetField("MULTI_SIT"))
        vals.append(zone_feat.GetField("APN_12"))
# Get the Geometry of the feature
        geom = zone_feat.GetGeometryRef()
# (1) "Grow_YN"
    # Create geometry-clone for the evaluation of the grows-layer, do coordinate transform
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_grows_tr)
    # Set spatial filter, get the summaries
        growsLYR.SetSpatialFilter(geom_zone)
        nr_points = growsLYR.GetFeatureCount()
        if nr_points > 0:
            Grow_YN = 1
        else:
            Grow_YN = 0
        vals.append(Grow_YN)
# (2) "GH_YN" / "NRplantsGH" / "NRplants"
        grow_feat = growsLYR.GetNextFeature()
        GH_YN = 0
        g_plants = 0
        o_plants = 0
        while grow_feat:
    # See if location is a greenhouse
            GH_test = grow_feat.GetField("greenhouse")
            if GH_test == 1:
                GH_YN = 1
            else:
                GH_YN = GH_YN
    # Get number of plants in greenhouses
            p_gh = grow_feat.GetField("g_plants")
            g_plants = g_plants + p_gh
    # Get number of plants in open space
            g_open = grow_feat.GetField("o_plants")
            o_plants = o_plants + g_open
            grow_feat = growsLYR.GetNextFeature()
        growsLYR.ResetReading()
        vals.append(GH_YN)
        vals.append(g_plants)
        vals.append(o_plants)
# (3) "Chinook_YN" / "Chinook_km"
    # Create geometry-clone for the chinook-layer, get geometry of chinook-layer (single-feature-layer, already dissolved)
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_chinook_tr)
        feat_chinook = chinookLYR.GetNextFeature()
        geom_chinook = feat_chinook.GetGeometryRef()
    # Do intersection, get geometry information
        intersection = geom_zone.Intersection(geom_chinook)
        if intersection.Length() == 0:
            vals.append(0)
            vals.append(0)
        else:
            vals.append(1)
            length = (intersection.Length()/1000)
            vals.append(length)
        chinookLYR.ResetReading()
# (4) "Steelh_YN" / "Steelh_km"
    # Create geometry-clone for the steelhead-layer, get geometry of steelhead-layer (single-feature-layer, already dissolved)
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_steelhead_tr)
        feat_steelhead = steelheadLYR.GetNextFeature()
        geom_steelhead = feat_steelhead.GetGeometryRef()
    # Do intersection, get geometry information
        intersection = geom_zone.Intersection(geom_steelhead)
        if intersection.Length() == 0:
            vals.append(0)
            vals.append(0)
        else:
            vals.append(1)
            length = (intersection.Length()/1000)
            vals.append(length)
        steelheadLYR.ResetReading()
# (5) "AgLand_p" / "AgLand_km"
    # Create geometry clone
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_agLand_tr)
        feat_agLand = agLandLYR.GetNextFeature()
        geom_agLand = feat_agLand.GetGeometryRef()
    # Do intersection, get geometry information
        intersection = geom_zone.Intersection(geom_agLand)
        if intersection.GetArea() == 0:
            vals.append(0)
            vals.append(0)
        else:
            IntersectArea = intersection.GetArea()/1000000
            vals.append(IntersectArea)
            parcelArea = geom_zone.GetArea()
            percentage = intersection.GetArea() / parcelArea
            vals.append(percentage)
        agLandLYR.ResetReading()
# (6) "City_p"
    # Create Geometry-clone
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_cities_tr)
        feat_cities = citiesLYR.GetNextFeature()
        geom_cities = feat_cities.GetGeometryRef()
    # Do intersection, get geometry information
        intersection = geom_zone.Intersection(geom_cities)
        if intersection.GetArea() == 0:
            vals.append(0)
        else:
            parcelArea = geom_zone.GetArea()
            percentage = intersection.GetArea() / parcelArea
            vals.append(percentage)
        citiesLYR.ResetReading()
# (7) "Pub_YN"
    # Create Geometry clones
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_pubLand_tr)
        feat_public = pubLandLYR.GetNextFeature()
        geom_public = feat_public.GetGeometryRef()
    # Do intersection
        intersection = geom_zone.Intersection(geom_public)
        if intersection.GetArea() <= 0.00000000001:
            vals.append(0)
        else:
            vals.append(1)
        pubLandLYR.ResetReading()
# (8) "Slope30_p"
    # Create Geometry clone, transform to raster-CS
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_slope_tr)
    # Build shp-file in memory from geom_zone
        target_SR = osr.SpatialReference()
        target_SR.ImportFromWkt(slope.GetProjection())
        shpMem = drvMemV.CreateDataSource('')
        shpMem_lyr = shpMem.CreateLayer('shpMem', target_SR, geom_type = ogr.wkbMultiPolygon)
        shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
        shpMem_feat = ogr.Feature(shpMem_lyr_defn)
        shpMem_feat.SetGeometry(geom_zone)
        shpMem_lyr.CreateFeature(shpMem_feat)
    # Load new SHP-file into array
        x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
        x_res = int((x_max - x_min) / pxSize)
        y_res = int((y_max - y_min) / pxSize)
        shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
        shpMem_asRaster.SetProjection(slope.GetProjection())
        shpMem_asRaster.SetGeoTransform((x_min, pxSize, 0, y_max, 0, -pxSize))
        shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
        shpMem_asRaster_b.SetNoDataValue(255)
        gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
        shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
    # Subset the classification raster and load it into the array
        rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, gdal.GDT_Byte)
        rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
        rasMem.SetProjection(shpMem_asRaster.GetProjection())
        gdal.ReprojectImage(slope, rasMem, slope.GetProjection(), shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
        rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
    # Mask out areas outside the hexagon, assign value of 999
        hexaMask_array = rasMem_array
        np.putmask(hexaMask_array, shpMem_array == 0, 0)
    # Calculate the mean slope
        mean_slope = np.mean(hexaMask_array)
        vals.append(mean_slope)
#(9) "MIX_p", "HDW_p", "SHB_p", "CON_p", "BAR_p", "HEB_p"
    # Create Geometry clone, transform to raster-CS
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_veg_tr)
    # Build shp-file in memory from geom_zone
        target_SR = osr.SpatialReference()
        target_SR.ImportFromWkt(veg.GetProjection())
        shpMem = drvMemV.CreateDataSource('')
        shpMem_lyr = shpMem.CreateLayer('shpMem', target_SR, geom_type = ogr.wkbMultiPolygon)
        shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
        shpMem_feat = ogr.Feature(shpMem_lyr_defn)
        shpMem_feat.SetGeometry(geom_zone)
        shpMem_lyr.CreateFeature(shpMem_feat)
    # Load new SHP-file into array
        x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
        x_res = int((x_max - x_min) / pxSize)
        y_res = int((y_max - y_min) / pxSize)
        shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
        shpMem_asRaster.SetProjection(veg.GetProjection())
        shpMem_asRaster.SetGeoTransform((x_min, pxSize, 0, y_max, 0, -pxSize))
        shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
        shpMem_asRaster_b.SetNoDataValue(255)
        gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
        shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
    # Subset the classification raster and load it into the array
        rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, gdal.GDT_Byte)
        rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
        rasMem.SetProjection(shpMem_asRaster.GetProjection())
        gdal.ReprojectImage(veg, rasMem, veg.GetProjection(), shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
        rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
    # Mask out areas outside the hexagon, assign value of 99
        hexaMask_array = rasMem_array
        np.putmask(hexaMask_array, shpMem_array == 0, 99)
        # Dot eh evaluations [rasterValue, class]
        value = [["MIX_p",1],["HDW_p",2],["SHB_p",3],["CON_p",4],["BAR_p",6],["HEB_p",7]]
        zone_area_km = geom_zone.GetArea() / 1000000
        for val in value:
            px_criteria = (hexaMask_array == val[1]).sum()
            km_criteria = (px_criteria * pxSize * pxSize) / 1000000
            perc_criteria = km_criteria / zone_area_km
            vals.append(perc_criteria)
# (10) "MajWTS_N", "MajWTS_p"
    # Create geometry-clone for the chinook-layer, get geometry of chinook-layer (single-feature-layer, already dissolved)
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_watershed_tr)
        geom_area = geom_zone.GetArea()
        eval_list = [] # List with the evaluations. Is formed of tupels that have the name and the percentage ["Name",val%]
        feat_WS = watershedLYR.GetNextFeature()
        while feat_WS:
            WS_Name = feat_WS.GetField("Name")
            geom_WS = feat_WS.GetGeometryRef()
            intersection = geom_zone.Intersection(geom_WS)
            area_intersection = intersection.GetArea()
            percentage = area_intersection / geom_area
            tupel = [WS_Name, percentage]
            eval_list.append(tupel)
            feat_WS = watershedLYR.GetNextFeature()
        watershedLYR.ResetReading()
        WSmax_name = sorted(eval_list,key=lambda x: -x[1])[0][0]
        WSmax_perc = sorted(eval_list,key=lambda x: -x[1])[0][1]
        vals.append(WSmax_name)
        vals.append(WSmax_perc)
# (11) "Will_YN"
    # Create geometry-clone for the chinook-layer, get geometry of chinook-layer (single-feature-layer, already dissolved)
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_williams_tr)
        feat_williams = williamsLYR.GetNextFeature()
        geom_williams = feat_williams.GetGeometryRef()
    # Do intersection --> inaccuracies in gemometric layer cause that areas can be minimal (10e-6), thats why we use a threshold
        intersection = geom_zone.Intersection(geom_williams)
        if intersection.GetArea() <= 0.001:
            vals.append(0)
        else:
            vals.append(1)
        williamsLYR.ResetReading()
# (12) "LocRoad_km", "MayColl_km", "MinColl_km", "MinArt_km", "PrinArt_km", "Priv_km", "Uncl_km"
    # Create geometry-clone, build names for categories
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_roads_tr)
    # Build sub-function
        def roadFunc(roadLayer, Subsetequation, parcelGeom):
            roadLayer.SetAttributeFilter(Subsetequation)
            feat_road = roadLayer.GetNextFeature()
            length = 0
            while feat_road:
         # Get the intersection
                geom_road = feat_road.GetGeometryRef()
                intersection = parcelGeom.Intersection(geom_road)
                length_intersection = intersection.Length() / 1000 #(in km)
                length = length + length_intersection
                feat_road = roadsLYR.GetNextFeature()
            roadLayer.ResetReading()
            return length



    # Select local roads
        localkm = roadFunc(roadsLYR, "FUNCTIONAL = 'Local Roads'", geom_zone)
        vals.append(localkm)
        maycollkm = roadFunc(roadsLYR, "FUNCTIONAL = 'Major Collectors'", geom_zone)
        vals.append(maycollkm)
        mincollkm = roadFunc(roadsLYR, "FUNCTIONAL = 'Minor Collectors'", geom_zone)
        vals.append(mincollkm)
        minartkm = roadFunc(roadsLYR, "FUNCTIONAL = 'Minor Arterials'", geom_zone)
        vals.append(minartkm)
        prinartkm = roadFunc(roadsLYR, "FUNCTIONAL = 'Principal Arterials'", geom_zone)
        vals.append(prinartkm)
        privkm = roadFunc(roadsLYR, "FUNCTIONAL = 'Private'", geom_zone)
        vals.append(privkm)
        unclkm = roadFunc(roadsLYR, "FUNCTIONAL = 'Unclassified'", geom_zone)
        vals.append(unclkm)
# (13) RoadDis_km
    # Create geometry-clone, build names for categories
        geom_zone = geom.Clone()
        geom_zone.Transform(parcel_roaddist_tr)
    # Build shp-file in memory from geom_zone
        target_SR = osr.SpatialReference()
        target_SR.ImportFromWkt(road_dis.GetProjection())
        shpMem = drvMemV.CreateDataSource('')
        shpMem_lyr = shpMem.CreateLayer('shpMem', target_SR, geom_type = ogr.wkbMultiPolygon)
        shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
        shpMem_feat = ogr.Feature(shpMem_lyr_defn)
        shpMem_feat.SetGeometry(geom_zone)
        shpMem_lyr.CreateFeature(shpMem_feat)
    # Load new SHP-file into array
        x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
        x_res = int((x_max - x_min) / pxSize)
        y_res = int((y_max - y_min) / pxSize)
        shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
        shpMem_asRaster.SetProjection(road_dis.GetProjection())
        shpMem_asRaster.SetGeoTransform((x_min, pxSize, 0, y_max, 0, -pxSize))
        shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
        shpMem_asRaster_b.SetNoDataValue(255)
        gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
        shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
    # Subset the distance raster and load it into the array
        rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, gdal.GDT_Int16)
        rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
        rasMem.SetProjection(shpMem_asRaster.GetProjection())
        gdal.ReprojectImage(road_dis, rasMem, road_dis.GetProjection(), shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
        rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
    # Do the summary
        hexaMask_array = rasMem_array
        np.putmask(hexaMask_array, shpMem_array == 0, 999)
        #hexaMask_array = hexaMask_array.astype('float')
        #hexaMask_array[hexaMask_array==0] = np.nan
        meanDist = np.mean(hexaMask_array) / 1000
        vals.append(meanDist)
# (14) Add vals-list to outList, then go to next feature
        outList.append(vals)
        zone_feat = parcelLYR.GetNextFeature()
    except:
        print("Some error occurred, skipping...")
        zone_feat = parcelLYR.GetNextFeature()
# (14) Write output
print("Write output")
with open(outFile, "w") as theFile:
    csv.register_dialect("custom", delimiter = ";", skipinitialspace = True, lineterminator = '\n')
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