# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, gdal, osr
import baumiTools as bt
from tqdm import tqdm
import numpy as np
import random
import struct
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### SET FILE PATHS ###################################################### #
tc = gdal.Open("G:/Baumann/_ANALYSES/Summary_HansenForestCover_ForestLaw/Hansen_treeCover.vrt")
loss = gdal.Open("G:/Baumann/_ANALYSES/Summary_HansenForestCover_ForestLaw/Hansen_lossYear.vrt")
provinces = bt.baumiVT.CopyToMem("G:/Baumann/_ANALYSES/Summary_HansenForestCover_ForestLaw/SummaryLayer/ARG_ProvincesDepartamentos_sinTUCcapital.shp")
FL = gdal.Open("G:/Baumann/_ANALYSES/Summary_HansenForestCover_ForestLaw/SummaryLayer/FL_ENTIRE_CHACO_LAEA_resampledto1km.tif")
CHACO = bt.baumiVT.CopyToMem("G:/CHACO/_SHP_Files/CHACO_outline_LAEA.shp")
outputFile = "G:/Baumann/_ANALYSES/Summary_HansenForestCover_ForestLaw/ForestLawSummary_20181010.csv"
pxArea = 25*25 # from hansen
# ####################################### START PROCESSING #################################################### #
# INSTANTIATE OUTPUT TABLE
outTab = [["Province", "Departamento", "Depart_area_km2", "Depart_Perc_in_Chaco", "Zone", "Year", "Forest_km2", "Defor_km2"]]
# GET THE SHAPELAYERS AND LOOP THROUGH THE DEPARTAMENTOS
proLYR = provinces.GetLayer()
#flLYR = FL.GetLayer()
chacoLYR = CHACO.GetLayer()
chacoFEAT = chacoLYR.GetNextFeature()
chacoGEOM = chacoFEAT.GetGeometryRef()

