
 #IMPORT SYSTEM MODULES
from __future__ import division
from math import sqrt
import sys, string, os#, arcgisscripting
import time

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# DEFINE INPUT FOLDER MANUALLY
input_folder = "X:/mbaumann/Cloudmask_MCK/00_Processing/p99_r78_processed/Results/"
output = "X:/mbaumann/Cloudmask_MCK/00_Processing/p99_r78_processed/numbers.csv"
# CREATE LISTS FOR CLOUDMASKS
acca1 = []
acca2 = []
cmask = []
fmask_original = []
fmask_sav = []
ltk = []
vct = []

# FILL LIST WITH FILES TO BE PROCESSED
fileList = os.listdir(input_folder)
for file in fileList[:]:
	if file.find(".sts") < 0:
		fileList.remove(file)

# SORT LISTS BY MEASUREMENT
AC = [] # aggregated cells
FIS = [] # Fuzzy Inference system
FK = [] # Fuzzy kappa
K = [] # Kappa
PC1 = [] # per Category 1 (No Cloud)
PC2 = [] # per category 2 (Cloud)

		
# LOOP THROUGH FILES AND SORT INTO LISTS	
for file in fileList[:]:
	if file.find("aggregated cells") >= 0:
		AC.append(file)
	if file.find("fuzzy inference system") >= 0:
		FIS.append(file)
	if file.find("fuzzy kappa") >= 0:
		FK.append(file)
	if file.find("kappa") >= 0:
		K.append(file)
	if file.find("item1") >= 0:
		PC1.append(file)
	if file.find("item2") >= 0:
		PC2.append(file)
# remove the fuzzy things in the kappa list
for kappa in K[:]:
	if kappa.find("fuzzy") >= 0:
		K.remove(kappa)
# ########################################################################################	
# PROCESS AGGREGATED CELLS
for file in AC[:]:
	if file.find("acca1") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("mean=") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				acca1.append(val)
		offen.close()
		
	if file.find("acca2") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("mean=") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				acca2.append(val)
		offen.close()
		
	if file.find("cmask") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("mean=") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				cmask.append(val)
		offen.close()
		
	if file.find("fmask_original") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("mean=") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				fmask_original.append(val)
		offen.close()
		
	if file.find("fmask_sav") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("mean=") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				fmask_sav.append(val)
		offen.close()
	
	if file.find("ltk") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("mean=") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				ltk.append(val)
		offen.close()

	if file.find("vct") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("mean=") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				vct.append(val)
		offen.close()

# PROCESS FUZZY INFERENCE SYSTEM
for file in FIS[:]:
	if file.find("acca1") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("results_fis") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				acca1.append(val)
		offen.close()

	if file.find("acca2") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("results_fis") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				acca2.append(val)
		offen.close()
		
	if file.find("cmask") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("results_fis") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				cmask.append(val)
		offen.close()
		
	if file.find("fmask_original") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("results_fis") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				fmask_original.append(val)
		offen.close()
		
	if file.find("fmask_sav") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("results_fis") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				fmask_sav.append(val)
		offen.close()
	
	if file.find("ltk") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("results_fis") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				ltk.append(val)
		offen.close()

	if file.find("vct") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for line in offen:
			if line.find("results_fis") >= 0:
				p1 = line.find("=")
				p2 = line.rfind(">")
				val = line[p1+2:p2-2]
				vct.append(val)
		offen.close()

