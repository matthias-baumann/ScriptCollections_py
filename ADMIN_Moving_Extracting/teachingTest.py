from osgeo import ogr, osr
import sys
import os
import pandas as pd

wd = "D:/_TEACHING/__Classes-Modules_HUB/MSc-M8_Geoprocessing-with-python/Week08 - Combining Vector and raster - zonal summary/Assignment08/Assignment08_data/"

### Get data
parcels_shp = ogr.Open(wd + 'Parcels.shp', 1)
if parcels_shp is None:
    sys.exit('Could not open Parcels.shp - Output is empty.')
else: parcels = parcels_shp.GetLayer('parcels')
publicLands_shp = ogr.Open(wd + 'PublicLands.shp', 1)
if publicLands_shp is None:
    sys.exit('Could not open PublicLands.shp - Output is empty.')
else: publicLands = publicLands_shp.GetLayer()
roads_shp = ogr.Open(wd + 'Roads.shp', 1)
if roads_shp is None:
    sys.exit('Could not open Roads.shp - Output is empty.')
else: roads = roads_shp.GetLayer()
thp_shp = ogr.Open(wd + 'TimberHarvestPlan.shp', 1)
if thp_shp is None:
    sys.exit('Could not open TimberHarvestPlan.shp - Output is empty.')
else: thp = thp_shp.GetLayer()
grows_shp = ogr.Open(wd + 'Marihuana_Grows.shp', 1)
if grows_shp is None:
    sys.exit('Could not open Marihuana_Grows.shp - Output is empty.')
else: grows = grows_shp.GetLayer()

### Create empty data dictionary
data_list = {'Parcel_APN': [],
             'Nr_GH-plants': [],
             'Nr_OD-plants': [],
             'Dist_to_grow_m': [],
             'km_privateRoad': [],
             'km_localRoad': [],
             'PublicLand-YN': [],
             'Prop_in_THP': []
             }

### Union single TimberHarvestPlan features to one single geometry so that intersection area can be calculated
### Compare to other method in which  respective intersection areas are summed up
# --> DIFFERENT RESULTS !!!! WHY ???? (Because THP features overlap?! Do they?)
geom_allTHP = ogr.Geometry(ogr.wkbPolygon)
THP_area_list = []
for THP in thp:
    geom_THP = THP.geometry().Clone()
    print("Respective THP polygon area: ", geom_THP.Area())
    geom_allTHP = geom_allTHP.Union(geom_THP)
    THP_area = geom_THP.Area()
    THP_area_list.append(THP_area)
    print(sum(THP_area_list))
    print(geom_allTHP.Area())
print("THP area summed up: ", sum(THP_area_list))
print("THP area union method: ", geom_allTHP.Area())
thp.ResetReading()

parcels.ResetReading()

