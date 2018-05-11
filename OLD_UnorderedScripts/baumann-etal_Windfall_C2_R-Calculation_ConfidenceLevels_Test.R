################################################################################################################################################
#### DO THE ANALYSIS ####
RAW_table = read.table(file.choose(), header = T)
table = subset(RAW_table, Area_m2 > 5400)

table$table_Diff = table$R_B5_11_ST + table$TC_B_11_ST - table$TC_W_11_ST
table$Class = 0
table$Class[which(table$table_Diff < 0)] = 1
##################################################################################################################################################
#### CREATE SUBSET TABLE WITH ONLY THE STUFF WE WANT AND CALCULATE CASES ####
conf_table = subset(table, , c(Class, Wind01_New, Area_m2, TC_B_11_ST, TC_W_11_ST, R_B5_11_ST))
conf_table$Area_ha = conf_table$Area_m2 / 10000
conf_table$ErrorMatrix = "NA"
conf_table$ErrorMatrix = ifelse(conf_table$Class == 1 & conf_table$Wind01_New == 1, "True Windfall", conf_table$ErrorMatrix)
conf_table$ErrorMatrix = ifelse(conf_table$Class == 0 & conf_table$Wind01_New == 0, "True Other", conf_table$ErrorMatrix)
conf_table$ErrorMatrix = ifelse(conf_table$Class == 1 & conf_table$Wind01_New == 0, "False Windfall", conf_table$ErrorMatrix)
conf_table$ErrorMatrix = ifelse(conf_table$Class == 0 & conf_table$Wind01_New == 1, "False Other", conf_table$ErrorMatrix)
conf_table$ConfLevel_w = 0
conf_table$ConfLevel_o = 0

##################################################################################################################################################
#### CALCULATE CONFIDENCE LEVEL FOR WINDFALL ####
wind = subset(conf_table, ErrorMatrix == "True Windfall" | ErrorMatrix == "False Windfall")
wind$ConfLevel_w = 0
# Level 4 --> "not confident"
wind$ConfLevel_w = ifelse(wind$TC_B_11_ST >= 0 & wind$TC_W_11_ST <= 0 & wind$R_B5_11_ST >= 0, 4, wind$ConfLevel_w)
# Level 3 --> 'moderately confident"
wind$ConfLevel_w = ifelse(wind$TC_B_11_ST < 0 | wind$TC_W_11_ST > 0 | wind$R_B5_11_ST < 0, 3, wind$ConfLevel_w)
# Level 2 --> "Confident"
wind$ConfLevel_w = ifelse(wind$TC_B_11_ST < 0 & wind$TC_W_11_ST > 0, 2, wind$ConfLevel_w)
wind$ConfLevel_w = ifelse(wind$TC_B_11_ST < 0 & wind$R_B5_11_ST < 0, 2, wind$ConfLevel_w)
wind$ConfLevel_w = ifelse(wind$R_B5_11_ST < 0 & wind$TC_W_11_ST > 0, 2, wind$ConfLevel_w)
# Level 1 --> "very confident"
wind$ConfLevel_w = ifelse(wind$TC_B_11_ST <= 0 & wind$TC_W_11_ST >= 0 & wind$R_B5_11_ST <= 0, 1, wind$ConfLevel_w)
# Calculate confidences
levels = c(1,2,3,4)
p1 = nrow(subset(wind, ConfLevel_w == 1))
p2 = nrow(subset(wind, ConfLevel_w == 2))
p3 = nrow(subset(wind, ConfLevel_w == 3))
p4 = nrow(subset(wind, ConfLevel_w == 4))
pLevels = c(p1, p2, p3, p4)
s = subset(wind, ConfLevel_w == 1)
a1 = sum(s$Area_m2) / 1000000
s = subset(wind, ConfLevel_w == 2)
a2 = sum(s$Area_m2) / 1000000
s = subset(wind, ConfLevel_w == 3)
a3 = sum(s$Area_m2) / 1000000
s = subset(wind, ConfLevel_w == 4)
a4 = sum(s$Area_m2) / 1000000
aLevels = c(a1, a2, a3, a4)
rbind(levels, pLevels, aLevels)

##################################################################################################################################################
#### CALCULATE CONFIDENCE LEVEL FOR OTHER ####
other = subset(conf_table, ErrorMatrix == "True Other" | ErrorMatrix == "False Other")
other$ConfLevel_o = 0
# Level 4 --> "not confident"
other$ConfLevel_o = ifelse(other$TC_B_11_ST <= 0 & other$TC_W_11_ST >= 0 & other$R_B5_11_ST <= 0, 4, other$ConfLevel_o)
# Level 3 --> 'moderately confident"
other$ConfLevel_o = ifelse(other$TC_B_11_ST > 0 | other$TC_W_11_ST < 0 | other$R_B5_11_ST > 0, 3, other$ConfLevel_o)
# Level 2 --> "Confident"
other$ConfLevel_o = ifelse(other$TC_B_11_ST > 0 & other$TC_W_11_ST < 0, 2, other$ConfLevel_o)
other$ConfLevel_o = ifelse(other$TC_B_11_ST > 0 & other$R_B5_11_ST > 0, 2, other$ConfLevel_o)
other$ConfLevel_o = ifelse(other$R_B5_11_ST > 0 & other$TC_W_11_ST < 0, 2, other$ConfLevel_o)
# Level 1 --> "very confident"
other$ConfLevel_o = ifelse(other$TC_B_11_ST >= 0 & other$TC_W_11_ST <= 0 & other$R_B5_11_ST >= 0, 1, other$ConfLevel_o)
# Calculate confidences
levels = c(1,2,3,4)
p1 = nrow(subset(other, ConfLevel_o == 1))
p2 = nrow(subset(other, ConfLevel_o == 2))
p3 = nrow(subset(other, ConfLevel_o == 3))
p4 = nrow(subset(other, ConfLevel_o == 4))
pLevels = c(p1, p2, p3, p4)
s = subset(other, ConfLevel_o == 1)
a1 = sum(s$Area_m2) / 1000000
s = subset(other, ConfLevel_o == 2)
a2 = sum(s$Area_m2) / 1000000
s = subset(other, ConfLevel_o == 3)
a3 = sum(s$Area_m2) / 1000000
s = subset(other, ConfLevel_o == 4)
a4 = sum(s$Area_m2) / 1000000
aLevels = c(a1, a2, a3, a4)
rbind(levels, pLevels, aLevels)