proFEAT = proLYR.GetNextFeature()
while proFEAT:
	# Get the name of the Province plus the other info from the shapefile
	prov = proFEAT.GetField("Name_1")
	dep = proFEAT.GetField("Name_2")#"ALL"#
	prov_area = proFEAT.GetField("Shape_Area")
	prov_area = float(format(prov_area,'.3f'))
	print(prov, dep)
	# Now get the geometry
	geom = proFEAT.GetGeometryRef()
	geom_cl = geom.Clone()
	# Intersect with Chaco-layer so that we know how much of it is in the Chaco
	int = geom.Intersection(chacoGEOM)
	int_area_km2 = int.GetArea() / 1000000
	percInChaco = float(format(int_area_km2 / prov_area,'.3f'))
	# Now Get the forest area in the intersected area, add the first output to the outputTable
	geom_np, forest_np = bt.baumiRT.Geom_Raster_to_np(int, tc)
	forest_np_masked = np.where((geom_np == 1), forest_np, 0)
	sumPX = np.count_nonzero(forest_np_masked > 25)
	forest2000 = sumPX * pxArea / 1000000
	outTab.append([prov, dep, prov_area, percInChaco, "Entire Departamento", 2000, float(format(forest2000,'.3f')), 0])
	# Now go over deforestation in the entire province
	geom_np, loss_np = bt.baumiRT.Geom_Raster_to_np(int, loss)

	loss_np_masked = np.where((geom_np == 1), loss_np, 0)
	defPX = list(np.histogram(loss_np_masked, bins=18)[0])

	for val in range(1, 18, 1):
		px = defPX[val]
		area_all = px * pxArea / 1000000
		forest2000 = forest2000 - area_all
		year = 2000 + val
		outTab.append([prov, dep, prov_area, percInChaco, "Entire Departamento", year, float(format(forest2000,'.3f')), float(format(area_all,'.3f'))])

	# Now do the stuff for the three forest law zones
	# Get the forest law zones as a numpy array
	geom_np, law_np = bt.baumiRT.Geom_Raster_to_np(int, FL)
	law_np_masked = np.where((geom_np == 1), law_np, 0)
	# GREEN ZONE
	# (0) Check if the class exists in the province
	if True == np.any(law_np_masked[:, :] == 3):
		# (1) Forest area
		forest_green = np.where(law_np_masked == 3, forest_np, 0)
		forest_np_masked = np.where((geom_np == 1), forest_green, 0)
		sumPX_green = np.count_nonzero(forest_np_masked > 25)
		forest2000_green = sumPX_green * pxArea / 1000000
		outTab.append([prov, dep, prov_area, percInChaco, "Green Zone", 2000, float(format(forest2000_green,'.3f')), 0])
		# (2) Forest loss
		loss_green = np.where(law_np_masked == 3, loss_np, 0)
		loss_green_masked = np.where((geom_np == 1), loss_green, 0)

		defPX_green = list(np.histogram(loss_green_masked, bins=18)[0])
		countZero_green = defPX_green.count(0)
		# Small work around to ensure that lists with exclusively zeros are being ommitted
		if not countZero_green > 15:
			for val in range(1, 18, 1):
				px = defPX_green[val]
				area_green = px * pxArea / 1000000
				forest2000_green = forest2000_green - area_green
				year = 2000 + val
				outTab.append([prov, dep, prov_area, percInChaco, "Green zone", year, float(format(forest2000_green,'.3f')), float(format(area_green,'.3f'))])
		else:
			outTab.append([prov, dep, prov_area, percInChaco, "Green zone", 2000, 0, 0])
			for val in range(1, 18, 1):
				year = 2000 + val
				outTab.append([prov, dep, prov_area, percInChaco, "Green zone", year, 0, 0])
	else:
		outTab.append([prov, dep, prov_area, percInChaco, "Green zone", 2000, 0, 0])
		for val in range(1, 18, 1):
			year = 2000 + val
			outTab.append([prov, dep, prov_area, percInChaco, "Green zone", year, 0, 0])
	#
	# YELLOW ZONE
	# (0) Check if the class exists in the province
	if True == np.any(law_np_masked[:, :] == 2):
		# (1) Forest area
		forest_yellow = np.where(law_np_masked == 2, forest_np, 0)
		forest_np_masked = np.where((geom_np == 1), forest_yellow, 0)
		sumPX_yellow = np.count_nonzero(forest_np_masked > 25)
		forest2000_yellow = sumPX_yellow * pxArea / 1000000
		outTab.append([prov, dep, prov_area, percInChaco, "Yellow Zone", 2000, float(format(forest2000_yellow,'.3f')), 0])
		# (2) Forest loss
		loss_yellow = np.where(law_np_masked == 2, loss_np, 0)
		loss_yellow_masked = np.where((geom_np == 1), loss_yellow, 0)

		defPX_yellow = list(np.histogram(loss_yellow_masked, bins=18)[0])
		countZero_yellow = defPX_yellow.count(0)
		# Small work around to ensure that lists with exclusively zeros are being ommitted
		if not countZero_yellow > 15:
			for val in range(1, 18, 1):
				px = defPX_yellow[val]
				area_yellow = px * pxArea / 1000000
				forest2000_yellow = forest2000_yellow - area_yellow
				year = 2000 + val
				outTab.append([prov, dep, prov_area, percInChaco, "Yellow zone", year, float(format(forest2000_yellow,'.3f')), float(format(area_yellow,'.3f'))])
		else:
			outTab.append([prov, dep, prov_area, percInChaco, "Yellow Zone", 2000, 0, 0])
			for val in range(1, 18, 1):
				year = 2000 + val
				outTab.append([prov, dep, prov_area, percInChaco, "Yellow zone", year, 0, 0])
	else:
		outTab.append([prov, dep, prov_area, percInChaco, "Yellow Zone", 2000, 0, 0])
		for val in range(1, 18, 1):
			year = 2000 + val
			outTab.append([prov, dep, prov_area, percInChaco, "Yellow zone", year, 0, 0])
	#
	# RED ZONE
	# (0) Check if the class exists in the province
	if True == np.any(law_np_masked[:, :] == 1):
		# (1) Forest area
		forest_red = np.where((law_np_masked == 1), forest_np, 0)
		forest_np_masked = np.where((geom_np == 1), forest_red, 0)
		sumPX_red = np.count_nonzero(forest_np_masked > 25)
		forest2000_red = sumPX_red * pxArea / 1000000
		outTab.append([prov, dep, prov_area, percInChaco, "Red Zone", 2000, float(format(forest2000_red,'.3f')), 0])
		# (2) Forest loss
		loss_red = np.where(law_np_masked == 1, loss_np, 0)
		loss_red_masked = np.where((geom_np == 1), loss_red, 0)

		defPX_red = list(np.histogram(loss_red_masked, bins=18)[0])
		countZero_red = defPX_red.count(0)
		# Small work around to ensure that lists with exclusively zeros are being ommitted
		if not countZero_red > 15:
			for val in range(1, 18, 1):
				px = defPX_red[val]
				area_red = px * pxArea / 1000000
				forest2000_red = forest2000_red - area_red
				year = 2000 + val
				#print(year, area_red)
				outTab.append([prov, dep, prov_area, percInChaco, "Red zone", year, float(format(forest2000_red,'.3f')), float(format(area_red,'.3f'))])
		else:
			outTab.append([prov, dep, prov_area, percInChaco, "Red Zone", 2000, 0, 0])
			for val in range(1, 18, 1):
				year = 2000 + val
				outTab.append([prov, dep, prov_area, percInChaco, "Red zone", year, 0, 0])

	else:
		outTab.append([prov, dep, prov_area, percInChaco, "Red Zone", 2000, 0, 0])
		for val in range(1, 18, 1):
			year = 2000 + val
			outTab.append([prov, dep, prov_area, percInChaco, "Red zone", year, 0, 0])
# GET THE NEXT FEATURE
	proFEAT = proLYR.GetNextFeature()

# WRITE THE OUTPUT-FILE
bt.baumiFM.WriteListToCSV(outputFile, outTab, delim=",")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")