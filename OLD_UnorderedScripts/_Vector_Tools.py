__author__ = 'Matthias Baumann'
import os
import ogr, osr, gdal
from gdalconst import *
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
drvV = ogr.GetDriverByName('ESRI Shapefile')

def AddFieldToSHP(shape, name, type):
    # Shape = input-shapefile, name = name of the field, type = type of the field
    # types --> Integer=OFTInteger, Float=OFTReal, String=OFTString
    shape_open = ogr.Open(shape, 1)
    lyr = shape_open.GetLayer()
    # Check if field already exists, if exists throw out warning
    ldef = lyr.GetLayerDefn()
    if ldef.GetFieldIndex(name) != -1:
        print("--> Warning: Fieldname " + name + " already exists. Skipping...")
    else:
        if type == "float":
            fieldDef = ogr.FieldDefn(name, ogr.OFTReal)
        if type == "int":
            fieldDef = ogr.FieldDefn(name, ogr.OFTInteger)
        if type == "string":
            fieldDef = ogr.FieldDefn(name, ogr.OFTString)
        lyr.CreateField(fieldDef)
    lyr = None
    shape_open = None

def ReprojectShape(inShape, outProj, outname):

# Open the layer of the input shapefile
    shp = drvMemV.CopyDataSource(ogr.Open(inShape),'')
    lyr = shp.GetLayer()
# Build the coordinate Transformation
    inPR = lyr.GetSpatialRef()
    outPR = osr.SpatialReference()
    outPR.ImportFromWkt(outProj)
    transform = osr.CoordinateTransformation(inPR, outPR)
# Create the output-SHP and LYR, get geometry type first
    feat = lyr.GetNextFeature()
    geom = feat.GetGeometryRef()
    geomType = geom.GetGeometryType()
    lyr.ResetReading()
    outSHP = drvV.CreateDataSource(outname)
    outLYR = outSHP.CreateLayer('outSHP', outPR, geom_type=geomType)
# Create all fields in the new shp-file that we created before
    inLayerDefn = lyr.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLYR.CreateField(fieldDefn)
# get the output layer's feature definition
    outLYRDefn = outLYR.GetLayerDefn()
# Now loop through the features from the inSHP, transform geometries, add to new SHP and also take the values in the attributes
    feat = lyr.GetNextFeature()
    while feat:
        geom = feat.GetGeometryRef()
        geom.Transform(transform)
        outFeat = ogr.Feature(outLYRDefn)
        outFeat.SetGeometry(geom)
        for i in range(0, outLYRDefn.GetFieldCount()):
            outFeat.SetField(outLYRDefn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))
        outLYR.CreateFeature(outFeat)
# Destroy/Close the features and get next input-feature
        outFeat.Destroy()
        feat.Destroy()
        feat = lyr.GetNextFeature()
# Close the shapefiles, return the output shapefile
    shp.Destroy()
    outSHP.Destroy()
    return outSHP



# shp_mem = drvV.CreateDataSource("D:/shpout.shp")
# lyr = shp_mem.CreateLayer('', steelheadLYR.GetSpatialRef(), ogr.wkbLineString)
# lyr = shp_mem.CreateLayer('', parcelLYR.GetSpatialRef(), ogr.wkbMultiPolygon)
# lyrDef = lyr.GetLayerDefn()
# feat = ogr.Feature(lyrDef)
# feat.SetGeometry(intersection)
# lyr.CreateFeature(feat)
# lyr.SetFeature(feat)





