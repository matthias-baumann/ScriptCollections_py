# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os, csv
import time
import gdal, osr, ogr
import numpy as np
import baumiTools as bt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from joblib import Parallel, delayed
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
if __name__ == '__main__':
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES FOR PROCESSING ##################### #
    rootFolder = "L:/_SHARED_DATA/AB_MB/"
    point_shp = rootFolder + "TDFsSAcut_grid_3kmpoint_EPSG54009.shp"
    eco_shp = rootFolder + "OlsonbasedSA_prj.shp"
    out_csv = rootFolder + "TDFsSAcut_grid_3kmpoint_EPSG54009_summary_Hansen-th10_20200813.csv"
    forest = "D:/baumamat/Warfare/_Variables/Forest/Forest2000.vrt"
    gain = "D:/baumamat/Warfare/_Variables/Forest/Gain.vrt"
    loss = "D:/baumamat/Warfare/_Variables/Forest/LossYear.vrt"
    uid_field = "Id"
    epsg_to = 54009 # Mollweide
    nPackages = 10000
    nr_cores = 25
# ####################################### PROCESSING ########################################################## #
# (1) Build job list
    jobList = []
    # Get the number of total features in the shapefile
    eco = ogr.Open(point_shp)
    ecoLYR = eco.GetLayer()
    nFeat = ecoLYR.GetFeatureCount()
    # Create a list of UIDs and subdivide the into smaller chunks
    featIDs = list(range(1, nFeat+1, 1))
    packageSize = int(nFeat / nPackages)
    IDlist = [featIDs[i * packageSize:(i + 1) * packageSize] for i in range((len(featIDs) + packageSize - 1) // packageSize )]
    # Now build the jobs and append to job list
    for chunk in IDlist:
        job = {'ids': chunk,
               'shp_path': point_shp,
               'epsg': epsg_to,
               'forest_raster': forest,
               'gain_raster': gain,
               'loss_raster': loss,
               'id': uid_field,
               'ecoregions': eco_shp}
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
        lyr.SetAttributeFilter("Id IN {}".format(tuple(idSubs)))
        # Load the ecoregion shapefile into memory
        ecoSHP = bt.baumiVT.CopyToMem(job['ecoregions'])
        ecoLYR = ecoSHP.GetLayer()
        # Create coordinate transformation rule
        point_SR = lyr.GetSpatialRef()
        #print(point_SR)
        #time.sleep(1)
        #point_SR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        #target_SR = osr.SpatialReference()
        #target_SR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        #target_SR.ImportFromEPSG(job['epsg'])
        #print(target_SR)
        #exit(0)
        #trans = osr.CoordinateTransformation(point_SR, target_SR)
        # Define the output pandas dataframe
        out_PD = pd.DataFrame(columns=['id_3000', 'x_3000', 'y_3000', 'id_1500', 'x_1500', 'y_1500', 'id_300', 'x_300', 'y_300',
                 'F2000_km', 'FL_2001_km', 'FL_2002_km', 'FL_2003_km', 'FL_2004_km', 'FL_2005_km', 'FL_2006_km',
                 'FL_2007_km', 'FL_2008_km', 'FL_2009_km', 'FL_2010_km', 'FL_2011_km', 'FL_2012_km', 'FL_2013_km',
                 'FL_2014_km', 'FL_2015_km', 'FL_2016_km', 'FL_2017_km', 'FL_2018_km', 'FL_2019_km', 'ECO_ID', 'BIOME_NUM'])
        # Now loop through the selected features in our lyr
        feat = lyr.GetNextFeature()
        while feat:
    # Get needed properties from the SHP-File, the take geometry, and transform to Target-EPSG
            # Ecoregion / BIOME Info
            pointID = int(feat.GetField(job['id']))
    # Instantiate output and take the geometry of the feature
            geom = feat.GetGeometryRef()
            #geom.Transform(trans)
    # Extract the information about the ecoregion from the shapefile
            ecoLYR.SetSpatialFilter(geom)
            ecoFEAT = ecoLYR.GetNextFeature()
            eco_num = ecoFEAT.GetField('OBJECTID')
            biome_num = ecoFEAT.GetField('BIOME_NUM')
            #biom_name = ecoFEAT.GetField('BIOME_NAME')
            ecoLYR.ResetReading()
            ecoLYR.SetSpatialFilter(None)
    # Build square of point --> 1500m into x&y-direction needs to be adjusted
            geom_x, geom_y = geom.GetX(), geom.GetY()
            #geom_x, geom_y = geom.GetY(), geom.GetX()
            square = ogr.Geometry(ogr.wkbLinearRing)
            square.AddPoint(geom_x - 1500, geom_y - 1500)
            square.AddPoint(geom_x - 1500, geom_y + 1500)
            square.AddPoint(geom_x + 1500, geom_y + 1500)
            square.AddPoint(geom_x + 1500, geom_y - 1500)
            square.AddPoint(geom_x - 1500, geom_y - 1500)
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(square)
    # Rasterize the new geometry, pixelSize is 30m, because we work with Landsat forest loss data
        # Create new SHP-file in memory to which we copy the geometry
            geom_shp = drvMemV.CreateDataSource('')
            geom_lyr = geom_shp.CreateLayer('geom', point_SR, geom_type=ogr.wkbMultiPolygon)
            geom_lyrDefn = geom_lyr.GetLayerDefn()
            geom_feat = ogr.Feature(geom_lyrDefn)
            geom_feat.SetGeometry(poly)
            geom_lyr.CreateFeature(geom_feat)
            #bt.baumiVT.CopySHPDisk(geom_shp, rootFolder + "px.shp")
        # Calculate the extent of the polygon, so that we know how large the raster should become
            x_min, x_max, y_min, y_max = geom_lyr.GetExtent()
            x_res = int((x_max - x_min) / 30)
            y_res = int((y_max - y_min) / 30)
        # Create an empty raster
            geom_ras = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
            geom_ras.SetProjection(point_SR.ExportToWkt())
            geom_ras.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
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
            #bt.baumiRT.CopyMEMtoDisk(forest, rootFolder + "forest.tif")
            #bt.baumiRT.CopyMEMtoDisk(loss, rootFolder + "loss.tif")
            #exit(0)
        # Open all rasters into np-Arrays
            geom_np = geom_ras.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
            forest_np = forest.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
            loss_np = loss.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
        # Calculate the summaries for the finest resolution
            # Part I: Forest
            forest_np_25 = np.where((geom_np == 1) & (forest_np >= 10), 1, 0)
            forest_np_25 = forest_np_25.astype(np.uint8)
            def blockshaped(arr, nrows, ncols):
                """
                Return an array of shape (n, nrows, ncols) where
                n * nrows * ncols = arr.size
                If arr is a 2D array, the returned array should look like n subblocks with
                each subblock preserving the "physical" layout of arr.
                source: https://stackoverflow.com/questions/16856788/slice-2d-array-into-smaller-2d-arrays
                """
                h, w = arr.shape
                assert h % nrows == 0, "{} rows is not evenly divisble by {}".format(h, nrows)
                assert w % ncols == 0, "{} cols is not evenly divisble by {}".format(w, ncols)
                return (arr.reshape(h // nrows, nrows, -1, ncols)
                        .swapaxes(1, 2)
                        .reshape(-1, nrows, ncols))
            # Subdivide the large forest array into small arrays --> Order is row by row from left to right
            forest_np_25_300 = blockshaped(forest_np_25, 10, 10).reshape((100, 100))
            f25_300 = np.sum(forest_np_25_300, axis=1) * 30 * 30 / 1000000
            f25_300 = f25_300.reshape((100,1))
            # Part II: Forest loss per year
            loss_np_forest = np.where((geom_np == 1) & (loss_np > 0) & (forest_np_25 == 1), loss_np, 0)
            loss_np_forest_300 = blockshaped(loss_np_forest, 10, 10).reshape((100, 100))
            lossYr_300 = np.zeros((100, 19), np.float32)
            for yr in range(1, 20, 1):
                loss_np_yr = np.where((loss_np_forest_300 == yr), 1, 0)
                loss_np_yr = loss_np_yr.astype(np.uint8)
                loss_yr = np.sum(loss_np_yr, axis=1) * 30 * 30 / 1000000
                lossYr_300[:, yr-1] = loss_yr
        # Create ID's and coordinates
            # Part I: the Identifiers
            id_3000 = (np.ones((100)) * pointID).astype(np.uint32).reshape((100,1))
            id_1500 = np.concatenate(
                (np.concatenate((np.full((5,5), pointID+0.1), np.full((5,5), pointID+0.2)), axis=1).astype(np.float).flatten(),
                np.concatenate((np.full((5,5), pointID+0.3), np.full((5,5), pointID+0.4)), axis=1).astype(np.float).flatten())).reshape((100,1))
            id_300 = np.concatenate(
                (np.tile((np.arange(1, 26).reshape(5, 5)), 2).astype(np.uint32).flatten(),
                 np.tile((np.arange(1, 26).reshape(5, 5)), 2).astype(np.uint32).flatten())).reshape((100,1))
            id_300 = id_1500 + (id_300 / 1000) # to create an ID that matches the hierachy
            # Part II: Coordinates
            x_3000 = np.full((100,1), geom_x)
            y_3000 = np.full((100,1), geom_y)
            x_1500 = np.concatenate(
                (np.concatenate((np.full((5,5), geom_x - 750), np.full((5,5), geom_x + 750)), axis=1).flatten(),
                np.concatenate((np.full((5, 5), geom_x - 750), np.full((5, 5), geom_x + 750)), axis=1).flatten())).reshape((100,1))
            y_1500 = np.concatenate((np.full((5,10), geom_y+750), np.full((5,10), geom_y-750))).reshape((100,1))#.flatten()
            x_300 = np.tile(np.linspace(geom_x - 1350, geom_x + 1350, 10), 10).reshape((100,1))#.flatten()
            y_300 = np.repeat(np.linspace(geom_y + 1350, geom_y - 1350, 10).reshape((10,1)), 10, axis=1).reshape((100,1))#.flatten()
            # Part III: Information on ecoregion
            ecoID = np.repeat(eco_num, 100).reshape((100,1))
            biomeID = np.repeat(biome_num, 100).reshape((100,1))
        # Put them all together into a pandas data frame
            df = pd.DataFrame(np.concatenate([id_3000, x_3000, y_3000, id_1500, x_1500, y_1500, id_300, x_300, y_300, f25_300, lossYr_300, ecoID, biomeID], axis=1),
                              columns=['id_3000', 'x_3000', 'y_3000', 'id_1500', 'x_1500', 'y_1500', 'id_300', 'x_300', 'y_300',
                                       'F2000_km', 'FL_2001_km', 'FL_2002_km', 'FL_2003_km', 'FL_2004_km', 'FL_2005_km', 'FL_2006_km',
                                       'FL_2007_km', 'FL_2008_km', 'FL_2009_km', 'FL_2010_km', 'FL_2011_km', 'FL_2012_km', 'FL_2013_km',
                                       'FL_2014_km', 'FL_2015_km', 'FL_2016_km', 'FL_2017_km', 'FL_2018_km', 'FL_2019_km','ECO_ID', 'BIOME_NUM'])
            # Merge the data.frame to the output data frame
            out_PD = pd.concat([out_PD, df])
            # For testing: convert the data frame into a point shapefile
            #df['geometry'] = df.apply(lambda x: Point((float(x.x_300), float(x.y_300))), axis=1)
            #geopandasDF = gpd.GeoDataFrame(df, geometry='geometry')
            #geopandasDF.crs = point_SR.ExportToProj4()
            #geopandasDF.to_file(rootFolder + 'test.shp', driver='ESRI Shapefile')
            #exit(0)
        # take the next feature
            feat = lyr.GetNextFeature()
    # return the outList as output from the function
        return out_PD
# (3) Execute the Worker_Funtion parallel
    job_results = Parallel(n_jobs=nr_cores)(delayed(SumFunc)(i) for i in tqdm(jobList))
    #for job in jobList:
    #    df = SumFunc(job)
    #    exit(0)
# (4) Merge the different packages back together into one dataset, write to csv
    print("Merge Outputs")
    outDS = pd.concat(job_results)
    # Create a uniqueID column
    outDS['UniqueID'] = np.arange(len(outDS)) + 1
    #outDS['geometry'] = outDS.apply(lambda x: Point((float(x.x_300), float(x.y_300))), axis=1)
    #geopandasDF = gpd.GeoDataFrame(outDS, geometry='geometry')
    #target_SR = osr.SpatialReference()
    #target_SR.ImportFromEPSG(epsg_to)
    #geopandasDF.crs = target_SR.ExportToProj4()
    #geopandasDF.to_file(rootFolder + 'parallel_test.shp', driver='ESRI Shapefile')
    print("write entire Dataset to disc")
    outDS.to_csv(out_csv, encoding='utf-8', index=False, sep=",")
    print("Write files per ecoregion to disc")
    for eco, df_eco in outDS.groupby('ECO_ID'):
        outname = rootFolder + "TDFsSAcut_grid_3kmpoint_EPSG54009_summary_Hansen-th10_20190810_ECO_ID_" + str(eco) + ".csv"
        df_eco.to_csv(outname, encoding='utf-8', index=False, sep=",")




# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")