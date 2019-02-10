# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT GLOBAL FOREST LOSS DATA (HANSEN ET AL) FROM GEE (Version 1.0)                                        ##
## (c) Matthias Baumann, May 2017                                                                               ##
##                                                                                                              ##
## Humboldt-University Berlin                                                                                   ##
# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## ##
import time
import osr
import ee
import csv
import ogr, json
import baumiTools as bt
from tqdm import tqdm
ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
rootFolder = "P:/"
eco_shp = rootFolder + "data/Olson-Ramankutty_Intersection_SinglePart/WWF_potentialVeg_intersect_single_test2.shp"
utm_shp = rootFolder + "data/UTM zones/UTM_Zone_Boundaries.shp"
out_csv = rootFolder + "GEE_extraction/areaSummaries_ALL_20181217.csv"
error_file = rootFolder + "GEE_extraction/areaSummaries_ALL_20181217_reprocessManually.txt"
packageSize = 5
# ####################################### FUNCTIONS ########################################################### #
def Build_EE_polygon(geometry, epsg):
# Transform the coordinate system into EPSG 54012 to get to an equal area projection
    source_SR = geometry.GetSpatialReference()
    target_SR = osr.SpatialReference()
    target_SR.ImportFromEPSG(epsg)
    trans = osr.CoordinateTransformation(source_SR, target_SR)
    geometry.Transform(trans)
# Build the EE-feature via the json-conversion
    geom_json = json.loads(geometry.ExportToJson())
    geom_coord = geom_json['coordinates']
    geom_EE = ee.Geometry.Polygon(coords=geom_coord)
    return geom_EE
# ####################################### START PREPARING THE FEATURE COLLECTION ############################## #
# Load the shapefiles, build the coordinate transformation
eco = ogr.Open(eco_shp)
eco_lyr = eco.GetLayer()
utm = ogr.Open(utm_shp)
utm_lyr = utm.GetLayer()
# Build the output-list
outDS = [["UID", "ECO_ID", "ECO_Name", "Navin_Name", "BIOME", "Prop_in_Navin",
          "F2000_km_th25", "F2000_km_th40", "FL2001_km", "FL2002_km", "FL2003_km", "FL2004_km", "FL2005_km",
          "FL2006_km", "FL2007_km", "FL2008_km", "FL2009_km", "FL2010_km", "FL2011_km", "FL2012_km","FL2013_km",
          "FL2014_km", "FL2015_km", "FL2016_km", "FL2017_km"]]
reprocessList = []
# Lopp through the features of the UTM zome, and then process the polygons
utm_feat = utm_lyr.GetNextFeature()
while utm_feat:
# Get the information from the UTM-Zone --> epsg
    epsg = utm_feat.GetField("EPSG")
    print("Processing polygons for UTM-Zone:", utm_feat.GetField("Zone_Hemi"), ", EPSG-Code:", str(epsg))
