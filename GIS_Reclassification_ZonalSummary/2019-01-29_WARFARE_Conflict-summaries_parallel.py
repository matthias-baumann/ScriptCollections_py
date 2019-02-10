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
    rootFolder = "Z:/Warfare/"
    pol_shp = rootFolder + "_SHPs/BIOMES_TropicsSavannas_10kmGrid_polygons.shp"
    point_shp = rootFolder + "_Variables/CONFLICT_DATA/PRIO/Disaggregated_Data/UCDP Georeferenced Event Dataset (GED) Global version 18.1 (2018)/ged181.shp"
    out_csv = rootFolder + "_DataSummaries/PRIO-summaries_ALL_20190129.csv"

    yrs = range(2000, 2017+1)
    nPackages = 500
    nr_cores = 55
# ####################################### PROCESSING ########################################################## #
# (1) Build job list
    jobList = []
    # Get the number of total features in the shapefile
    eco = ogr.Open(pol_shp)
    ecoLYR = eco.GetLayer()
    nFeat = ecoLYR.GetFeatureCount()
    # Create a list of UIDs and subdivide the into smaller chunks
    featIDs = list(range(1, nFeat+1, 1))
    packageSize = int(nFeat / nPackages)
    #
    feat = ecoLYR.GetNextFeature()
    #featIDs = []
    #while feat:
    #    featIDs.append(feat.GetField('UniqueID'))
    #    feat = ecoLYR.GetNextFeature()
    #ecoLYR.ResetReading()
    #IDlist = set(featIDs)
    IDlist = [featIDs[i * packageSize:(i + 1) * packageSize] for i in range((len(featIDs) + packageSize - 1) // packageSize )]
    #
    # Now build the jobs and append to job list
    for chunk in IDlist:
        job = {'ids': chunk,
               'pol_path': pol_shp,
               'point_path': point_shp,
               'years': yrs}
        jobList.append(job)
# (2) Build Worker_Function
    def SumFunc(job):
    # Prepare the stuff we need for the processing of the data
        # Define the drivers that we need for creating the summaries
        drvMemV = ogr.GetDriverByName('Memory')
        # Load the polygon layer into mem, get the layer and subset by the IDs that are in the chunk
        grids = bt.baumiVT.CopyToMem(job['pol_path'])
        pol_lyr = grids.GetLayer()
        grids_copy = bt.baumiVT.CopyToMem(job['pol_path'])
        pol_lyr_copy = grids_copy.GetLayer()
        idSubs = job['ids']
        pol_lyr.SetAttributeFilter("UniqueID IN {}".format(tuple(idSubs)))
        # Load the conflict layer into memory, get the layer
        conflicts = bt.baumiVT.CopyToMem(job['point_path'])
        conf_lyr = conflicts.GetLayer()
        # Create coordinate transformation rule
        grid_SR = pol_lyr.GetSpatialRef()
        conflict_SR = conf_lyr.GetSpatialRef()
        trans = osr.CoordinateTransformation(grid_SR, conflict_SR)
        # Define the output-list that we want to return
        outList = []
    # Now loop through the selected features in our lyr
        feat = pol_lyr.GetNextFeature()
        while feat:
        # Get the UID from the field
            UID = feat.GetField("UniqueID")
    # Get the geometry, and start running the analyses
            geom = feat.GetGeometryRef()
            # Create a clone of the geometry, transform it to the point-CS, set spatial filter on conflict.lyr
            geom_cl = geom.Clone()
            geom_cl.Transform(trans)
            conf_lyr.SetSpatialFilter(geom_cl)
            # Loop through the years; make in addition thematic selection on the precision (where_prec <= 2)
            for yr in job['years']:
                select_statement = '(where_prec < 3) AND (year = ' + str(yr) + ')'
                conf_lyr.SetAttributeFilter(select_statement)
                # Calculate the statistics we want to gather
        # (1) FOR THIS GRID-CELL ONLY
                # (a) Nr. events
                nr_events = conf_lyr.GetFeatureCount()
                # Calculate the rest only if nr_events > 0, otherwise set to zero
                if nr_events > 0:
                # (b) Nr. fatalities
                    nr_fatalities = 0
                    conf_feat = conf_lyr.GetNextFeature()
                    while conf_feat:
                        deaths = conf_feat.GetField('best')
                        nr_fatalities = nr_fatalities + deaths
                        conf_feat = conf_lyr.GetNextFeature()
                # (c) Is it "conflict" by PRIO-definition --> more than 25 deaths per year
                    if nr_fatalities >= 25:
                        conflict_yn = 1
                    else:
                        conflict_yn = 0
                # (d) Average # fatalities per events
                    if nr_events > 0:
                        fat_per_event = nr_fatalities / nr_events
                    else:
                        fat_per_event = 0
                else:
                    nr_fatalities = 0
                    conflict_yn = 0
                    fat_per_event = 0
                # Reset the reading and remove attribute filter
                conf_lyr.ResetReading()
                conf_lyr.SetAttributeFilter(None)
        # (2): IN THE SURROUNDING CELLS --> strategy: build a buffer around the polygon, then set spatial filter
                geom_cl = geom.Clone()
                ###### V01: 3x3 window ######
                geom_buff = geom_cl.Buffer(1000)
                pol_lyr_copy.SetSpatialFilter(geom_buff)
                # Instantiate the variables we want to calculate (or that we need to calculate others
                nr_events_3x3 = 0
                nr_fatalities_3x3 = 0
                conflict_yn_3x3 = 0
                # Loop through the nighboring polygons
                lyrFEAT = pol_lyr_copy.GetNextFeature()
                nr_neighbors = pol_lyr_copy.GetFeatureCount() - 1
                while lyrFEAT:
                    # Get geometry, buid clone, tansform CS
                    geom_lyrGEOM = lyrFEAT.GetGeometryRef()
                    geom_lyrGEOM_cl = geom_lyrGEOM.Clone()
                    geom_lyrGEOM_cl.Transform(trans)
                    # Set spatial and attribute filter to conflict-lyr based on the polygon
                    conf_lyr.SetSpatialFilter(geom_lyrGEOM_cl)
                    select_statement = '(where_prec < 3) AND (year = ' + str(yr) + ')'
                    conf_lyr.SetAttributeFilter(select_statement)
                    # Get the numbers for this particular conflict by counting the points and then looping over them
                    nr_events_sub = conf_lyr.GetFeatureCount()
                    nr_fatalities_sub = 0
                    # Start looping through the selected conflict features
                    conf_feat_sub = conf_lyr.GetNextFeature()
                    while conf_feat_sub:
                        deaths = conf_feat_sub.GetField('best')
                        nr_fatalities_sub = nr_fatalities_sub + deaths
                        conf_feat_sub = conf_lyr.GetNextFeature()
                    # Add the fatalities from this neighboring grid cell to the overall of the window
                    nr_fatalities_3x3 = nr_fatalities_3x3 + nr_fatalities_sub
                    nr_events_3x3 = nr_events_3x3 + nr_events_sub
                    if nr_fatalities_sub >= 25:
                        conflict_yn_3x3 = conflict_yn_3x3 + 1
                    # Reset the reading and the filter of the conflict layer
                    conf_lyr.ResetReading()
                    conf_lyr.SetAttributeFilter(None)
                    # Take the next neighboring feature
                    lyrFEAT = pol_lyr_copy.GetNextFeature()
                # Calculate the remaining variables
                if nr_neighbors > 0:
                    av_event_3x3 = nr_events_3x3 / nr_neighbors
                    av_fatalities_3x3 = nr_fatalities_3x3 / nr_neighbors
                    prop_conflict_yn_3x3 = conflict_yn_3x3 / nr_neighbors
                else:
                    av_event_3x3 = 0
                    av_fatalities_3x3 = 0
                    prop_conflict_yn_3x3 = 0
                if nr_events_3x3 > 0:
                    fat_per_event_3x3 = nr_fatalities_3x3 / nr_events_3x3
                else:
                    fat_per_event_3x3 = 0
                if prop_conflict_yn_3x3 > 0:
                    conflict_yn_any_3x3 = 1
                else:
                    conflict_yn_any_3x3 = 0
                pol_lyr_copy.ResetReading()

                ###### V02: 5x5 window ######
                geom_buff = geom_cl.Buffer(15000)
                pol_lyr_copy.SetSpatialFilter(geom_buff)
                #print(pol_lyr_copy.GetFeatureCount())
                # Instantiate the variables we want to calculate (or that we need to calculate others
                nr_events_5x5 = 0
                nr_fatalities_5x5 = 0
                conflict_yn_5x5 = 0
                # Loop through the nighboring polygons
                lyrFEAT = pol_lyr_copy.GetNextFeature()
                nr_neighbors = pol_lyr_copy.GetFeatureCount() - 1
                while lyrFEAT:
                    # Get geometry, buid clone, tansform CS
                    geom_lyrGEOM = lyrFEAT.GetGeometryRef()
                    geom_lyrGEOM_cl = geom_lyrGEOM.Clone()
                    geom_lyrGEOM_cl.Transform(trans)
                    # Set spatial and attribute filter to conflict-lyr based on the polygon
                    conf_lyr.SetSpatialFilter(geom_lyrGEOM_cl)
                    select_statement = '(where_prec < 3) AND (year = ' + str(yr) + ')'
                    conf_lyr.SetAttributeFilter(select_statement)
                    # Get the numbers for this particular conflict by counting the points and then looping over them
                    nr_events_sub = conf_lyr.GetFeatureCount()
                    nr_fatalities_sub = 0
                    # Start looping through the selected conflict features
                    conf_feat_sub = conf_lyr.GetNextFeature()
                    while conf_feat_sub:
                        deaths = conf_feat_sub.GetField('best')
                        nr_fatalities_sub = nr_fatalities_sub + deaths
                        conf_feat_sub = conf_lyr.GetNextFeature()
                    # Add the fatalities from this neighboring grid cell to the overall of the window
                    nr_fatalities_5x5 = nr_fatalities_5x5 + nr_fatalities_sub
                    nr_events_5x5 = nr_events_5x5 + nr_events_sub
                    if nr_fatalities_sub >= 25:
                        conflict_yn_5x5 = conflict_yn_5x5 + 1
                    # Reset the reading and the filter of the conflict layer
                    conf_lyr.ResetReading()
                    conf_lyr.SetAttributeFilter(None)
                    # Take the next neighboring feature
                    lyrFEAT = pol_lyr_copy.GetNextFeature()
                # Calculate the remaining variables
                if nr_neighbors > 0:
                    av_event_5x5 = nr_events_5x5 / nr_neighbors
                    av_fatalities_5x5 = nr_fatalities_5x5 / nr_neighbors
                    prop_conflict_yn_5x5 = conflict_yn_5x5 / nr_neighbors
                else:
                    av_event_5x5 = 0
                    av_fatalities_5x5 = 0
                    prop_conflict_yn_5x5 = 0
                if nr_events_5x5 > 0:
                    fat_per_event_5x5 = nr_fatalities_5x5 / nr_events_5x5
                else:
                    fat_per_event_5x5 = 0
                if prop_conflict_yn_5x5 > 0:
                    conflict_yn_any_5x5 = 1
                else:
                    conflict_yn_any_5x5 = 0
                pol_lyr_copy.ResetReading()

                # ###### V03: 7x7 window ######
                # geom_buff = geom_cl.Buffer(29000)
                # pol_lyr_copy.SetSpatialFilter(geom_buff)
                # # Instantiate the variables we want to calculate (or that we need to calculate others
                # nr_events_7x7 = 0
                # nr_fatalities_7x7 = 0
                # conflict_yn_7x7 = 0
                # # Loop through the nighboring polygons
                # lyrFEAT = pol_lyr_copy.GetNextFeature()
                # nr_neighbors = pol_lyr_copy.GetFeatureCount() - 1
                # while lyrFEAT:
                #     # Get geometry, buid clone, tansform CS
                #     geom_lyrGEOM = lyrFEAT.GetGeometryRef()
                #     geom_lyrGEOM_cl = geom_lyrGEOM.Clone()
                #     geom_lyrGEOM_cl.Transform(trans)
                #     # Set spatial and attribute filter to conflict-lyr based on the polygon
                #     conf_lyr.SetSpatialFilter(geom_lyrGEOM_cl)
                #     select_statement = '(where_prec < 3) AND (year = ' + str(yr) + ')'
                #     conf_lyr.SetAttributeFilter(select_statement)
                #     # Get the numbers for this particular conflict by counting the points and then looping over them
                #     nr_events_sub = conf_lyr.GetFeatureCount()
                #     nr_fatalities_sub = 0
                #     # Start looping through the selected conflict features
                #     conf_feat_sub = conf_lyr.GetNextFeature()
                #     while conf_feat_sub:
                #         deaths = conf_feat_sub.GetField('best')
                #         nr_fatalities_sub = nr_fatalities_sub + deaths
                #         conf_feat_sub = conf_lyr.GetNextFeature()
                #     # Add the fatalities from this neighboring grid cell to the overall of the window
                #     nr_fatalities_7x7 = nr_fatalities_7x7 + nr_fatalities_sub
                #     nr_events_7x7 = nr_events_7x7 + nr_events_sub
                #     if nr_fatalities_sub >= 25:
                #         conflict_yn_7x7 = conflict_yn_7x7 + 1
                #     # Reset the reading and the filter of the conflict layer
                #     conf_lyr.ResetReading()
                #     conf_lyr.SetAttributeFilter(None)
                #     # Take the next neighboring feature
                #     lyrFEAT = pol_lyr_copy.GetNextFeature()
                # # Calculate the remaining variables
                # av_event_7x7 = nr_events_7x7 / nr_neighbors
                # av_fatalities_7x7 = nr_fatalities_7x7 / nr_neighbors
                # if nr_events_7x7 > 0:
                #     fat_per_event_7x7 = nr_fatalities_7x7 / nr_events_7x7
                # else:
                #     fat_per_event_7x7 = 0
                # prop_conflict_yn_7x7 = conflict_yn_7x7 / nr_neighbors
                # if prop_conflict_yn_7x7 > 0:
                #     conflict_yn_any_7x7 = 1
                # else:
                #     conflict_yn_any_7x7 = 0
                # pol_lyr_copy.ResetReading()

                # Add to the list we want to store
                vals = [UID, yr, conflict_yn, nr_events, nr_fatalities, format(fat_per_event, '.3f'),
                        conflict_yn_any_3x3, format(prop_conflict_yn_3x3, '.3f'), nr_events_3x3, nr_fatalities_3x3, format(fat_per_event_3x3, '.3f'), format(av_event_3x3, '.3f'), format(av_fatalities_3x3, '.3f'),
                        conflict_yn_any_5x5, format(prop_conflict_yn_5x5, '.3f'), nr_events_5x5, nr_fatalities_5x5, format(fat_per_event_5x5, '.3f'), format(av_event_5x5, '.3f'), format(av_fatalities_5x5, '.3f')]#,
                        #conflict_yn_any_7x7, format(prop_conflict_yn_7x7, '.3f'), nr_events_7x7, nr_fatalities_7x7, format(fat_per_event_7x7, '.3f'), format(av_event_7x7, '.3f'), format(av_fatalities_7x7, '.3f')]
            # Append the values to the output-DS
                outList.append(vals)
            # after all years are processed, take the next feature
            feat = pol_lyr.GetNextFeature()
    # return the outList as output from the function
        return outList
# (3) Execute the Worker_Funtion parallel
    job_results = Parallel(n_jobs=nr_cores)(delayed(SumFunc)(i) for i in tqdm(jobList))
    #for job in jobList:
    #   list = SumFunc(job)
# (4) Merge the different packages back together into one dataset, instantiate colnames first
    print("Merge Outputs")
    outDS = [["PolygonID", "Year",
              "Conflict_YN", "nr_events", "nr_fatalities", "nr_fatalities_per_event", # Summaries at the location itself
              "Conflict_YN_any_3x3", "Conflict_YN_prop_3x3", "nr_events_3x3", "nr_fatalities_3x3", "fat_per_event_3x3", "av_nr_events_3x3", "av_nr_fatalities_3x3",
              "Conflict_YN_any_5x5", "Conflict_YN_prop_5x5", "nr_events_5x5", "nr_fatalities_5x5", "fat_per_event_5x5", "av_nr_events_5x5", "av_nr_fatalities_5x5"]]#,
              #"Conflict_YN_any_7x7", "Conflict_YN_prop_7x7", "nr_events_7x7", "nr_fatalities_7x7", "fat_per_event_7x7", "av_nr_events_7x7", "av_nr_fatalities_7x7"]]
    # Now extract the information from all the evaluations
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