for parcel in parcels:
    ### Reproject geometry to grows' spatial reference ###
    geom = parcel.geometry().Clone()
    geom_repr = parcel.geometry().Clone()
    # print("Spatial Reference before transformation: ", geom.GetSpatialReference())
    geom_repr.Transform(osr.CoordinateTransformation(parcels.GetSpatialRef(), grows.GetSpatialRef()))
    # print("Spatial Reference after transformation: ", geom.GetSpatialReference())

    # ##############  Number of cannabis plants in each parcel  ##############
    # grows.SetSpatialFilter(geom_repr) # only for layer 'grows' because it's the only one in a different spatial reference system!!
    # print("#####################", parcel.GetField('APN'), "#####################")
    # data_list['Parcel_APN'].append(parcel.GetField('APN'))
    # print("Total grows in parcel: ", grows.GetFeatureCount())
    # g_plants = 0
    # o_plants = 0
    # # g_plants_tmp = 0
    # # o_plants_tmp = 0
    # for grow in grows:
    #     g_plants += grow.GetField('g_plants')
    #     # print("GH plants: ", g_plants)
    #     #g_plants_tmp = g_plants_tmp + g_plants
    #     o_plants += grow.GetField('o_plants')
    #     # print('Outdoor plants: ', o_plants)
    #     # o_plants_tmp = o_plants_tmp + o_plants
    # print("GH plants per parcel: ", g_plants)
    # data_list['Nr_GH-plants'].append(g_plants)
    # print("Outdoor plants per parcel: ", o_plants)
    # data_list['Nr_OD-plants'].append(o_plants)
    # grows.SetSpatialFilter(None)
    # grows.ResetReading()
	#
    # ##############  Distance between parcel and next grow  ##############
    # grows.SetSpatialFilter(geom_repr)
    # featuresWithinParcel = grows.GetFeatureCount()
    # if featuresWithinParcel != 0:
    #     grows.SetSpatialFilter(None)
    #     bufferWidth = 0
    #     exitVariable = 0
    #     while exitVariable == 0:
    #         bufferWidth = bufferWidth + 10
    #         buffer = geom_repr.Buffer(bufferWidth)
    #         grows.SetSpatialFilter(buffer)
    #         buffer_count = grows.GetFeatureCount()
    #         if buffer_count > featuresWithinParcel:
    #             exitVariable += 1
    #             distance = bufferWidth
    # else: distance = 'NA'
    # data_list['Dist_to_grow_m'].append(distance)
	#
    # ##############  (Private/Local) road length in each parcel  ##############
    # roads.SetAttributeFilter("FUNCTIONAL = 'Private' OR FUNCTIONAL = 'Local Roads'")
    # for road in roads:
    #     # road_clip = road.geometry().intersection(geom)
    #     if road.GetField('FUNCTIONAL') == 'Private':
    #         # print("Private")
    #         geom_PrivateRoad = road.geometry().Clone()
    #         PrivateRoad_intersection = geom_PrivateRoad.Intersection(geom)
    #         print("Private road length within parcel: ", PrivateRoad_intersection.Length()*3.2808399)
    #         data_list['km_privateRoad'].append(PrivateRoad_intersection.Length()*3.2808399) # convert from feet to meters!!
    #     elif road.GetField('FUNCTIONAL') == 'Local Roads':
    #         # print("Local")
    #         geom_LocalRoad = road.geometry().Clone()
    #         LocalRoad_intersection = geom_LocalRoad.Intersection(geom)
    #         print("Local road length within parcel: ", LocalRoad_intersection.Length()*3.2808399)
    #         data_list['km_localRoad'].append(LocalRoad_intersection.Length()*3.2808399) # convert from feet to meters!!
    # roads.SetAttributeFilter(None)
    # roads.ResetReading()
	#
    # ##############  Binary - Parcel on public land?  ##############
    # for publicLand in publicLands:
    #     geom_public = publicLand.geometry().Clone()
    # if geom_public.Intersects(geom):
    #     print("Public land")
    #     data_list['PublicLand-YN'].append(1)
    # else:
    #     print("Private land")
    #     data_list['PublicLand-YN'].append(0)
    # publicLands.ResetReading()
	#
    # ##############  Mean elevation of parcel  ##############



    ##############  Proportion of parcel in THP  ##############
    print("Parcel area: ", geom.Area())
    intersection_list = []
    for THP in thp:
        geom_THP = THP.geometry().Clone()
        print("Respective THP polygon area: ", geom_THP.Area())
        intersection_area = geom_THP.Intersection(geom).Area()
        intersection_list.append(intersection_area)
        print("Total intersection: ", sum(intersection_list))
    data_list['Prop_in_THP'].append(sum(intersection_list)/geom.Area())
    thp.ResetReading()
    # print("THP intersection area: ", geom_allTHP.Intersection(geom).Area())
    proportion_THP_intersection = geom_allTHP.Intersection(geom).Area() / geom.Area()
    data_list['Prop_in_THP'].append(proportion_THP_intersection)


exit(0)

##############  Write data frame and .csv  ##############
df = pd.DataFrame(data_list) # list means dictionary here :P
df.to_csv(wd + '../df_assignment08.csv', sep = ',')

