################################################################################################################################################
#### LOAD THE REQUIRED PACKAGES ####
library(grDevices)
library(RGraphics)
library(lattice)
library(gridExtra)
################################################################################################################################################
#### CREATE THE PLOT FOOTPRINT 026027  ####
table_026028 = read.table(file.choose(), header = T)

table = table_026028
table$Valida = as.factor(table$Valida)
table$Classifi = as.factor(table$Classifi)

plot_026027 <- cloud(TC_B_00_ST ~ R_B5_00_ST*TC_W_00_ST, groups = Valida, data = table,
                     col=c("#00008B","#8B0000"),#[table$Valida], # Set colours for the two groups
                     main = list("Minnesota (USA)", font = 1, cex = 2, x = 0.5, y = -0.5),
                     xlab = list("Band 5 Reflectance", rot = -30, font = 1, cex = 1.4),
                     ylab = list("Tasseled Cap Wetness", rot = 38, font = 1, cex = 1.4),
                     zlab = list("Tasseled Cap Brightness", rot = 95, font = 1, cex = 1.4),
                     panel.aspect = 1,
                     pch = 18,
                     scales = list(arrows=FALSE, cex=1.3, col="black", font = 1, tck = 0.7),
                     screen = list(z = 140, x = -60),
                     par.settings = list(axis.line = list(col = "transparent")), # makes outer box transparent
                     auto.key = list(x = 0.28, y = 0.94, size = 2, cex = 1.5,
                                     columns = 2,
                                     text = c("Other", "Windfall"),
                                     pch = 20
                                     )
                      )
                         
plot_026027                   
###########################################################################################################################################
#### CREATE THE PLOT FOR PATH/ROW 177/019 ####

RAW_177019 = read.table(file.choose(), header = T)

table_177019 = RAW_177019
table_177019$Valida = as.factor(table_177019$Valida)
table_177019$Classifi = as.factor(table_177019$Classifi)

plot_177019 <- cloud(TC_B_11_ST ~ R_B5_11_ST*TC_W_11_ST, groups = Valida, data = table_177019,
                     col = c("#00008B", "#8B0000"),
                     main = list("Russia", font = 1, cex = 2, x = 0.5, y = -0.5),
                     xlab = list("Band 5 Reflectance", rot = -30, font = 1, cex = 1.4),
                     ylab = list("Tasseled Cap Wetness", rot = 38, font = 1, cex = 1.4),
                     zlab = list("Tasseled Cap Brightness", rot = 95, font = 1, cex = 1.4),
                     panel.aspect = 1,
                     pch = 18,
                     scales = list(arrows=FALSE, cex=1.3, col="black", font = 1, tck = 0.7),
                     screen = list(z = 140, x = -60),
                     par.settings = list(axis.line = list(col = "transparent")), # makes outer box transparent
                     auto.key = list(x = 0.28, y = 0.94, size = 2, cex = 1.5,
                                     columns = 2,
                                     text = c("Other", "Windfall"),
                                     pch = 20
                                     )
                     )

plot_177019
###########################################################################################################################################
#### COMBINE THE TWO GRAPHS AND WRITE INTO OUTPUT ####
png("d:/TrainingPointValidation_3dPlot.png", width=4000,height=2000,res=300)
grid.arrange(arrangeGrob(plot_026027, plot_177019, nrow = 1))
dev.off()
