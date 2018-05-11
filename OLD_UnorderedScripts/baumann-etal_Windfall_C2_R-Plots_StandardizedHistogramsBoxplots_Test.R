#### LOAD PACKAGES, NEEDED TO CREATE THE PLOTS ####
library(ggplot2)
library(gregmisc)

#### LOAD DATA TABLE AND SET INTIAL WORKSPACE ####
RAW_table = read.table(file.choose(), header = T)

#### EXCLUDE DISTURBANCES THAT ARE SMALLER THAN 7 PIXEL, CALCULATE ALSO AXIS-RATIO ####
table = subset(RAW_table, Area_m2 > 5400)
table$AXIS_Ratio = table$MAJORAXIS / table$MINORAXIS

######################################################################
#### CREATE ALL COMBINATIONS OF VARIABLES, FOR THE ENTIRE DATASET ####

#### SET WORSPACE FOR OUTPUT ####
workDir = "D:/Matthias/Projects-and-Publications/Publications-in-preparation/Baumann-etal_Windfall-classification_RSE"
setwd(workDir)

#### Normalize Geometric Variables ####
table$Area_m2_ST = (table$Area_m2 - mean(table$Area_m2))/sd(table$Area_m2)
table$Perim_m_ST = (table$Perim_m - mean(table$Perim_m))/sd(table$Perim_m)
table$ArePeriRat_ST = (table$ArePeriRat - mean(table$ArePeriRat))/sd(table$ArePeriRat)
table$THICKNESS_ST = (table$THICKNESS - mean(table$THICKNESS))/sd(table$THICKNESS)
table$MINORAXIS_ST = (table$MINORAXIS - mean(table$MINORAXIS))/sd(table$MINORAXIS)
table$MAJORAXIS_ST = (table$MAJORAXIS - mean(table$MAJORAXIS))/sd(table$MAJORAXIS)
table$AXIS_Ratio_ST = (table$AXIS_Ratio - mean(table$AXIS_Ratio))/sd(table$AXIS_Ratio)

#### CREATE ALL PERMUTATIONS, NOTE: REMOVE FIRST COLUMN '2', '38', '39' TO AVOID "NO-VARIABLES" ####
IndVars = subset(table, , c(R_B5_11_ST, TC_W_11_ST, TC_G_11_ST, TC_B_11_ST, R_B5DIF_ST, Area_m2_ST, Perim_m_ST, ArePeriRat_ST, THICKNESS_ST, MINORAXIS_ST, MAJORAXIS_ST, AXIS_Ratio_ST))
response = table$Wind01_New

No_variables = length(colnames(IndVars))
combos = combinations(No_variables, 3, repeats = FALSE)
nr_combos = length(combos)/3

#### NOW START LOOPING THROUGH THE DATASET ####
for (i in 1:nr_combos) {

#### CREATE SUBSET-TABLE, VARIABLE-NAMES AND OUTPUT-FILE-NAME ####
sub = subset(IndVars, select = c(combos[i,1],combos[i,2]))
sub = cbind(sub,response)
colnames(sub)[3] = "WindDis"
sub$WindDis = factor(sub$WindDis, labels = c("Other", "Windfall"))
y_name = colnames(sub[2])
x_name = colnames(sub[1])
outfile = c(x_name, "_vs_", y_name, ".png")
outfile = paste(outfile, collapse = "")
title = c(x_name, " vs. ", y_name)
title = paste(title, collapse = "")

#### NOW START MAKING THE PLOT ####
ggplot(data = sub, aes(sub[,1], sub[,2])) + 
geom_point(aes(colour = sub[,3]), size = 1.5, show_guide = FALSE, alpha = 1/3) +
opts(title = title) +
ylab(y_name) +
xlab(x_name) +
ggsave(outfile, dpi = 96, scale = 0.8)

#### END LOOP ####
}

#### CREATE THE BOXPLOTS ####

#### RE-CREATE THE VARIABLE NAMES ####
nr_cols = ncol(IndVars)

#### NOW START LOOPING THROUGH THE COLUMNS ####
for (i in 1:nr_cols) {

#### CREATE THE TABLE THAT WE NEED TO 
sub = subset(IndVars, select = c(i))
sub = cbind(sub, response)
colnames(sub)[2] = "WindDis"
sub$WindDis = factor(sub$WindDis, labels = c("Other", "Windfall"))
y_name = colnames(sub[1])
outfile = c(colnames(sub[1]), ".png")
outfile = paste(outfile, collapse = "")
title = c(colnames(sub[1]))

#### NOW START CREATING THE BOXPLOT ####
ggplot(sub, aes(WindDis, sub[,1])) +
geom_boxplot() + 
opts(title = title) +
ylab("") + 
xlab("") +
ggsave(outfile, dpi = 96, scale = 0.8)

#### END LOOP ####
}


#### CREATE HISTOGRAMS ####
for (i in 1:nr_cols) {

#### CREATE THE TABLE THAT WE NEED TO 
sub = subset(IndVars, select = c(i))
sub = cbind(sub, response)
colnames(sub)[2] = "WindDis"
sub$WindDis = factor(sub$WindDis, labels = c("Other", "Windfall"))
outfile = c(colnames(sub[1]), "_histo.png")
outfile = paste(outfile, collapse = "")
title = c(colnames(sub[1]))

#### NOW START CREATING THE BOXPLOT ####
ggplot(sub, aes(x = sub[,1], fill = WindDis)) +
geom_histogram(binwidth = 0.2, alpha = 0.5, position = "identity") + 
opts(title = title) +
ylab("") + 
xlab("")

ggsave(outfile, dpi = 96, scale = 0.8)

#### END LOOP ####
}





