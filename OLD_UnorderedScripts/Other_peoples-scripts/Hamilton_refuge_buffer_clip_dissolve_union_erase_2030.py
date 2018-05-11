# IMPORT SYSTEM MODULES
from __future__ import division
import sys, string, os, arcgisscripting, time, math

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# CREATE THE GEOPROCESSOR OBJECT
print "CREATING GEOPROCESSOR OBJECT"
gp = arcgisscripting.create(9.3)

# ----- DEFINE INPUTS
workDir = "F:/DataF/chamilton/NWR_housing_2030/"
NWRShp = workDir + "NWRs_low48_alb_dissolved_multi.shp"
pbgFile = "F:/DataF/dhelmers/census_old/us_pbg00_2007.gdb/us_pbg00_Oct_8_2007"


# ------- PROCESSING

# create file for  each NWR
rows = gp.SearchCursor(NWRShp)
row = rows.Next()
while row:

	# string processing - replace naughty characters
	orgname = row.ORGNAME
	orgname = orgname.replace("-", "_")
	orgname = orgname.replace("'", "_")
	orgname = orgname.replace(".", "_")
	orgname = orgname.replace(",", "_")
	orgname = orgname.replace(" ", "_")
	
	print orgname
	
	# create NWR boundary file
	selectout = workDir + "NWRs_01/" + orgname + ".shp"
	if not gp.Exists(selectout):
		expr = '"ORGNAME" = ' + "'" + row.ORGNAME + "'"
		print expr
		print "gp= SELECT ->", selectout
		gp.Select_analysis(NWRShp,selectout,expr)
	else:
		print selectout, "already exists...skipping SELECT"		
	
	# buffer NWR at 50, 25, 10, 5, 1 km
	distList = ["1","5","10","25","50"]   # list furthest distance last !!!
	for dist in distList:
		bufferout = workDir+ "buffers_02/" + dist + "/" + orgname + "_buff" + dist + "km.shp"
		if not gp.Exists(bufferout):
			unit = dist + " Kilometers"
			print "gp= BUFFER ->", bufferout
			gp.Buffer_analysis(selectout,bufferout,unit,"FULL","ROUND","ALL")
		else:
			print bufferout, "already exists...skipping BUFFER"
	
	# clip PBG at furthest buffer distance
	clipout = workDir + "pbg_clip_03/" + orgname + "_buff" + dist + "km_PBG.shp"
	if not gp.Exists(clipout):
		print "gp= CLIP ->", clipout
		gp.Clip_analysis(pbgFile,bufferout,clipout)
	else:
		print clipout, "already exists...skipping CLIP"
		
	# union NWR boundary with PBG clip and add density class field
	unionout = workDir + "union_04/" + orgname + "_buff" + dist + "km_PBG_refuge.shp"
	if not gp.Exists(unionout):
		print "gp= UNION ->", unionout
		unioninput = clipout + "; " + selectout
		gp.Union_analysis(unioninput, unionout)
		
		# Add density class field
			# cutoffs
		very_low = 6.177635
		low = 49.42108
		med = 741.3162
		
		
		
		print "gp= AddField -> DENS_CLASS" 
		gp.AddField_management(unionout,"DENS_CLASS","LONG")
		print "gp= AddField -> TERRA" 
		gp.AddField_management(unionout,"TERRA","LONG")
		print "gp= AddField -> TERRA_AQUA" 
		gp.AddField_management(unionout,"TERRA_AQUA","LONG")
		rows2 = gp.UpdateCursor(unionout)
		row2 = rows2.Next()
		while row2:

			if row2.HDEN30 == 0: row2.DENS_CLASS = 0
			if row2.HDEN30 > 0 and row2.HDEN30 <= very_low: row2.DENS_CLASS = 1
			if row2.HDEN30 > very_low and row2.HDEN30 <= low: row2.DENS_CLASS = 2
			if row2.HDEN30 > low and row2.HDEN30 <= med: row2.DENS_CLASS = 3
			if row2.HDEN30 > med: row2.DENS_CLASS = 4
			
			if len(row2.ORGNAME) > 1: row2.DENS_CLASS = 1 
			if row2.WATER00 == 1: row2.DENS_CLASS = -999
			
			if row2.DENS_CLASS <= 1: 
				row2.TERRA_AQUA = 1
				if row2.DENS_CLASS == -999:
					row2.TERRA = 0
				else:
					row2.TERRA = 1
			else:
				row2.TERRA_AQUA = 0
			
			rows2.UpdateRow(row2)
			row2 = rows2.Next()
	else:
		print unionout, "already exists...skipping UNION"
	
	# dissolve on Density Classes
	
		# terra
	dissolveout1 = workDir + "terra_05a/" + dist + "/" + orgname + "_buff" + dist + "km_PBG_terra.shp"
	if not gp.Exists(dissolveout1):
		print "gp= DISSOLVE ->", dissolveout1
		gp.Dissolve_management(unionout,dissolveout1,"TERRA","","SINGLE_PART")
	else:
		print dissolveout1, "already exists...skipping TERRA"
	
		# terra_aqua
	dissolveout2 = workDir + "aqua_terra_05b/" + dist + "/" + orgname + "_buff" + dist + "km_PBG_aqua_terra.shp"
	if not gp.Exists(dissolveout2):
		print "gp= DISSOLVE ->", dissolveout2
		gp.Dissolve_management(unionout,dissolveout2,"TERRA_AQUA","","SINGLE_PART")
	else:
		print dissolveout2, "already exists...skipping TERRA_AQUA"
	
	
	# clip out for remaining buffer distances
	distList2 = ["1","5","10","25"]   # remove last distance from above !!!
	for dist2 in distList2:
	
		clipfile = workDir + "buffers_02/" + dist2 + "/" + orgname + "_buff" + dist2 + "km.shp"
	
			# terra
		terraclip = workDir + "terra_05a/" + dist2 + "/" + orgname + "_buff" + dist2 + "km_PBG_terra.shp"
		if not gp.Exists(terraclip):
			print "gp= CLIP ->", terraclip
			gp.Clip_analysis(dissolveout1,clipfile,terraclip)
		else:
			print terraclip, "already exists...skipping TERRA CLIP"
			
			# terra aqua
		aquaclip = workDir + "aqua_terra_05b/" + dist2 + "/" + orgname + "_buff" + dist2 + "km_PBG_aqua_terra.shp"
		if not gp.Exists(aquaclip):
			print "gp= CLIP ->", aquaclip
			gp.Clip_analysis(dissolveout2,clipfile,aquaclip)
		else:
			print aquaclip, "already exists...skipping TERRA_AQUA CLIP"
		

		
	# erase refuge from all dissolved buffer files
	distList3 = ["1","5","10","25","50"]
	for dist3 in distList3:
	
		terraout = workDir + "terra_erase_06a/" + dist3 + "/" + orgname + "_buff" + dist3 + "km_PBG_terra_no_nwr.shp"
		if not gp.exists(terraout):
			terraerase = workDir + "terra_05a/" + dist3 + "/" + orgname + "_buff" + dist3 + "km_PBG_terra.shp"
			print "gp= Erase ->", terraout
			gp.Erase_analysis(terraerase, selectout, terraout)
		else:
			print terraout, "already exists...skipping TERRA ERASE NWR"
	
		aquaout = workDir + "aqua_terra_erase_06b/" + dist3 + "/" + orgname + "_buff" + dist3 + "km_PBG_aqua_terra_no_nwr.shp"
		if not gp.exists(aquaout):
			aquaerase = workDir + "aqua_terra_05b/" + dist3 + "/" + orgname + "_buff" + dist3 + "km_PBG_aqua_terra.shp"
			print "gp= Erase ->", aquaout
			gp.Erase_analysis(aquaerase, selectout, aquaout)
		else:
			print aquaout, "already exists...skipping AQUA TERRA ERASE NWR"
		
	# dissolve on Density Classes
	distList4 = ["1","5","10","25","50"]
	for dist4 in distList4:
	
		# terra
	dissolveout3 = workDir + "terra_dissolve2_07a/" + dist4 + "/" + orgname + "_buff" + dist4 + "km_PBG_terra_dissolve.shp"
	if not gp.Exists(dissolveout3):
		print "gp= DISSOLVE ->", dissolveout3
		gp.Dissolve_management(terraout,dissolveout3,"TERRA","","SINGLE_PART")
	else:
		print dissolveout3, "already exists...skipping TERRA...I blame Helmers"
	
		# terra_aqua
	dissolveout4 = workDir + "aqua_terra_dissolve2_07b/" + dist4 + "/" + orgname + "_buff" + dist4 + "km_PBG_aqua_terra_dissolve.shp"
	if not gp.Exists(dissolveout4):
		print "gp= DISSOLVE ->", dissolveout4
		gp.Dissolve_management(aquaout,dissolveout4,"TERRA_AQUA","","SINGLE_PART")
	else:
		print dissolveout4, "already exists...skipping TERRA_AQUA...I blame Helmers"
		
	print 
	row = rows.Next()



endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
