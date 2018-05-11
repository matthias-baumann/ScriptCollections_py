# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import numpy as np
import time
import baumiTools as bt
import gdal
import csv
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
rootPath = "Z:/_SHARED_DATA/PLTEMP/"
admin = bt.baumiVT.CopyToMem(rootPath + "CHACO_AdminBoundaries_ALL.shp")
defor = bt.baumiVT.CopyToMem(rootPath + "gran_chaco_deforestation_semi_cleaned.shp")
lc = gdal.Open(rootPath + "lc_2015_final.tif")
output = rootPath + "_SummaryByRegion.csv"
years = range(2011, 2016)
def GeomRasterNumpy(geom, raster):
    import ogr, osr
    import numpy as np
    # Make a coordinate transformation of the geom-srs to the raster-srs
    pol_srs = geom.GetSpatialReference()
    ras_srs = raster.GetProjection()
    target_SR = osr.SpatialReference()
    target_SR.ImportFromWkt(ras_srs)
    srs_trans = osr.CoordinateTransformation(pol_srs, target_SR)
    geom.Transform(srs_trans)
    # Calculate the km2 area here --> divide by 1e6
    geom_area = geom.GetArea() / 1000000
    # Create a memory shp/lyr to rasterize in
    geom_shp = ogr.GetDriverByName('Memory').CreateDataSource('')
    geom_lyr = geom_shp.CreateLayer('geom_shp', srs=geom.GetSpatialReference())
    geom_feat = ogr.Feature(geom_lyr.GetLayerDefn())
    geom_feat.SetGeometryDirectly(ogr.Geometry(wkt=str(geom)))
    geom_lyr.CreateFeature(geom_feat)
    # Rasterize the layer, open in numpy
    #bt.baumiVT.CopySHPDisk(geom_shp, rootPath + "_tryout.shp")
    x_min, x_max, y_min, y_max = geom.GetEnvelope()
    gt = raster.GetGeoTransform()
    pr = raster.GetProjection()
    x_res = int((x_max - x_min) / 30)
    y_res = int((y_max - y_min) / 30)
    if x_res > 0 and y_res > 0:
        new_gt = (x_min, gt[1], 0, y_max, 0, -gt[1])
        lyr_ras = gdal.GetDriverByName('MEM').Create('', x_res, y_res, 1, gdal.GDT_Byte)
        lyr_ras.GetRasterBand(1).SetNoDataValue(0)
        lyr_ras.SetProjection(pr)
        lyr_ras.SetGeoTransform(new_gt)
        gdal.RasterizeLayer(lyr_ras, [1], geom_lyr, burn_values=[1])
        geom_np = np.array(lyr_ras.GetRasterBand(1).ReadAsArray())
        # Now load the raster into the array --> only take the area that is 1:1 the geom-layer (see Garrard p.195)
        inv_gt = gdal.InvGeoTransform(gt)
        offsets_ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)
        off_ul_x, off_ul_y = map(int, offsets_ul)
        raster_np = np.array(raster.GetRasterBand(1).ReadAsArray(off_ul_x, off_ul_y, x_res, y_res))
        ## Just for checking if the output is correct --> write it to disc. Outcommented here
        #val_ras = gdal.GetDriverByName('MEM').Create('', x_res, y_res, 1, gdal.GDT_Byte)
        #val_ras.SetProjection(pr)
        #val_ras.SetGeoTransform(new_gt)
        #val_ras.GetRasterBand(1).WriteArray(raster_np, 0, 0)
        #bt.baumiRT.CopyMEMtoDisk(lyr_ras, rootPath + "_tryout2.tif")
        #bt.baumiRT.CopyMEMtoDisk(val_ras, rootPath + "_tryout3.tif")
    else:
        geom_np = raster_np = geom_area = 0

    return geom_np, raster_np, geom_area
# ####################################### PROCESSING ########################################################## #
# Initialize output table
outData = [["Coutry_ID", "Country_Name", "Province_Name", "Province_ID", "Departamento_Name", "Departamento_ID",
            "Year", "FL_All_km2", "FL_crop_km2", "FL_pasture_km2", "F_control_km2"]]
# Loop through the admin-boundaries
admin_lyr = admin.GetLayer()
defor_lyr = defor.GetLayer()
pol_trans = bt.baumiVT.CS_Transform(admin_lyr, defor_lyr)
admin_feat = admin_lyr.GetNextFeature()
while admin_feat:
# Get the general info of the polygon
    countryID = admin_feat.GetField('ID_0')
    countryName = admin_feat.GetField('Name_0')
    provName = admin_feat.GetField('Name_1')
    provID = admin_feat.GetField('ID_1')
    departName = admin_feat.GetField('Name_2')
    departID = admin_feat.GetField('ID_2')
    print(countryName, provName, departName)
# Get the geometry
    admin_geom = admin_feat.GetGeometryRef()
# Select, if there are deforestation plots from Guyra Paraguay in the departamento
    admin_geom_clone = admin_geom.Clone()
    admin_geom_clone.Transform(pol_trans)
    defor_lyr.SetSpatialFilter(admin_geom_clone)
    defor_count = defor_lyr.GetFeatureCount()
    # if there aren't, add to the output the rows with information of zero deforestation
    if defor_count == 0:
        for y in years:
            vals = [countryID, countryName, provName, provID, departName, departID, y, 0, 0, 0, 0]
            outData.append(vals)
    else:
    # if there are, then intersect the geometries from the defor-layer at the departamento-level in case we have plots that reach over two
        # Loop by year
        for yr in years:
            # Initiate values
            vals = [countryID, countryName, provName, provID, departName, departID, yr]
            fl = 0
            flc = 0
            flp = 0
            f = 0
            defor_feat = defor_lyr.GetNextFeature()
            while defor_feat:
                # Get the information from the year
                yr_check = defor_feat.GetField('year')
                #print(defor_feat.GetField('ID'))
                # If the polygon is not from the year, get the next defor-poly
                if yr_check != yr:
                    defor_feat = defor_lyr.GetNextFeature()
                else:
                # if it is from the year, intersect it with the departamento --> for accuracy reasons
                    defor_geom = defor_feat.GetGeometryRef()
                    inters = defor_geom.Intersection(admin_geom_clone)
                # Get the rasters as values
                    geom_vals, lc_vals, area = GeomRasterNumpy(inters, lc)
                    if area > 0:
                # Mask in lc_vals everything that is not 1 in geom_vals
                        lc_mask = np.where((geom_vals == 0), 0, lc_vals)
                        # Now check which LC- class we have
                        pasture = np.sum(np.where((lc_mask == 5), 1, 0))
                        cropland = np.sum(np.where((lc_mask == 4), 1, 0))
                        forest = np.sum(np.where((lc_mask == 1), 1, 0))
                        #print(pasture, cropland, forest)
                        if pasture > cropland and pasture > forest:
                            fl = fl + area
                            flp = flp + area
                        if cropland > pasture and cropland > forest:
                            fl = fl + area
                            flc = flc + area
                        if forest > cropland and forest > pasture:
                            fl = fl + area
                            f = f + area
                    else:
                        fl=fl
                        flp=flp
                        flc=flc
                        f=f
                    # Take the next deforestation feature
                    defor_feat = defor_lyr.GetNextFeature()
            # Append the summed up values to the vals-list and bring to the output, resetreading on deforestation plots
            defor_lyr.ResetReading()
            vals.extend([fl, flc, flp, f])
            # Append vals to output
            outData.append(vals)
    # take next admin-feature feature
    admin_feat = admin_lyr.GetNextFeature()
# Write output
print("Write output")
with open(output, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in outData:
        writer.writerow(element)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")