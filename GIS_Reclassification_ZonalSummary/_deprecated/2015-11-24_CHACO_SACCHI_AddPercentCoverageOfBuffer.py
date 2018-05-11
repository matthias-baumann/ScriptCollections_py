# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import ogr, osr
from ZumbaTools._Vector_Tools import *

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
shape_buff = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Sacchi-etal_Pueblos-Chaco-LUC/Chaco_urbantowns_LS_asSHP_SAD69_BuffersMerged.shp"
shape_outline = "Z:/CHACO/ShapeFiles/CHACO_outline_LAEA.shp"
# LOAD DRIVERS
drvV = ogr.GetDriverByName('ESRI Shapefile')
# ADD PROPORTION FIELD TO SHAPEFILE
#AddFieldToSHP(shape_buff,"Perc_Chaco", "float")
# OPEN SHAPEFILES
buff = drvV.Open(shape_buff, 1)
buff_lyr = buff.GetLayer()
outline = drvV.Open(shape_outline, 1)
outline_lyr = outline.GetLayer()
# BUILD COORDINATE TRANSFORMATION
buff_srs = buff_lyr.GetSpatialRef()
outline_srs = outline_lyr.GetSpatialRef()
transform = osr.CoordinateTransformation(buff_srs, outline_srs)

# GET OUTLINE-FEATURE
outline_feat = outline_lyr.GetNextFeature()
geom_outline = outline_feat.GetGeometryRef()

# LOOP THROUGH FEATURES IN BUFFER-SHAPEFILE
buff_feat = buff_lyr.GetNextFeature()
while buff_feat:
    # Calculate the area for the current buffer feature (in squaremeters probably)
    geom_buff = buff_feat.GetGeometryRef()
    buff_area = geom_buff.GetArea()
    # Build the intersection
    intersect = geom_buff.Intersection(geom_outline)
    # Calculate area of intersection and percentage by dividing through area of original polygon
    intersect_area = intersect.GetArea()
    prop = intersect_area / buff_area
    # Write value into shapefile
    buff_feat.SetField("Perc_Chaco", prop)
    buff_lyr.SetFeature(buff_feat)
    # Get next feature
    buff_feat = buff_lyr.GetNextFeature()
# Reset the reading of the layer
buff_lyr.ResetReading()
# CLOSE FILES AND LAYERS
buff_feat = None
outline_feat = None
buff_lyr = None
outline_lyr = None


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")