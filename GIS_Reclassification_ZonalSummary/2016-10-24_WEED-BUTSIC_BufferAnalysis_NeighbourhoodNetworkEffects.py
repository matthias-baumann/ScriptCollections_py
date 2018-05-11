# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
from gdalconst import *
import ogr, osr
from ZumbaTools._Vector_Tools import *
import csv
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
buffer = 1500 # buffer in feet
outFile = "D:/baumamat/Butsic_etal_NeighborhoodSummaries/BufferAnalysis_20161024_500m.csv"
APN_in = "D:/baumamat/Butsic_etal_NeighborhoodSummaries/APN_clean.txt"
parcelname = "D:/baumamat/Butsic_etal_NeighborhoodSummaries/00_Parcel.shp"
slope = gdal.Open("D:/baumamat/Butsic_etal_NeighborhoodSummaries/DEM_Humboldt_slope.tif", GA_ReadOnly)
aspect = gdal.Open("D:/baumamat/Butsic_etal_NeighborhoodSummaries/DEM_Humboldt_aspect.tif", GA_ReadOnly)
cover = gdal.Open("D:/baumamat/Butsic_etal_NeighborhoodSummaries/Veg_AsRaster_30m.tif", GA_ReadOnly)
THP = "D:/baumamat/Butsic_etal_NeighborhoodSummaries/12_TimberHarvestPlan_PlanDissolve.shp"
# ####################################### FUNCTIONS ########################################################### #
def Ctrans_shp(LYRfrom, LYRto):
    outPR = LYRto.GetSpatialRef()
    inPR = LYRfrom.GetSpatialRef()
    transform = osr.CoordinateTransformation(inPR, outPR)
    return transform
def Ctrans_ras(polSR, rasSR):
    target_SR = osr.SpatialReference()
    target_SR.ImportFromWkt(rasSR)
    transform = osr.CoordinateTransformation(polSR, target_SR)
    return transform
def BuildArraysForSummary(geometry, rasterFile):
    rasterSize = float(rasterFile.GetGeoTransform()[1])
    target_SR = osr.SpatialReference()
    target_SR.ImportFromWkt(rasterFile.GetProjection())
    # Create new SHP-file in memory to which we copy the geometry
    shpMem = drvMemV.CreateDataSource('')
    shpMem_lyr = shpMem.CreateLayer('shpMem', target_SR, geom_type=ogr.wkbMultiPolygon)
    shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
    shpMem_feat = ogr.Feature(shpMem_lyr_defn)
    shpMem_feat.SetGeometry(geometry)
    shpMem_lyr.CreateFeature(shpMem_feat)
    # Load new SHP-file into array
    x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
    x_res = int((x_max - x_min) / rasterSize)
    y_res = int((y_max - y_min) / rasterSize)
    # Polygon has to be at least one pixel wide or long
    if x_res > 0 and y_res > 0:
        shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
        shpMem_asRaster.SetProjection(rasterFile.GetProjection())
        shpMem_asRaster.SetGeoTransform((x_min, rasterSize, 0, y_max, 0, -rasterSize))
        shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
        shpMem_asRaster_b.SetNoDataValue(0)
        gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
        shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
        # CopyMEMtoDisk(shpMem_asRaster, "D:/shp.tif")
        # Subset the classification raster and load it into the array
        rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, gdal.GDT_Float32)
        rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
        rasMem.SetProjection(shpMem_asRaster.GetProjection())
        gdal.ReprojectImage(rasterFile, rasMem, rasterFile.GetProjection(), shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
        rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
        return shpMem_array, rasMem_array
def CreateSHPfromLYR(LYR):
# Build the outputSHP
    shpMem = drvMemV.CreateDataSource('')
    shpMem_lyr = shpMem.CreateLayer('shpMem', LYR.GetSpatialRef(), geom_type=ogr.wkbMultiPolygon)
    shpMem_lyr_defn = LYR.GetLayerDefn()
# Create all fields in the new shp-file that we created before
    for i in range(0, shpMem_lyr_defn.GetFieldCount()):
        fieldDefn = shpMem_lyr_defn.GetFieldDefn(i)
        shpMem_lyr.CreateField(fieldDefn)
# Now copy feature per feature into the memory shapefile
    feat = LYR.GetNextFeature()
    while feat:
        geom = feat.GetGeometryRef()
        outFeat = ogr.Feature(shpMem_lyr_defn)
        outFeat.SetGeometry(geom)
        for i in range(0, shpMem_lyr_defn.GetFieldCount()):
            outFeat.SetField(shpMem_lyr_defn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))
        shpMem_lyr.CreateFeature(outFeat)
# Destroy/Close the features and get next input-feature
        outFeat.Destroy()
        feat.Destroy()
        feat = LYR.GetNextFeature()
    return shpMem
# ####################################### GET THE LIST OF THE APN WE ANALYZE  ################################# #
apn_list = []
txt_open = open(APN_in, "r")
for line in txt_open:
    line = line.replace("\n","")
    line = line.replace("'","")
    apn_list.append(line)
txt_open.close()

# ####################################### OPEN FILES, BUILD COORDINATE TRANSFORMATION ######################### #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
parcel = drvMemV.CopyDataSource(ogr.Open(parcelname),'')
parcelLYR = parcel.GetLayer()
parcelRef = drvMemV.CopyDataSource(ogr.Open(parcelname),'')
parcelLYRref = parcelRef.GetLayer()
thp = drvMemV.CopyDataSource(ogr.Open(THP), '')
thpLYR = thp.GetLayer()
# ####################################### BUILD HEADER IN OUTPUT-FILE ######################################### #
outList = []
header = ["APN", "ParcelSize_acres", "BufferSize_acres", "#_NeighParcels", "meanArea_acres", "meanArea_acres_sq",
          # Zoning percentages
          "#parc_AEZ", "#parc_Ag", "#parc_TPZ", "#parc_ResUrb", "#parc_ForRec", "#parc_City", "#parc_Other",
          # Calculated variables
          "perc_slope30", "percSESSW", "Mix_p", "HDW_p", "SHP_p", "CON_p", "BAR_p", "THP_YN"]
