#### READ IN RAW-TABLE AND EXCLUDE ALL DISTURBANCE SITES OF <7px ####
RAW_table = read.table(file.choose(), header = T)
table = subset(RAW_table, Area_m2 > 5400)
library(ggplot2)
#### Normalize Geometric Variables ####
#### DEFINE OUTPUT FILE AND WORKING DIRECTORY IN CASE WE NEED IT ####
workDir = "D:/Matthias/Projects-and-Publications/Publications-in-preparation/Baumann-etal_Windfall-classification_RSE"
setwd(workDir)

#### VARIABLE-COMBINATION ####
table$AXIS_Ratio = table$MAJORAXIS / table$MINORAXIS
table$table_Diff = table$R_B5_11_ST + table$TC_B_11_ST - table$TC_W_11_ST
table$Class = 0

#### CODE CLASSIFICATION FIELD BASED ON VALUE IN DIFF-FIELD ####
table$Class[which(table$table_Diff < -0.5)] = 1

#### ASSESS THE ACCURACY OF THIS COMBINATION ####
accuracy_table = subset(table, , c(Class, Wind01_New, Area_m2, Perim_m, ArePeriRat, THICKNESS, MAJORAXIS, MINORAXIS, AXIS_Ratio, R_B5_11_ST, TC_B_11_ST, TC_W_11_ST))
colnames(accuracy_table) = c("Classification", "Validation", "Area_m2", "Perimeter_m", "Area_Perimeter_Ratio", "Thickness", "Majoraxis", "Minoraxis", "Axis_Ratio", "R_B5_11", "TC_B_11", "TC_W_11")
accuracy_table$Classification = as.factor(accuracy_table$Classification)
levels(accuracy_table$Classification) = c("Classification_Other", "Classification_Windfall")
accuracy_table$Validation = as.factor(accuracy_table$Validation)
levels(accuracy_table$Validation) = c("Validation_Other", "Validation_Windfall")

#### BUILD ON THE PLOTS ####

plot <- ggplot(accuracy_table, aes(x=log(Area_m2))) + geom_histogram(binwidth=0.25,colour="black")
plot + facet_grid(Classification ~ Validation)





plot <- ggplot(accuracy_table, aes(x=Axis_Ratio)) + geom_histogram(binwidth=0.5,colour="black")
plot + facet_grid(Classification ~ Validation)




