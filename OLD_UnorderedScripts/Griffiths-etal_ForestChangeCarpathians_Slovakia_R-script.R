#### READ IN TABLE AND THEN SUBSET IT BY PICKING ONLY COLUMNS THAT WE NEED ####
table = read.table(file.choose(), header = T)

subset_table = subset(table, , c(ID,Area_ha,DR1,ZS1,DR2,ZS2,DR3,ZS3,DR4,ZS4,DR5,ZS5,DR6,ZS6,DR7,ZS7,DR8,ZS8))

# Remove empty plots
subset_table = subset(subset_table, ZS1 > 0)


#### CREATE LISTS 'DECIDIOUS' AND 'CONIFEROUS' ####
decidious = c("DL","DZ", "DC", "DP", "CR", "DX", "DS", "BK", "HB", "BH", "BP", "VZ", "BD", "JH", "JM", "JP", 
              "JT", "JI", "JU", "JS", "JA", "JK", "JJ", "PJ", "JL", "JX", "JZ", "BR", "BA", "LM", "LV", "AG",
              "VB", "VF", "VK", "VV", "JB", "MK","BX", "OK", "TB", "TC", "TI", "TR", "OS", "CS", "MH", "OC",
              "OV", "GJ", "GK", "TP", "HR", "JN", "PL", "OH", "BZ", "DR", "HJ", "HO", "DB", "LP", "VR", "TD", "TS")

coniferous = c("SM", "SP", "SO", "JD", "JO", "BO", "BC", "BS", "KS", "VJ", "LB", "BB", "DG", "SC", "SJ", "TX", "BV")


#### START ANALYSIS ####

# ADD NEW COLUMNS FOR THE ANALYSIS
subset_table$DR1_CD = as.character(subset_table$DR1)
subset_table$DR2_CD = as.character(subset_table$DR2)
subset_table$DR3_CD = as.character(subset_table$DR3)
subset_table$DR4_CD = as.character(subset_table$DR4)
subset_table$DR5_CD = as.character(subset_table$DR5)
subset_table$DR6_CD = as.character(subset_table$DR6)
subset_table$DR7_CD = as.character(subset_table$DR7)
subset_table$DR8_CD = as.character(subset_table$DR8)

# REPLACE DECIDIOUS FOREST TYPE WITH 'D' IN NEW COLUMS
for (i in decidious){
  subset_table$DR1_CD[subset_table$DR1_CD == i] = "D"
  subset_table$DR2_CD[subset_table$DR2_CD == i] = "D"
  subset_table$DR3_CD[subset_table$DR3_CD == i] = "D"
  subset_table$DR4_CD[subset_table$DR4_CD == i] = "D"
  subset_table$DR5_CD[subset_table$DR5_CD == i] = "D"
  subset_table$DR6_CD[subset_table$DR6_CD == i] = "D"
  subset_table$DR7_CD[subset_table$DR7_CD == i] = "D"
  subset_table$DR8_CD[subset_table$DR8_CD == i] = "D"
}

# REPLACE CONIFEROUS FOREST TYPE WITH 'C' IN NEW COLUMS
for (i in coniferous){
  subset_table$DR1_CD[subset_table$DR1_CD == i] = "C"
  subset_table$DR2_CD[subset_table$DR2_CD == i] = "C"
  subset_table$DR3_CD[subset_table$DR3_CD == i] = "C"
  subset_table$DR4_CD[subset_table$DR4_CD == i] = "C"
  subset_table$DR5_CD[subset_table$DR5_CD == i] = "C"
  subset_table$DR6_CD[subset_table$DR6_CD == i] = "C"
  subset_table$DR7_CD[subset_table$DR7_CD == i] = "C"
  subset_table$DR8_CD[subset_table$DR8_CD == i] = "C"
}

subset_table = parking




# CONSOLIDATE CONIFEROUS AND DECIDIOUS INTO ONE COLUMN (SUM THEM UP)
subset_table$Perc_Dec = 0
subset_table$Perc_Con = 0

subset_table$D_S1 = ifelse(subset_table$DR1_CD == "D", subset_table$ZS1, 0)
subset_table$D_S2 = ifelse(subset_table$DR2_CD == "D", subset_table$ZS2, 0)
subset_table$D_S3 = ifelse(subset_table$DR3_CD == "D", subset_table$ZS3, 0)
subset_table$D_S4 = ifelse(subset_table$DR4_CD == "D", subset_table$ZS4, 0)
subset_table$D_S5 = ifelse(subset_table$DR5_CD == "D", subset_table$ZS5, 0)
subset_table$D_S6 = ifelse(subset_table$DR6_CD == "D", subset_table$ZS6, 0)
subset_table$D_S7 = ifelse(subset_table$DR7_CD == "D", subset_table$ZS7, 0)
subset_table$D_S8 = ifelse(subset_table$DR8_CD == "D", subset_table$ZS8, 0)

subset_table$C_S1 = ifelse(subset_table$DR1_CD == "C", subset_table$ZS1, 0)
subset_table$C_S2 = ifelse(subset_table$DR2_CD == "C", subset_table$ZS2, 0)
subset_table$C_S3 = ifelse(subset_table$DR3_CD == "C", subset_table$ZS3, 0)
subset_table$C_S4 = ifelse(subset_table$DR4_CD == "C", subset_table$ZS4, 0)
subset_table$C_S5 = ifelse(subset_table$DR5_CD == "C", subset_table$ZS5, 0)
subset_table$C_S6 = ifelse(subset_table$DR6_CD == "C", subset_table$ZS6, 0)
subset_table$C_S7 = ifelse(subset_table$DR7_CD == "C", subset_table$ZS7, 0)
subset_table$C_S8 = ifelse(subset_table$DR8_CD == "C", subset_table$ZS8, 0)




subset_table$Perc_Dec = subset_table$D_S1 + subset_table$D_S2 + subset_table$D_S3 + subset_table$D_S4 + subset_table$D_S5 + subset_table$D_S6 + subset_table$D_S7 + subset_table$D_S8
subset_table$Perc_Con = subset_table$C_S1 + subset_table$C_S2 + subset_table$C_S3 + subset_table$C_S4 + subset_table$C_S5 + subset_table$C_S6 + subset_table$C_S7 + subset_table$C_S8

subset_table = subset(subset_table, ,-c(D_S1, D_S2, D_S3, D_S4, D_S5, D_S6, D_S7, D_S8, C_S1, C_S2, C_S3, C_S4, C_S5, C_S6, C_S7, C_S8))


# MAKE FINAL CALL BETWEEN "CD" (CLEAR DECIDIOUS), "CC" (CLEAR CONIFEROUS), "MD" (MIXED DECIDIOUS), "MC" (MIXED CONIFEROUS)
subset_table$Plot_Char = "EMPTY"
subset_table$Plot_Char[subset_table$Perc_Dec >= 70] = "CD"
subset_table$Plot_Char[subset_table$Perc_Con >= 70] = "CC"
subset_table$Plot_Char[subset_table$Perc_Dec < 70 & subset_table$Perc_Dec >= 50] = "MD"
subset_table$Plot_Char[subset_table$Perc_Con < 70 & subset_table$Perc_Con > 50] = "MC"

#### WRITE INTO OUTPUT-TXT-FILE, SEPARATED BY KOMMAS ####
write.table(subset_table, file = "E:/tempdata/mbaumann/Carpathian_AccuracyAssessment/DataProcessing/Slovakia_output2.txt", sep = ",")