# PROCESS FUZZY KAPPA		
for file in FK[:]:
	if file.find("acca1") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 3:
				p1 = line.find("=")
				val1 = line[p1+2:p1+21]
				p2 = line.rfind("=")
				val2 = line[p2+2:p2+20]	
			if i == 7:		# look first for the cloud value, since we concatenate everything vice versa
				p3l = line.find("=")
				p3r = line.rfind(">")
				val3 = line[p3l+2:p3r-2]
			if i == 6:
				p4l = line.find("=")
				p4r = line.rfind(">")
				val4 = line[p4l+2:p4r-2]	
		acca1.append(val3)
		acca1.append(val4)
		acca1.append(val2)
		acca1.append(val1)
		offen.close()

	if file.find("acca2") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 3:
				p1 = line.find("=")
				val1 = line[p1+2:p1+21]
				p2 = line.rfind("=")
				val2 = line[p2+2:p2+20]
			if i == 7:		# look first for the cloud value, since we concatenate everything vice versa
				p3l = line.find("=")
				p3r = line.rfind(">")
				val3 = line[p3l+2:p3r-2]
			if i == 6:
				p4l = line.find("=")
				p4r = line.rfind(">")
				val4 = line[p4l+2:p4r-2]
		acca2.append(val3)
		acca2.append(val4)
		acca2.append(val2)
		acca2.append(val1)
		offen.close()

	if file.find("cmask") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 3:
				p1 = line.find("=")
				val1 = line[p1+2:p1+21]
				p2 = line.rfind("=")
				val2 = line[p2+2:p2+20]
			if i == 7:		# look first for the cloud value, since we concatenate everything vice versa
				p3l = line.find("=")
				p3r = line.rfind(">")
				val3 = line[p3l+2:p3r-2]
			if i == 6:
				p4l = line.find("=")
				p4r = line.rfind(">")
				val4 = line[p4l+2:p4r-2]
		cmask.append(val3)
		cmask.append(val4)
		cmask.append(val2)
		cmask.append(val1)
		offen.close()

	if file.find("fmask_original") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 3:
				p1 = line.find("=")
				val1 = line[p1+2:p1+21]
				p2 = line.rfind("=")
				val2 = line[p2+2:p2+20]
			if i == 7:		# look first for the cloud value, since we concatenate everything vice versa
				p3l = line.find("=")
				p3r = line.rfind(">")
				val3 = line[p3l+2:p3r-2]
			if i == 6:
				p4l = line.find("=")
				p4r = line.rfind(">")
				val4 = line[p4l+2:p4r-2]
		fmask_original.append(val3)
		fmask_original.append(val4)
		fmask_original.append(val2)
		fmask_original.append(val1)
		offen.close()		
		
	if file.find("fmask_sav") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 3:
				p1 = line.find("=")
				val1 = line[p1+2:p1+21]
				p2 = line.rfind("=")
				val2 = line[p2+2:p2+20]
			if i == 7:		# look first for the cloud value, since we concatenate everything vice versa
				p3l = line.find("=")
				p3r = line.rfind(">")
				val3 = line[p3l+2:p3r-2]
			if i == 6:
				p4l = line.find("=")
				p4r = line.rfind(">")
				val4 = line[p4l+2:p4r-2]
		fmask_sav.append(val3)
		fmask_sav.append(val4)
		fmask_sav.append(val2)
		fmask_sav.append(val1)
		offen.close()
		
	if file.find("ltk") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 3:
				p1 = line.find("=")
				val1 = line[p1+2:p1+21]
				p2 = line.rfind("=")
				val2 = line[p2+2:p2+20]
			if i == 7:		# look first for the cloud value, since we concatenate everything vice versa
				p3l = line.find("=")
				p3r = line.rfind(">")
				val3 = line[p3l+2:p3r-2]
			if i == 6:
				p4l = line.find("=")
				p4r = line.rfind(">")
				val4 = line[p4l+2:p4r-2]
		ltk.append(val3)
		ltk.append(val4)
		ltk.append(val2)
		ltk.append(val1)
		offen.close()			
		
	if file.find("vct") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 3:
				p1 = line.find("=")
				val1 = line[p1+2:p1+21]
				p2 = line.rfind("=")
				val2 = line[p2+2:p2+20]
			if i == 7:		# look first for the cloud value, since we concatenate everything vice versa
				p3l = line.find("=")
				p3r = line.rfind(">")
				val3 = line[p3l+2:p3r-2]
			if i == 6:
				p4l = line.find("=")
				p4r = line.rfind(">")
				val4 = line[p4l+2:p4r-2]
		vct.append(val3)
		vct.append(val4)
		vct.append(val2)
		vct.append(val1)
		offen.close()		
		