outList.append(header)
# ####################################### LOOP THROUGH FEATURES ############################################### #
zone_feat = parcelLYR.GetNextFeature()
i = 1
while zone_feat:
#### Check if object in skipList
    ID = zone_feat.GetField("APN")
    if ID in apn_list:# and int(ID) == 51313108:
        print("Processing APN " + str(ID) + ", Parcel " + str(i) + " out of " + str(len(apn_list)))
        i = i + 1
# Append parcel ID
        vals = []
        vals.append(ID)
# Get the Geometry
        geom = zone_feat.GetGeometryRef()
        area = geom.GetArea()
        vals.append(area)
# Grow a buffer, intersect it with the geometry (to get the buffer area only), then set extent of Parcel_LYR, get number of parcels
        geomBuff = geom.Buffer(buffer)
        buffArea = geomBuff.GetArea()
        vals.append(buffArea)
        intersection = geomBuff.Difference(geom)
        parcelLYRref.SetSpatialFilter(intersection)
        nrParcels = parcelLYRref.GetFeatureCount()
        vals.append(nrParcels)
# Calculate average parcel size of selected parcels, get also the zoning information
        # Area of the zone
        areaSum = -(zone_feat.GetField("AREA")) # so that we do not count the area of the center parcel
        sub_feat = parcelLYRref.GetNextFeature()
        # Empty Zoning variables --> we fill these now in the loop
        AEZ = 0
        Ag = 0
        TPZ = 0
        ResUrb = 0
        ForRec = 0
        City = 0
        while sub_feat:
            # Area calculation
            area = sub_feat.GetField("AREA")
            areaSum = areaSum + area
            # Zoning variables
            zoneType = sub_feat.GetField("ZONING")
            if zoneType != None:
                if zoneType.startswith("AE"):
                    AEZ = AEZ + 1
                if zoneType.startswith("AG"):
                    Ag = Ag + 1
                if zoneType.startswith("TPZ"):
                    TPZ = TPZ + 1
                if zoneType.startswith("RS"):
                    ResUrb = ResUrb + 1
                if zoneType.startswith("FR"):
                    ForRec = ForRec + 1
                if zoneType.startswith("CITY"):
                    City = City + 1
            else:
                AEZ = AEZ
                Ag = Ag
                TPZ = TPZ
                ResUrb = ResUrb
                ForRec = ForRec
                City = City
            sub_feat = parcelLYRref.GetNextFeature()
        avArea = areaSum / nrParcels
        vals.append(avArea)
        vals.append(avArea * avArea)
        vals.append(AEZ)
        vals.append(Ag)
        vals.append(TPZ)
        vals.append(ResUrb)
        vals.append(ForRec)
        vals.append(City)
        Other = nrParcels - (AEZ + Ag + TPZ + ResUrb + ForRec + City)
        vals.append(Other)
        parcelLYRref.ResetReading()
# Calculate percentage of buffer with more than 30% slope; use clone of geometry
        geomCL = intersection.Clone()
        geomCL.Transform(Ctrans_ras(parcelLYR.GetSpatialRef(), slope.GetProjection()))
        shpArray, rasArray = BuildArraysForSummary(geomCL, slope)
        above30 = np.sum(np.where((shpArray == 1) * (rasArray > 30), 1, 0))
        above0 = np.sum(np.where((shpArray  == 1), 1, 0))
        ratio = above30 / above0
        vals.append(ratio)
# Calculate percentage of buffer facing SW, S, SE; use new clone
        geomCL = intersection.Clone()
        geomCL.Transform(Ctrans_ras(parcelLYR.GetSpatialRef(), aspect.GetProjection()))
        shpArray, rasArray = BuildArraysForSummary(geomCL, aspect)
        inBuffer = np.sum(np.where((shpArray == 1), 1, 0))
        SESSW = np.sum(np.where((shpArray == 1) * (rasArray >= 112.5) * (rasArray <= 247.5), 1, 0))
        ratio = SESSW / inBuffer
        vals.append(ratio)
# Percent of land-cover types
        geomCL = intersection.Clone()
        geomCL.Transform(Ctrans_ras(parcelLYR.GetSpatialRef(), cover.GetProjection()))
        shpArray, rasArray = BuildArraysForSummary(geomCL, cover)
        value = [["MIX_p", 1], ["HDW_p", 2], ["SHB_p", 3], ["CON_p", 4], ["BAR_p", 6]]
        for val in value:
            inBuffer = np.sum(np.where((shpArray == 1), 1, 0))
            cov = np.sum(np.where((shpArray == 1) * (rasArray == val[1]), 1, 0))
            ratio = cov / inBuffer
            vals.append(ratio)
# Timber Harvest Plan - binary: was the parcel ever part of the THP
        geomCL = intersection.Clone()
        geomCL.Transform(Ctrans_shp(parcelLYR, thpLYR))
        thpYN = 0
        thpFeat = thpLYR.GetNextFeature()
        while thpFeat:
            geomTHP = thpFeat.GetGeometryRef()
            intersect = geomCL.Intersect(geomTHP)
            if int(intersect) == 0:
                thpFeat = thpLYR.GetNextFeature()
            else:
                thpYN = 1
                thpFeat = thpLYR.GetNextFeature()
        thpLYR.ResetReading()
        vals.append(thpYN)
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