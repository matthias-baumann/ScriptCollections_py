# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os, csv
import time
import gdal, osr, ogr
import numpy as np
import baumiTools as bt
from joblib import Parallel, delayed
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
if __name__ == '__main__':
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES FOR PROCESSING ##################### #
    rootFolder = "P:/"
    eco_shp = rootFolder + "data/Olson-Ramankutty_Intersection_SinglePart/WWF_potentialVeg_intersect_single_1degree_UN_GADM.shp"
    out_csv = rootFolder + "data/results/Hansen_Summaries_ALL_th25_20190628.csv"
    forest = "D:/baumamat/Warfare/_Variables/Forest/Forest2000.vrt"
    gain = "D:/baumamat/Warfare/_Variables/Forest/Gain.vrt"
    loss = "D:/baumamat/Warfare/_Variables/Forest/LossYear.vrt"
    PAs = rootFolder + "data/WDPA/WDPA_May2019-shapefile-polygons.shp"
    epsg_to = 54009 # Mollweide
    nPackages = 300
    nr_cores = 40
# ####################################### PROCESSING ########################################################## #
# (1) Build job list
    jobList = []
    # Get the number of total features in the shapefile
    eco = ogr.Open(eco_shp)
    ecoLYR = eco.GetLayer()
    nFeat = ecoLYR.GetFeatureCount()
    # Create a list of UIDs and subdivide the into smaller chunks
    featIDs = list(range(1,nFeat+1, 1))
    packageSize = int(nFeat / nPackages)
    IDlist = [featIDs[i * packageSize:(i + 1) * packageSize] for i in range((len(featIDs) + packageSize - 1) // packageSize )]
    # Now build the jobs and append to job list
    for chunk in IDlist:
        job = {'ids': chunk,
               'shp_path': eco_shp,
               'epsg': epsg_to,
               'forest_raster': forest,
               'gain_raster': gain,
               'loss_raster': loss,
               'PA_shape': PAs}
        jobList.append(job)
# (2) Build Worker_Function
    def SumFunc(job):
    # Define the drivers that we need for creating the summaries
        drvMemV = ogr.GetDriverByName('Memory')
        drvMemR = gdal.GetDriverByName('MEM')
        # Load the shapefile into mem, get the layer and subset by the IDs that are in the chunk
        shpMem = bt.baumiVT.CopyToMem(job['shp_path'])
        lyr = shpMem.GetLayer()
        idSubs = job['ids']
        #lyr.SetAttributeFilter("UID_GridID IN {}".format(tuple(idSubs)))
        lyr.SetAttributeFilter("UID_GID_GA IN {}".format(tuple(idSubs)))
        # Create coordinate transformation rule
        eco_SR = lyr.GetSpatialRef()
        target_SR = osr.SpatialReference()
        target_SR.ImportFromEPSG(job['epsg'])
        trans = osr.CoordinateTransformation(eco_SR, target_SR)
        # Open the WDPA, build coordinate transformation here as well
        #wdpa = ogr.Open(job['PA_shape'])
        wdpa = bt.vectorTools.CopyToMem(job['PA_shape'])
        wdpa_lyr = wdpa.GetLayer()
        wdpa_trans = osr.CoordinateTransformation(eco_SR, wdpa_lyr.GetSpatialRef())
        # Define the output-list that we want to return
        outList = []
        # Now loop through the selected features in our lyr
        feat = lyr.GetNextFeature()
        while feat:
    # Get needed properties from the SHP-File, the take geometry, and transform to Target-EPSG
            # Ecoregion / BIOME Info
            ecoID = int(feat.GetField("ECO_ID"))
            ecoName = feat.GetField("ECO_NAME")
            navinName = feat.GetField("Class_Name")
            biome = int(feat.GetField("BIOME"))
            prop = format(feat.GetField("AreaRatio"), '.5f')
            UID = feat.GetField("UID")
            UID_GridID = feat.GetField("UID_GID_GA")
            country = feat.GetField("NAME_0")
            countryISO = feat.GetField("ISO3")
    # Instantiate output and take the geometry of the feature, transform it to our epsg
            vals = [UID_GridID, UID, ecoID, ecoName, navinName, biome, prop, country, countryISO]
            geom = feat.GetGeometryRef()
            geom_cl = geom.Clone()
            geom.Transform(trans)
    # Rasterize the geometry, pixelSize is 30m
        # Create new SHP-file in memory to which we copy the geometry
            geom_shp = drvMemV.CreateDataSource('')
            geom_lyr = geom_shp.CreateLayer('geom', target_SR, geom_type=ogr.wkbMultiPolygon)
            geom_lyrDefn = geom_lyr.GetLayerDefn()
            geom_feat = ogr.Feature(geom_lyrDefn)
            geom_feat.SetGeometry(geom)
            geom_lyr.CreateFeature(geom_feat)
        # Check if the geometry we are processing is larger than 1x1 pixel
            x_min, x_max, y_min, y_max = geom_lyr.GetExtent()
            x_res = int((x_max - x_min) / 30)
            y_res = int((y_max - y_min) / 30)
        # Do the rest of the operation for this polygon only if x_res and y_res are >= 1
            if x_res > 0 and y_res > 0:
                geom_ras = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
                geom_ras.SetProjection(target_SR.ExportToWkt())
                geom_ras.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
                #geom_rb = geom_ras.GetRasterBand(1)
                gdal.RasterizeLayer(geom_ras, [1], geom_lyr, burn_values=[1])
            # Reproject the Hansen-Rasters "into" the geometry-raster
                def ReprojectRaster(valRaster, GEOMraster):
                    vasRaster_sub = drvMemR.Create('', GEOMraster.RasterXSize, GEOMraster.RasterYSize, 1, gdal.GDT_Byte)
                    vasRaster_sub.SetGeoTransform(GEOMraster.GetGeoTransform())
                    vasRaster_sub.SetProjection(GEOMraster.GetProjection())
                    gdal.ReprojectImage(valRaster, vasRaster_sub, valRaster.GetProjection(), GEOMraster.GetProjection(), gdal.GRA_NearestNeighbour)
                    return vasRaster_sub
                forest = ReprojectRaster(gdal.Open(job['forest_raster']), geom_ras)
                loss = ReprojectRaster(gdal.Open(job['loss_raster']), geom_ras)
                gain = ReprojectRaster(gdal.Open(job['gain_raster']), geom_ras)
                #bt.baumiRT.CopyMEMtoDisk(geom_ras, rootFolder + "mask.tif")
                #bt.baumiRT.CopyMEMtoDisk(forest, rootFolder+"forest.tif")
                #bt.baumiRT.CopyMEMtoDisk(loss, rootFolder + "loss.tif")
                #bt.baumiRT.CopyMEMtoDisk(gain, rootFolder + "gain.tif")
            # Open all rasters into np-Arrays
                geom_np = geom_ras.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
                forest_np = forest.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
                loss_np = loss.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
                gain_np = gain.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
            # Now extract the summaries
                # Forest 2000 --> 25% canopy
                forest_np_25 = np.where((geom_np == 1) & (forest_np >= 25), 1, 0)
                forest_np_25 = forest_np_25.astype(np.uint8)
                f25 = forest_np_25.sum() * 30 * 30 / 1000000
                vals.append(format(f25, '.5f'))
                # Loss per year
                for yr in range(1, 19, 1):
                    loss_np_yr = np.where((geom_np == 1) & (loss_np == yr) & (forest_np_25 == 1), 1, 0)
                    loss_np_yr = loss_np_yr.astype(np.uint8)
                    loss_yr = loss_np_yr.sum() * 30 * 30 / 1000000
                    vals.append(format(loss_yr, '.5f'))
                # gain
                gain_np_mask = np.where((geom_np == 1) & (gain_np == 1) & (forest_np_25 == 1), 1, 0)
                gain_np_mask = gain_np_mask.astype(np.uint8)
                gn = gain_np_mask.sum() * 30 * 30 / 1000000
                vals.append(format(gn, '.5f'))
            # Calculate the array of forest area in last year -->
                forest_np_2018 = np.where((forest_np_25 == 1) & (loss_np == 0), 1, 0)
                forest_np_2018 = forest_np_2018.astype(np.uint8)
                forest_np_2018_area = forest_np_2018.sum() * 30 * 30 / 1000000
                vals.append(format(forest_np_2018_area, '.5f'))
            # Now rasterize the PA-layer
                # Set First a spatial filter
                geom_cl.Transform(wdpa_trans)
                wdpa_lyr.SetSpatialFilter(geom_cl)
                # Loop through the categories --> Ia, Ib, II, III, IV, V, VI
                for cat in ['Ia', 'Ib', 'II', 'III', 'IV', 'V', 'VI']:
                    #print(cat)
                    #wdpa_lyr.SetAttributeFilter("STATUS IN ('Designated', 'Established') AND IUCN_CAT IN ('Ia', 'Ib', 'II', 'III', 'IV', 'V', 'VI')")
                    clause = "STATUS IN ('Designated', 'Established') AND IUCN_CAT IN ('" + cat + "')"
                    wdpa_lyr.SetAttributeFilter(clause)
                    if wdpa_lyr.GetFeatureCount() > 0:
                        wdpa_ras = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
                        wdpa_ras.SetProjection(target_SR.ExportToWkt())
                        wdpa_ras.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
                        gdal.RasterizeLayer(wdpa_ras, [1], wdpa_lyr, burn_values=[1])#, options=['ATTRIBUTE=IUCN_CAT'])
                        #bt.baumiRT.CopyMEMtoDisk(wdpa_ras, rootFolder + "wdpa.tif")
                        # Load the new raster to np-arry, do the calculation
                        wdpa_cat = wdpa_ras.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
                        forest18_wdpa_cat = np.where((forest_np_2018 == 1) & (wdpa_cat == 1), 1, 0)
                        forest18_wdpa_cat = forest18_wdpa_cat.astype(np.uint8)
                        forest18_wdpa_cat_area = forest18_wdpa_cat.sum() * 30 * 30 / 1000000
                        #print(forest18_wdpa_cat_area)
                        vals.append(format(forest18_wdpa_cat_area, '.5f'))
                        wdpa_lyr.SetAttributeFilter(None)
                    else:
                        vals.append(0)
                # Remove the spatial filter
                wdpa_lyr.SetSpatialFilter(None)
        # If the polygon is < 1px in x- and y-direction, then write zeros for everything
            else:
                vals.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        # Append the values to the output-DS, then take the next feature
            outList.append(vals)
            feat = lyr.GetNextFeature()
    # return the outList as output from the function
        return outList
# (3) Execute the Worker_Funtion parallel
    job_results = Parallel(n_jobs=nr_cores)(delayed(SumFunc)(i) for i in tqdm(jobList))
    #for job in jobList:
    #   list = SumFunc(job)
# (4) Merge the different packages back together into one dataset, instantiate colnames first
    print("Merge Outputs")
    outDS = [["UID_GridID_GA", "UID", "ECO_ID", "ECO_Name", "Navin_Name", "BIOME", "Prop_in_Navin", "Country_Name", "Country_ISO3",
              "F2000_km_th25", "FL2001_km", "FL2002_km", "FL2003_km", "FL2004_km", "FL2005_km",
              "FL2006_km", "FL2007_km", "FL2008_km", "FL2009_km", "FL2010_km", "FL2011_km", "FL2012_km","FL2013_km",
              "FL2014_km", "FL2015_km", "FL2016_km", "FL2017_km", "FL2018_km", "Gain_km", "F2018_km_h25",
              "F2018_km_th25_IUCN-Ia", "F2018_km_th25_IUCN-Ib", "F2018_km_th25_IUCN-II", "F2018_km_th25_IUCN-III", "F2018_km_th25_IUCN-IV", "F2018_km_th25_IUCN-V", "F2018_km_th25_IUCN-VI"]]
    # Now extract the information from all the evaluations
    #exit(0)
    # 1st loop --> the different chunks
    for result in job_results:
        # 2nd loop --> all outputs in each chunk
        for out in result:
            outDS.append(out)
# (5) Write all outputs to disc
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