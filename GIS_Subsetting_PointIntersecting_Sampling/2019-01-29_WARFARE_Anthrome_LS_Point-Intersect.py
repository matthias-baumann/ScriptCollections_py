# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
import ogr, osr
from gdalconst import *
import struct
import csv
import baumiTools as bt
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
    rootFolder = "D:/baumamat/Warfare/"
    points = rootFolder + "_SHPs/uniqueID_country_Biome.shp"
    out_file = rootFolder + "uniqueID_country_Biome_LS_Anthrome_20190130.csv"
    anthromes = rootFolder + "_Variables/LandSystems_Anthromes/2000/anthro2_a2000.tif"
    nPackages = 300
    nr_cores = 30
# ####################################### PROCESSING ########################################################## #
# (1) Build job list
    jobList = []
    # Get the number of total features in the shapefile
    ps = ogr.Open(points)
    psLYR = ps.GetLayer()
    nFeat = psLYR.GetFeatureCount()
    # Create a list of UIDs and subdivide the into smaller chunks
    featIDs = list(range(1, nFeat+1, 1))
    packageSize = int(nFeat / nPackages)
    IDlist = [featIDs[i * packageSize:(i + 1) * packageSize] for i in range((len(featIDs) + packageSize - 1) // packageSize )]
    # Now build the jobs and append to job list
    for chunk in IDlist:
        job = {'ids': chunk,
               'point_path': points,
               'raster_path': anthromes}
        jobList.append(job)
# (2) Build Worker_Function
    def WorkFunc(job):
    # Prepare the stuff we need for the processing of the data
        # Define the drivers that we need for creating the summaries
        drvMemV = ogr.GetDriverByName('Memory')
        # Load the polygon layer into mem, get the layer and subset by the IDs that are in the chunk
        pts = bt.baumiVT.CopyToMem(job['point_path'])
        pts_lyr = pts.GetLayer()
        idSubs = job['ids']
        pts_lyr.SetAttributeFilter("UniqueID IN {}".format(tuple(idSubs)))
        # Now get the raster information
        ras = bt.baumiRT.OpenRasterToMemory(job['raster_path'])
        pr = ras.GetProjection()
        gt = ras.GetGeoTransform()
        rb = ras.GetRasterBand(1)
        rasdType = bt.baumiRT.GetDataTypeHexaDec(rb.DataType)
        # Create coordinate transformation for point
        source_SR = pts_lyr.GetSpatialRef()
        target_SR = osr.SpatialReference()
        target_SR.ImportFromWkt(pr)
        cT = osr.CoordinateTransformation(source_SR, target_SR)
        # now loop over the features and extract the point at the location of the raster
        outList = []
        feat = pts_lyr.GetNextFeature()
        while feat:
            # Retrieve the infos from the attribute table
            id = feat.GetField("UniqueID")
            gid0 = feat.GetField("GID_0")
            id0 = feat.GetField("ID_0")
            name0 = feat.GetField("NAME_0")
            pt_x = feat.GetField("POINT_X")
            pt_y = feat.GetField("POINT_Y")
            biome = feat.GetField("BIOME")
            ecoNr = feat.GetField("ECO_NUM")
            lsKehoe = feat.GetField("LS_Kehoe")
            if lsKehoe < 0:
                lsKehoe = -999
            else:
                lsKehoe = lsKehoe
            lsVanAss = feat.GetField("LS_vanAss")
            # Now extact the point from the rast
            geom = feat.GetGeometryRef()
            geom_cl = geom.Clone()
            geom_cl.Transform(cT)
            mx, my = geom_cl.GetX(), geom_cl.GetY()
            # Extract raster value
            px = int((mx - gt[0]) / gt[1])
            py = int((my - gt[3]) / gt[5])
            structVar = rb.ReadRaster(px, py, 1, 1)
            Val = struct.unpack(rasdType, structVar)[0]
            values = [id, gid0, id0, name0, pt_x, pt_y, biome, ecoNr, lsKehoe, lsVanAss, Val]
            # Take next feature
            outList.append(values)
            feat = pts_lyr.GetNextFeature()
        return outList
# (3) Execute the Worker_Funtion parallel
    job_results = Parallel(n_jobs=nr_cores)(delayed(WorkFunc)(i) for i in tqdm(jobList))
    #for job in jobList:
    #   list = SumFunc(job)
# (4) Merge the different packages back together into one dataset, instantiate colnames first
    print("Merge Outputs")
    outDS = [["UniqueID", "GID_0", "ID_0", "NAME_0", "POINT_X", "POINT_Y", "BIOME", "ECO_NUM", "LS_Kehoe", "LS_vanAss", "Anthrome"]]
    # Now extract the information from all the evaluations
    # 1st loop --> the different chunks
    for result in job_results:
        # 2nd loop --> all outputs in each chunk
        for out in result:
            outDS.append(out)
# (5) Write all outputs to disc
    print("Write output")
    with open(out_file, "w") as theFile:
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