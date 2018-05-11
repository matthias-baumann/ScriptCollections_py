#### READ IN TABLE AND THEN SUBSET IT BY PICKING ONLY COLUMNS THAT WE NEED ####
table = read.table(file.choose(), header = T)

# REMVOE UNCATEGOZIRED PLOTS
table = subset(table, Plot_Char != "EMPTY")

# REMOVE ALL PLOTS THAT ARE SMALLER THAN 11PX (WHICH IS OUR MMU)
table = subset(table, Area_m2 >= 10000)

# CONSOLIDATE CONIFEROUS AND DECIDIOUS INTO ONE COLUMN (SUM THEM UP)
table$Class = "EMPTY"

# REMOVE ALL PLOTS THAT DO NOT HAVE ANY PIXELS FROM THE MAP IN IT
table = subset(table, Coni_px > 0 | Decid_px > 0 | Mixed_px > 0 | Other_px > 0)

# CALCULATE PERCENTAGES FROM CLASSIFICATION
table$PercConi = (table$Coni_px/(table$Coni_px + table$Mixed_px + table$Decid_px))*100
table$PercMixed = (table$Mixed_px/(table$Coni_px + table$Mixed_px + table$Decid_px))*100
table$PercDeci = (table$Decid_px/(table$Coni_px + table$Mixed_px + table$Decid_px))*100

table$Coni_Prezi = ((table$Coni_px + 0.5*table$Mixed_px)/(table$Coni_px + table$Mixed_px + table$Decid_px))*100
table$Deci_Prezi = ((table$Decid_px + 0.5*table$Mixed_px)/(table$Coni_px + table$Mixed_px + table$Decid_px))*100

# MAKE CLASS DECISION
table$Class = ifelse(table$PercMixed > 70, "MF", table$Class)
table$Class = ifelse(table$PercConi > 70, "CF", table$Class)
table$Class = ifelse(table$PercDeci > 70, "DF", table$Class)

table$Class = ifelse(table$Coni_Prezi >= 70 & table$PercConi <= 70, "CF", table$Class)
table$Class = ifelse(table$Deci_Prezi >= 70 & table$PercDeci <= 70, "DF", table$Class)

table$Class = ifelse(table$Coni_Prezi < 70 & table$Deci_Prezi < 70, "MF", table$Class)

# RE-CODE THE 'PLOT_CHAR'-FIELD
table$Vali = ifelse(table$Plot_Char == "CC", "CF", "EMPTY")
table$Vali = ifelse(table$Plot_Char == "CD", "DF", table$Vali)
table$Vali = ifelse(table$Plot_Char == "MC", "MF", table$Vali)
table$Vali = ifelse(table$Plot_Char == "MD", "MF", table$Vali)

# CREATE ERROR MATRIX
accuracy_table = subset(table, , c(Class, Vali))
table(accuracy_table)


#### WRITE INTO OUTPUT-TXT-FILE, SEPARATED BY KOMMAS ####
write.table(table, file = "X:/mbaumann/Griffiths-etal_ForestChange-Carpathians_AccuracyAssessment/DataProcessing/Romania_1985_AccuracyAssessment_Output_revision.txt", sep = ",")