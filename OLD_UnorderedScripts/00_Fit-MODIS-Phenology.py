# ######################################## LOAD REQUIRED MODULES ############################################## #
import os
import sys
import time
import datetime
import ogr
import osr
from osgeo import gdal
from osgeo.gdalconst import *
import numpy as np
from osgeo import gdal_array as gdalnumeric
import csv
import itertools
import math
gdal.TermProgress = gdal.TermProgress_nocb
gdal.TermProgress = gdal.TermProgress_nocb
import scipy.ndimage
import struct
from scipy.optimize import leastsq
from pylab import *

# ####################################### SET TIME-COUNT ################################################################## #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")
# ####################################### BUILD GLOBAL FUNCTIONS ########################################################## #
def GetInfoFromCSV(csv_file, subsetRow, subsetColumn, variable):  # Row is 'year', Column is 'point' (starts column 4 (3 in py-notation))
	data = np.genfromtxt(csv_file, names = True, delimiter = ',', dtype = None)
	out_array = [[],[]]
	if variable == "ndvi":
		for row in data:
			if row['Year'] == subsetRow:
				out_array[1].append((row[subsetColumn] * 0.0001))
				out_array[0].append(row['DOY'])
	if variable == "temp":
		for row in data:
			if row['Year'] == subsetRow:
				out_array[1].append((row[subsetColumn] - 273.15)) 
				out_array[0].append(row['DOY'])
	return np.array(out_array)

def CalculateAGDD(temperature_table, t_base, t_max):
    out_array = []
    out_array.append(temperature_table[0])
    b = np.clip (temperature_table[1], t_base, t_max)
    c = np.where (b - t_base < 0, 0, b - t_base)
    agdd = c.cumsum ( axis=0 )
    out_array.append(list(agdd))
    return out_array

def InterpolateNDVI(ndvi_data, temp_data):
    out_array = []
    DOYs = np.arange(1, (len(temp_data[0])+1))
    ndvi_days = ndvi_data[0]
    ndvi_vals = ndvi_data[1]
    ndvid = np.interp(DOYs, ndvi_days, ndvi_vals)
    out_array.append(DOYs)
    out_array.append(ndvid)
    return out_array

def FitNDVI(ndvi_day):
	DOY = ndvi_day[0]
	ndvis = ndvi_daily[1]
	ndvi_max = np.max(ndvis)
	ndvi_min = ndvi_daily[1][0]
	fitfunc = lambda p, DOY: ndvi_min + (ndvi_max-ndvi_min) * (1./(1+np.exp(p[0]*(DOY-p[1])))+1./(1+np.exp(p[2]*(DOY-p[3]))) - 1)
	init = np.array([0.3, 165, 0.3, 240])
	errfunc = lambda p, doy, NDVI: fitfunc(p, doy) - NDVI
	p1,success = leastsq(errfunc, init[:], args=(DOY,ndvis),maxfev=100000000)
	return p1

def FitPhenologyModel(agdd_daily, ndvi_daily):
	np.seterr(over=None)
	DOY = ndvi_daily[0]
	ndvis = ndvi_daily[1]
	agdds = agdd_daily[1]
	ndvi_min = np.min(ndvis)
	ndvi_range = np.max(ndvis) - np.min(ndvis)
	init_parameters = np.array([ndvi_min, ndvi_range, 0.3, 165, 0.3, 240])
	PhenoFunction = init_parameters[0]+init_parameters[1]*(1./(1+np.exp(init_parameters[2]*(agdd_daily-init_parameters[3])))+1./(1+np.exp(-init_parameters[4]*(agdd_daily-init_parameters[5])))-1)
	output = []
	fitness = lambda p, ndvi, agdd: ndvi - PhenoFunction
	oot = fitness(init_parameters, ndvi_daily, agdd_daily)
	[output.append(x) for x in oot]
	output = np.array(output).squeeze()
	return output	
	
def WriteOutput(outlist, outfile):
	print("Write Output-File")
	with open(outfile, "w") as the_file:
		csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
		writer = csv.writer(the_file, dialect="custom")
		for element in outlist:
			writer.writerow(element)