# Make a spatial selection in the eco_lyr based on the UTM-Zone, CS is the same in both
    utm_geom = utm_feat.GetGeometryRef()
    eco_lyr.SetSpatialFilter(utm_geom)
    if eco_lyr.GetFeatureCount() == 0:
        print("--> No features detected in this zone, continuing...")
        utm_feat = utm_lyr.GetNextFeature()
    else:
        zone_feats = eco_lyr.GetFeatureCount()
        overallCount = 1
        packageCount = 1
        eco_feat = eco_lyr.GetNextFeature()
        job = []
        while eco_feat:
            if packageCount <= packageSize:# and overallCount <= nFeatures:
        # Get needed properties from the SHP-File
                ecoID = int(eco_feat.GetField("ECO_ID"))
                ecoName = eco_feat.GetField("ECO_NAME")
                navinName = eco_feat.GetField("Class_Name")
                biome = int(eco_feat.GetField("BIOME"))
                prop = format(eco_feat.GetField("AreaRatio"), '.5f')
                UID = eco_feat.GetField("UID")
                ecoGEOM = eco_feat.GetGeometryRef()
        # Intersect with the UTM-Polygon
                ecoGEOM_part = utm_geom.Intersection(ecoGEOM)
        # Build an earth engine feature using the function above, give also UTM-EPSG-code as variable
                try:
                    interEE = Build_EE_polygon(ecoGEOM_part, epsg)
                    eeFeat = ee.Feature(interEE, {"UID": UID, "ECO_ID": ecoID, "ECO_NAME": ecoName, "Navin_Name": navinName, "BIOME": biome, "propAREA": prop})
                    job.append(eeFeat)
                    packageCount += 1
                    overallCount += 1
                    eco_feat = eco_lyr.GetNextFeature()
                except:
                    reprocessList.append(UID)
                    eco_feat = eco_lyr.GetNextFeature()
            else:
        # Process the job by extracting the correpsond values from GEE
                # Convert the feature-List into an GEE-FeatureCollection
                jobCollection = ee.FeatureCollection(ee.List(job))
                # Convert the UTM-Zone polygon into an EE-Feature, so that we can subset the gfc-file
                utm_ee = Build_EE_polygon(utm_geom, 4326)
                epsg_string = 'EPSG:' + str(epsg)
                # Extract the values from GEE
                def ExtractFromGEE(featureCollection):
                    # Get the images, re-project into UTM zone, and subset to area of UTM-polygon
                    gfc = ee.Image(r'UMD/hansen/global_forest_change_2017_v1_5').clip(utm_ee).reproject(crs=epsg_string, scale=30)
                    forest2000 = gfc.select(['treecover2000'])
                    lossYear = gfc.select(['lossyear'])
                    # Do the extraction from GEE for the three varaibles we want --> F25, F40, lossYr
                    processFlag = 0
                    try:
                        # Forest with TC > 25%
                        forMask_25 = forest2000.updateMask(forest2000.gt(25)).remap([0], [0], 1)
                        forest_25 = forMask_25.reduceRegions(reducer=ee.Reducer.sum().weighted(), collection=job, scale=30).getInfo()
                        # Forest with TC > 40%
                        forMask_40 = forest2000.updateMask(forest2000.gt(40)).remap([0], [0], 1)
                        forest_40 = forMask_40.reduceRegions(reducer=ee.Reducer.sum().weighted(), collection=job, scale=30).getInfo()
                        # Loss per year
                        lossYR = lossYear.reduceRegions(reducer=ee.Reducer.frequencyHistogram().weighted(), collection=job, scale=30).getInfo()
                        # Switch the processing flag to 1 if successfully processed
                    except:
                        time.sleep(1)
                        print("--> GEE timed out, idle for 1min, ", time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
                        processFlag = 1
                    # Now take the output from GEE, and create our output for the csv file
                    if processFlag == 0:
                        forest_25 = forest_25['features']
                        forest_40 = forest_40['features']
                        lossYR = lossYR['features']
                        return_list = []
                        for f25, f40, loss in zip(forest_25, forest_40, lossYR):
                            f25_num = f25['properties']
                            f40_num = f40['properties']
                            loss_num = loss['properties']
                            vals = [f25_num['UID'], f25_num['ECO_ID'], f25_num['ECO_NAME'], f25_num['Navin_Name'],
                                    f25_num['BIOME'], f25_num['propAREA'],
                                    format(f25_num['sum'] * 900 / 1000000, '.5f'),
                                    format(f40_num['sum'] * 900 / 1000000, '.5f')]
                            for yr in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15',
                                       '16', '17']:
                                px = loss_num.get(yr)
                                if px == None:
                                    px = 0
                                else:
                                    px = px
                                fl_km = format(px * 900 / 1000000, '.5f')
                                vals.append(fl_km)
                            return_list.append(vals)
                    else:
                        return_list = "Time-Out"
                    return return_list



    # take the last remaining jobs and append them
                featCol_vals = ExtractFromGEE(jobCollection)
                # Append values to outDS if the return from the function is not "Time-Out"
                if not featCol_vals == "Time-Out":
                    for row in featCol_vals:
                        outDS.append(row)
                else:
                # If it is "Time-Out", then append the IDs of this package to the reprocessList
                    errorInfo = jobCollection.getInfo()
                    errorFeats = errorInfo['features']
                    errorFeats = errorFeats['properties']
                    for f in errorFeats:
                        reprocessList.append(f)
                # Reset the job-list and packageCount
                packageCount = 1
                job = []
        # take the last remaining jobs and append them
        jobCollection = ee.FeatureCollection(ee.List(job))
        featCol_vals = ExtractFromGEE(jobCollection)
        # Append values to outDS if the return from the function is not "Time-Out"
        print("Get values")
        if not featCol_vals == "Time-Out":
            print("Values recieved")
            for row in featCol_vals:
                outDS.append(row)
        else:
            # If it is "Time-Out", then append the IDs of this package to the reprocessList
            errorInfo = jobCollection.getInfo()
            errorFeats = errorInfo['features']
            errorFeats = errorFeats['properties']
            for f in errorFeats:
                print(f)
                reprocessList.append(f)
        for out in outDS:
            print(out)
        print("")
        for error in reprocessList:
            print(error)
        #exit(0)
        # Take on next UTM-Zone
        utm_feat = utm_lyr.GetNextFeature()

# Write output
print("Write output")
with open(out_csv, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in outDS:
        writer.writerow(element)
f_open = open(error_file, "w")
for item in reprocessList:
    f_open.write(item + "\n")
f_open.close()
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")