# PROCESS KAPPA
for file in K[:]:
	if file.find("acca1") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 17:
				p1 = line.find("=")
				val1 = line[p1+2:p1+19]
			if i == 16:
				p1 = line.find("=")
				val2 = line[p1+2:p1+19]
			if i == 12:
				p1 = line.find("=")
				val3 = line[p1+2:p1+19]
			if i == 11:
				p1 = line.find("=")
				val4 = line[p1+2:p1+19]
			if i == 7:
				p1 = line.find("=")
				val5 = line[p1+2:p1+19]
			if i == 6:
				p1 = line.find("=")
				val6 = line[p1+2:p1+19]
			if i == 3:		
				p1 = line.rfind("klocation=")
				val7 = line[p1+11:p1+26]	
				p2 = line.find("khisto=")
				val8 = line[p2+8:p2+25]		
				p3 = line.find("kappa=")
				val9 = line[p3+7:p3+24]
				p4 = line.find("frac_correct=")
				val10 = line[p4+14:p4+31]
		acca1.append(val1)
		acca1.append(val2)
		acca1.append(val3)
		acca1.append(val4)
		acca1.append(val5)
		acca1.append(val6)
		acca1.append(val7)
		acca1.append(val8)		
		acca1.append(val9)		
		acca1.append(val10)	

		offen.close()

	if file.find("acca2") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 17:
				p1 = line.find("=")
				val1 = line[p1+2:p1+19]
			if i == 16:
				p1 = line.find("=")
				val2 = line[p1+2:p1+19]
			if i == 12:
				p1 = line.find("=")
				val3 = line[p1+2:p1+19]
			if i == 11:
				p1 = line.find("=")
				val4 = line[p1+2:p1+19]
			if i == 7:
				p1 = line.find("=")
				val5 = line[p1+2:p1+19]
			if i == 6:
				p1 = line.find("=")
				val6 = line[p1+2:p1+19]
			if i == 3:		
				p1 = line.rfind("klocation=")
				val7 = line[p1+11:p1+26]	
				p2 = line.find("khisto=")
				val8 = line[p2+8:p2+25]		
				p3 = line.find("kappa=")
				val9 = line[p3+7:p3+24]
				p4 = line.find("frac_correct=")
				val10 = line[p4+14:p4+31]
		acca2.append(val1)
		acca2.append(val2)
		acca2.append(val3)
		acca2.append(val4)
		acca2.append(val5)
		acca2.append(val6)
		acca2.append(val7)
		acca2.append(val8)		
		acca2.append(val9)		
		acca2.append(val10)	
		offen.close()

	if file.find("cmask") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 17:
				p1 = line.find("=")
				val1 = line[p1+2:p1+19]
			if i == 16:
				p1 = line.find("=")
				val2 = line[p1+2:p1+19]
			if i == 12:
				p1 = line.find("=")
				val3 = line[p1+2:p1+19]
			if i == 11:
				p1 = line.find("=")
				val4 = line[p1+2:p1+19]
			if i == 7:
				p1 = line.find("=")
				val5 = line[p1+2:p1+19]
			if i == 6:
				p1 = line.find("=")
				val6 = line[p1+2:p1+19]
			if i == 3:		
				p1 = line.rfind("klocation=")
				val7 = line[p1+11:p1+26]	
				p2 = line.find("khisto=")
				val8 = line[p2+8:p2+25]		
				p3 = line.find("kappa=")
				val9 = line[p3+7:p3+24]
				p4 = line.find("frac_correct=")
				val10 = line[p4+14:p4+31]
		cmask.append(val1)
		cmask.append(val2)
		cmask.append(val3)
		cmask.append(val4)
		cmask.append(val5)
		cmask.append(val6)
		cmask.append(val7)
		cmask.append(val8)		
		cmask.append(val9)		
		cmask.append(val10)	
		offen.close()

	if file.find("fmask_original") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 17:
				p1 = line.find("=")
				val1 = line[p1+2:p1+19]
			if i == 16:
				p1 = line.find("=")
				val2 = line[p1+2:p1+19]
			if i == 12:
				p1 = line.find("=")
				val3 = line[p1+2:p1+19]
			if i == 11:
				p1 = line.find("=")
				val4 = line[p1+2:p1+19]
			if i == 7:
				p1 = line.find("=")
				val5 = line[p1+2:p1+19]
			if i == 6:
				p1 = line.find("=")
				val6 = line[p1+2:p1+19]
			if i == 3:		
				p1 = line.rfind("klocation=")
				val7 = line[p1+11:p1+26]	
				p2 = line.find("khisto=")
				val8 = line[p2+8:p2+25]		
				p3 = line.find("kappa=")
				val9 = line[p3+7:p3+24]
				p4 = line.find("frac_correct=")
				val10 = line[p4+14:p4+31]
		fmask_original.append(val1)
		fmask_original.append(val2)
		fmask_original.append(val3)
		fmask_original.append(val4)
		fmask_original.append(val5)
		fmask_original.append(val6)
		fmask_original.append(val7)
		fmask_original.append(val8)		
		fmask_original.append(val9)		
		fmask_original.append(val10)
		offen.close()		

	if file.find("fmask_sav") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 17:
				p1 = line.find("=")
				val1 = line[p1+2:p1+19]
			if i == 16:
				p1 = line.find("=")
				val2 = line[p1+2:p1+19]
			if i == 12:
				p1 = line.find("=")
				val3 = line[p1+2:p1+19]
			if i == 11:
				p1 = line.find("=")
				val4 = line[p1+2:p1+19]
			if i == 7:
				p1 = line.find("=")
				val5 = line[p1+2:p1+19]
			if i == 6:
				p1 = line.find("=")
				val6 = line[p1+2:p1+19]
			if i == 3:		
				p1 = line.rfind("klocation=")
				val7 = line[p1+11:p1+26]	
				p2 = line.find("khisto=")
				val8 = line[p2+8:p2+25]		
				p3 = line.find("kappa=")
				val9 = line[p3+7:p3+24]
				p4 = line.find("frac_correct=")
				val10 = line[p4+14:p4+31]
		fmask_sav.append(val1)
		fmask_sav.append(val2)
		fmask_sav.append(val3)
		fmask_sav.append(val4)
		fmask_sav.append(val5)
		fmask_sav.append(val6)
		fmask_sav.append(val7)
		fmask_sav.append(val8)		
		fmask_sav.append(val9)		
		fmask_sav.append(val10)	
		offen.close()

	if file.find("ltk") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 17:
				p1 = line.find("=")
				val1 = line[p1+2:p1+19]
			if i == 16:
				p1 = line.find("=")
				val2 = line[p1+2:p1+19]
			if i == 12:
				p1 = line.find("=")
				val3 = line[p1+2:p1+19]
			if i == 11:
				p1 = line.find("=")
				val4 = line[p1+2:p1+19]
			if i == 7:
				p1 = line.find("=")
				val5 = line[p1+2:p1+19]
			if i == 6:
				p1 = line.find("=")
				val6 = line[p1+2:p1+19]
			if i == 3:		
				p1 = line.rfind("klocation=")
				val7 = line[p1+11:p1+26]	
				p2 = line.find("khisto=")
				val8 = line[p2+8:p2+25]		
				p3 = line.find("kappa=")
				val9 = line[p3+7:p3+24]
				p4 = line.find("frac_correct=")
				val10 = line[p4+14:p4+31]
		ltk.append(val1)
		ltk.append(val2)
		ltk.append(val3)
		ltk.append(val4)
		ltk.append(val5)
		ltk.append(val6)
		ltk.append(val7)
		ltk.append(val8)		
		ltk.append(val9)		
		ltk.append(val10)	
		offen.close()
		
	if file.find("vct") >= 0:
		input = input_folder + file
		offen = open(input, "r")
		for i,  line in enumerate(offen):		# to go to specific lines, not that i = n-1 for nth line
			if i == 17:
				p1 = line.find("=")
				val1 = line[p1+2:p1+19]
			if i == 16:
				p1 = line.find("=")
				val2 = line[p1+2:p1+19]
			if i == 12:
				p1 = line.find("=")
				val3 = line[p1+2:p1+19]
			if i == 11:
				p1 = line.find("=")
				val4 = line[p1+2:p1+19]
			if i == 7:
				p1 = line.find("=")
				val5 = line[p1+2:p1+19]
			if i == 6:
				p1 = line.find("=")
				val6 = line[p1+2:p1+19]
			if i == 3:		
				p1 = line.rfind("klocation=")
				val7 = line[p1+11:p1+26]	
				p2 = line.find("khisto=")
				val8 = line[p2+8:p2+25]		
				p3 = line.find("kappa=")
				val9 = line[p3+7:p3+24]
				p4 = line.find("frac_correct=")
				val10 = line[p4+14:p4+31]
		vct.append(val1)
		vct.append(val2)
		vct.append(val3)
		vct.append(val4)
		vct.append(val5)
		vct.append(val6)
		vct.append(val7)
		vct.append(val8)		
		vct.append(val9)		
		vct.append(val10)	
		offen.close()
		
