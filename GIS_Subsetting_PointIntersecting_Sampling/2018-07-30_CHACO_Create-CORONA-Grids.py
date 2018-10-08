# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr
import baumiTools as bt
import pandas as pd
import re
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
# drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('memory')
input = "L:/_SHARED_DATA/_students_data_exchange/LL_MB/Corona/Corona_Wolken.csv"
outfile = "L:/_SHARED_DATA/_students_data_exchange/LL_MB/Corona/Corona_Wolken_polygons.shp"
# ####################################### FUNCTIONS ########################################################### #
# source: https://stackoverflow.com/questions/21298772/how-to-convert-latitude-longitude-to-decimal-in-python
def ConvertCoord(inputString):
	# Convert all symbols into hyphon
	inputString = re.sub('[Â]', '-', inputString)
	inputString = re.sub('[°]', '', inputString)
	inputString = re.sub("[']", '-', inputString)
	inputString = re.sub('["]', '', inputString)
	multipler = 1 if inputString[-1] in ['N', 'E'] else -1
	outCoord = multipler * sum(float(x) / 60 ** n for n, x in enumerate(inputString[:-1].split('-')))
	return outCoord
# ####################################### PROGRAMMING ######################################################### #
# (1) CREATE NEW SHAPEFILE
# Create shapefile on disc
pr = ogr.osr.SpatialReference()
pr.ImportFromEPSG(4326)
outSHP = drvMemV.CreateDataSource('')
outLYR = outSHP.CreateLayer('outSHP', pr, geom_type=ogr.wkbPolygon)
# Add fields manually
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "EntityID", 'string')
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "AcqDate", 'string')
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "DirectFlag", 'string')
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "CamType", 'string')
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "CamRes", 'string')
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "FilmType", 'string')
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "Polar", 'string')
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "DispID", 'string')
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "OrderID", 'string')
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "DL_avail", 'string')
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "Browse", 'string')

# (2) CONVERT INFO FROM CSV-FILE TO SHAPE
# Open file with correct encoding
csv_open = pd.read_csv(input, sep=',', encoding="ISO-8859-1")
# Loop over rows
for index, row in csv_open.iterrows():
	print(row["Entity ID"])
    # Extract coordinates for the polygon
	NW_lat = ConvertCoord(row['NW Corner Lat'])
	NW_lon = ConvertCoord(row['NW Corner Long'])
	NE_lat = ConvertCoord(row['NE Corner Lat'])
	NE_lon = ConvertCoord(row['NE Corner Long'])
	SE_lat = ConvertCoord(row['SE Corner Lat'])
	SE_lon = ConvertCoord(row['SE Corner Long'])
	SW_lat = ConvertCoord(row['SW Corner Lat'])
	SW_lon = ConvertCoord(row['SW Corner Long'])
	# Create Polygon
	square = ogr.Geometry(ogr.wkbLinearRing)
	square.AddPoint(NW_lon, NW_lat)
	square.AddPoint(NE_lon, NE_lat)
	square.AddPoint(SE_lon, SE_lat)
	square.AddPoint(SW_lon, SW_lat)
	square.AddPoint(NW_lon, NW_lat)
	poly = ogr.Geometry(ogr.wkbPolygon)
	poly.AddGeometry(square)
	# Create the feature
	featDef = outLYR.GetLayerDefn()
	featOut = ogr.Feature(featDef)
	featOut.SetGeometry(poly)
	# Add the fields
	featOut.SetField('EntityID', row['Entity ID'])
	featOut.SetField('AcqDate', row['Acquisition Date'])
	featOut.SetField('DirectFlag', row['Direction Flag'])
	featOut.SetField('CamType', row['Camera Type'])
	featOut.SetField('CamRes', row['Camera Resolution'])
	featOut.SetField('FilmType', row['Film Type'])
	featOut.SetField('Polar', row['Polarity'])
	featOut.SetField('DispID', row['Display ID'])
	featOut.SetField('OrderID', row['Ordering ID'])
	featOut.SetField('DL_avail', row['Down Load Available'])
	featOut.SetField('Browse', row['Browse Link'])
	# Create the feature, get the next feature
	outLYR.CreateFeature(featOut)

# Copy the file to disk
bt.baumiVT.CopySHPDisk(outSHP, outfile)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")
