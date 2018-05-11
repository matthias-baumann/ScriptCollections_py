setwd("d:/Matthias/Publications/Publications-in-preparation/2011_Baumann-etal_Forest-covr-change-Russia/Figure_03")
table = read.table(file.choose(), header = T)


# CREATE A TABLE FOR OVERALL ACCURACY COMPARISON
subset = subset(table, Param == "Acc")
subsub = subset(subset, Winter == "Single-Image")
single = c(subsub$Value)
subsub = subset(subset, Winter == "Image-Stack")
combo = c(subsub$Value)
data = rbind(single, combo)
png("Overall-Accuracy.png", width=4000,height=4000,res=600)
barplot(data, beside = T, main = "Overall accuracy", ylab = "Overall Classification Accuracy [%]", names.arg = c("179023(1)","179023(2)","169020","167020"), ylim = c(90,100), cex = 1.5, cex.main = 3, cex.axis=1.6, cex.lab=1.6, xpd = F, legend.text = c("Single Image", "Including Winter Image"))
dev.off()

# CREATE A TABLE FOR OVERALL KAPPA COMPARISON
subset = subset(table, Param == "Kappa")
subsub = subset(subset, Winter == "Single-Image")
single = c(subsub$Value)
subsub = subset(subset, Winter == "Image-Stack")
combo = c(subsub$Value)
data = rbind(single, combo)
png("Kappa.png", width=4000,height=4000,res=600)
barplot(data, beside = T, main = "Kappa Statistic", ylab = "Kappa value", names.arg = c("179023(1)","179023(2)","169020","167020"), ylim = c(0.8,1), cex = 1.5, cex.main = 3, cex.axis=1.6, cex.lab=1.6, xpd = F, legend.text = c("Single Image", "Including Winter Image"))
dev.off()

# CREATE A TABLE FOR OVERALL F1 COMPARISON
subset = subset(table, Param == "F-Meas")
subsub = subset(subset, Winter == "Single-Image")
single = c(subsub$Value)
subsub = subset(subset, Winter == "Image-Stack")
combo = c(subsub$Value)
data = rbind(single, combo)
png("F-Measure.png", width=4000,height=4000,res=600)
barplot(data, beside = T, main = "Averaged F-Measure", ylab = "Averaged F-Measure [%]", names.arg = c("179023(1)","179023(2)","169020","167020"), ylim = c(90,100), cex = 1.5, cex.main = 3, cex.axis=1.6, cex.lab=1.6, xpd = F, legend.text = c("Single Image", "Including Winter Image"))
dev.off()