# PROCESS CATEGORY ITEM 2
for file in PC2[:]:
	if file.find("acca1") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		acca1.append(val4)
		acca1.append(val3)
		acca1.append(val2)
		acca1.append(val1)		
		offen.close()
		
	if file.find("acca2") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		acca2.append(val4)
		acca2.append(val3)
		acca2.append(val2)
		acca2.append(val1)		
		offen.close()		
		
	if file.find("cmask") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		cmask.append(val4)
		cmask.append(val3)
		cmask.append(val2)
		cmask.append(val1)		
		offen.close()		
		
	if file.find("fmask_original") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		fmask_original.append(val4)
		fmask_original.append(val3)
		fmask_original.append(val2)
		fmask_original.append(val1)		
		offen.close()		

	if file.find("fmask_sav") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		fmask_sav.append(val4)
		fmask_sav.append(val3)
		fmask_sav.append(val2)
		fmask_sav.append(val1)		
		offen.close()			

	if file.find("ltk") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		ltk.append(val4)
		ltk.append(val3)
		ltk.append(val2)
		ltk.append(val1)		
		offen.close()	

	if file.find("vct") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		vct.append(val4)
		vct.append(val3)
		vct.append(val2)
		vct.append(val1)		
		offen.close()
		
# PROCESS CATEGORY ITEM 1
for file in PC1[:]:
	if file.find("acca1") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		acca1.append(val4)
		acca1.append(val3)
		acca1.append(val2)
		acca1.append(val1)		
		offen.close()
		
	if file.find("acca2") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		acca2.append(val4)
		acca2.append(val3)
		acca2.append(val2)
		acca2.append(val1)		
		offen.close()		
		
	if file.find("cmask") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		cmask.append(val4)
		cmask.append(val3)
		cmask.append(val2)
		cmask.append(val1)		
		offen.close()		
		
	if file.find("fmask_original") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		fmask_original.append(val4)
		fmask_original.append(val3)
		fmask_original.append(val2)
		fmask_original.append(val1)		
		offen.close()		

	if file.find("fmask_sav") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		fmask_sav.append(val4)
		fmask_sav.append(val3)
		fmask_sav.append(val2)
		fmask_sav.append(val1)		
		offen.close()			

	if file.find("ltk") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		ltk.append(val4)
		ltk.append(val3)
		ltk.append(val2)
		ltk.append(val1)		
		offen.close()	

	if file.find("vct") >= 0:
		input = input_folder + file
		offen = open(input, "r")		
		for i, line in enumerate(offen):
			if i == 3:
				p1 = line.find("in_both=")
				subset = line[p1:p1+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val1 = subset[ps1+1:ps2]
				p2 = line.find("in_none=")
				subset = line[p2:p2+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val2 = subset[ps1+1:ps2]
				p3 = line.find("map1=")
				subset = line[p3:p3+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val3 = subset[ps1+1:ps2]
				p4 = line.find("map2=")
				subset = line[p4:p4+20]		
				ps1 = subset.find('"')
				ps2 = subset.rfind('"')
				val4 = subset[ps1+1:ps2]						
		vct.append(val4)
		vct.append(val3)
		vct.append(val2)
		vct.append(val1)		
		offen.close()


# WRITE INTO OUTPUT CSV-FILE

out = open(output, "w")
for ac1 in acca1[::-1]:
	i = acca1.index(ac1)
	out.write(ac1 + "," + acca2[i] + "," + cmask[i] + "," + fmask_original[i] + "," +
	fmask_sav[i] + "," + ltk[i] + "," + vct[i] + "\n")
out.close
		




endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print("start: ", starttime)
print("end: ", endtime)