# ####################################### ESTABLISH INPUT-PARAMETERS FOR WHOLE SCRIPT ##################################### #
# (1) Input-Tables from previous processes
NDVI_input = "E:/kirkdata/mbaumann/Species-separation_Chapter03/05_Warping/01_Point-Intersection_MODIS-NDVI_Output_doyAdded.csv"
TMP_input = "E:/kirkdata/mbaumann/Species-separation_Chapter03/05_Warping/02_DailyMeanTemp_Output_doyAdded.csv"
# (2) Year, which we will process
year_list = [2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
# (3) Names of Point-Location that we collected values for
point_list = ["Point_01","Point_02","Point_03","Point_04","Point_05","Point_06","Point_07","Point_08","Point_09","Point_10","Point_11","Point_12", \
"Point_13","Point_14","Point_15","Point_16","Point_17","Point_18","Point_19","Point_20","Point_21","Point_22","Point_23"]
# (4) Minimum temperature for Growing Degrees
t_base = 10
# (5) Maximum temperature for Growing Degrees
t_max = 40

# ######################################## ESTABLISH OUTPUT-LISTS THAT WE FILL WITH THE VALUES ############################ #
output_NDVI_Interpolation = [] # NDVI-INTERPOLATION
output_AGDD_Calculation = []
output_parameters = [] # FITTING PARAMETERS
output_parameters_Titles = ["Point_ID", "Year", "Param_p[0]","Param_p[1]","Param_p[2]","Param_p[3]"]
output_parameters.append(output_parameters_Titles)
output_NDVI_Fitting = []
output_phenology = []

# ######################################## FIT YEARLY NDVI-CURVES FOR 1 POINT IN 1 YEAR, EXTRACT PARAMETERS ############### #
for point in point_list:
	print("Processing Point: ", point)
	variable = point
	# Establish list for daily NDVI-interpolation
	ndvi_list = [variable]
	# Establish list for Accumulated Growind Degree Days (AGDD)
	agdd_list = [variable]
	# Establish list for fitted NDVI-values
	ndviFIT_list = [variable]
	# Establish list for daily Phenology-Model-output
	phenoVals_list = [variable]
	# Establish list for Year and Day of Year
	y_list = ["Year"]
	d_list = ["DOY"]
	for yr in year_list:
		year = yr
		print("Year: ", year)
		# Generate Data to use
		ndvi_yr_point = GetInfoFromCSV(NDVI_input, year, variable, "ndvi")
		temp_yr_point = GetInfoFromCSV(TMP_input, year, variable, "temp")
		# Generate information about YEAR and DOY, append to list
		doy_list = list(temp_yr_point[0])
		for day in doy_list:
			d_list.append(int(day))
		y_list_tmp = np.repeat(year, len(doy_list))		
		for y in y_list_tmp:
			y_list.append(int(y))
		# Calculate AGDD and write into list of AGDD-Calculation
		print("AGDD")
		agdd = CalculateAGDD(temp_yr_point, t_base, t_max)
		agdds = agdd[1]
		for gdd in agdds:
			agdd_list.append(gdd)
		# Do NDVI-Interpolation and write into list of NDVI-Interpolation
		print("NDVI-Interpolation")
		ndvi_daily = InterpolateNDVI(ndvi_yr_point, temp_yr_point)
		ndvis = ndvi_daily[1]
		for ndvi in ndvis:
			ndvi_list.append(ndvi)
		# Do the NDVI-Fit and extract the parameters
		print("Parameter Estimation")
		params = FitNDVI(ndvi_daily)
		param_list = []
		param_list.append(variable)
		param_list.append(year)
		for param in params:
			param_list.append(param)
		output_parameters.append(param_list)
		print("Model NDVI")
		ndvi_max = np.max(ndvis)
		ndvi_min = np.min(ndvis)
		for day in doy_list:
			ndvifit = ndvi_min + (ndvi_max-ndvi_min) * (1./(1+np.exp(params[0]*(day-params[1])))+1./(1+np.exp(params[2]*(day-params[3]))) - 1)
			ndviFIT_list.append(ndvifit)
		print("Model Phenology")
		vals = FitPhenologyModel(agdd, ndvi_daily)
		phenos = vals[1]
		for val in phenos:
			phenoVals_list.append(val)

	output_NDVI_Interpolation.append(y_list)
	output_NDVI_Interpolation.append(d_list)	
	output_NDVI_Interpolation.append(ndvi_list)		
	output_AGDD_Calculation.append(y_list)
	output_AGDD_Calculation.append(d_list)
	output_AGDD_Calculation.append(agdd_list)
	output_NDVI_Fitting.append(y_list)
	output_NDVI_Fitting.append(d_list)
	output_NDVI_Fitting.append(ndviFIT_list)
	output_phenology.append(y_list)
	output_phenology.append(d_list)
	output_phenology.append(phenoVals_list)	
	print("")
	
# Remove duplicates from the list (i.e., all the columns with Nx-Year etc.
output_NDVI_Interpolation.sort()
output_NDVI_Interpolation = list(output_NDVI_Interpolation for output_NDVI_Interpolation,_ in itertools.groupby(output_NDVI_Interpolation))
output_NDVI_Interpolation = map(list, zip(*output_NDVI_Interpolation))
output_AGDD_Calculation.sort()
output_AGDD_Calculation = list(output_AGDD_Calculation for output_AGDD_Calculation,_ in itertools.groupby(output_AGDD_Calculation))
output_AGDD_Calculation = map(list, zip(*output_AGDD_Calculation))
output_NDVI_Fitting.sort()
output_NDVI_Fitting = list(output_NDVI_Fitting for output_NDVI_Fitting,_ in itertools.groupby(output_NDVI_Fitting))
output_NDVI_Fitting = map(list, zip(*output_NDVI_Fitting))
output_phenology.sort()
output_phenology = list(output_phenology for output_phenology,_ in itertools.groupby(output_phenology))
output_phenology = map(list, zip(*output_phenology))
print("")
# ####################################### WRITE THE OUTPUT FILE ########################################################## #
print("Writing Output-Files")
outfile_params = "E:/kirkdata/mbaumann/Species-separation_Chapter03/05_Warping/03_FitPhenology_OptimizedParameters.csv"
outfile_NDVIdaily = "E:/kirkdata/mbaumann/Species-separation_Chapter03/05_Warping/03_FitPhenology_NDVI-daily.csv"
outfile_AGDD = "E:/kirkdata/mbaumann/Species-separation_Chapter03/05_Warping/03_FitPhenology_AGDD.csv"
outfile_NDVIfit = "E:/kirkdata/mbaumann/Species-separation_Chapter03/05_Warping/03_FitPhenology_NDVI-fitted.csv"
outfile_Phenology = "E:/kirkdata/mbaumann/Species-separation_Chapter03/05_Warping/03_FitPhenology_Phenology.csv"
WriteOutput(output_parameters, outfile_params)
WriteOutput(output_NDVI_Interpolation, outfile_NDVIdaily)
WriteOutput(output_AGDD_Calculation, outfile_AGDD)
WriteOutput(output_NDVI_Fitting, outfile_NDVIfit)
WriteOutput(output_phenology, outfile_Phenology)      
# ####################################### END TIME-COUNT AND PRINT TIME STATS ############################################ #        
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")