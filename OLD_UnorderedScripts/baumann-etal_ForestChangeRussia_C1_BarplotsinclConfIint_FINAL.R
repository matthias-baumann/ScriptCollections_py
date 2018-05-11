#### READ TABLE AND SET WORKSPACE ####
setwd("d:/Matthias/Publications/Publications-in-preparation/2011_Baumann-etal_Forest-covr-change-Russia/Figure_02")
table = read.table(file.choose(), header = T)


#### CREATE LIST FOR FOOTPRINTS AND BUILD ADDITIONAL COLUMNS FOR SECOND AND THIRD GRAPH ####
fps = c(176021, 166022, 167020, 169020, 171022, 172020, 174024, 175019, 179019, 179023, 181022, 183019)
table$diff = table$FC - table$FC_T1
table$rel_ch = (table$FC / table$FC_T1 - 1) * 100


for(fp in fps){
subset = subset(table, Footprint == fp)
x = subset$Year
y = subset$FC
u = subset$Upper_CI
v = subset$Lower_CI
z = subset$Net.Change_Error
zz = subset$Net.Change_Error_Perc
yy = subset$diff
yyy = subset$rel_ch
filename = c(fp, ".png")
filename = paste(filename, collapse="")
png(filename,width=4000,height=5000,res=600)
layout(matrix(c(1,1,1,2,2,3,3),7,1,byrow=TRUE))
layout.show(3)
par(mar=c(4,6,4,2)) 
plot1 = barplot(y, main = fp, xlab = "Year", ylab = expression("Forest area [ " * km^2 * "]"), names.arg = x, ylim = c(0,25000), cex=2, cex.main=3.5, cex.axis=2, cex.lab=2)
#mtext("Kostroma Region", line = -1)
arrows(x0 = 0.7, x1 = 0.7, y0 = v[1], y1 = u[1], code = 3, angle = 90, length = 0.05)
arrows(x0 = 1.9, x1 = 1.9, y0 = v[2], y1 = u[2], code = 3, angle = 90, length = 0.05)
arrows(x0 = 3.1, x1 = 3.1, y0 = v[3], y1 = u[3], code = 3, angle = 90, length = 0.05)
arrows(x0 = 4.3, x1 = 4.3, y0 = v[4], y1 = u[4], code = 3, angle = 90, length = 0.05)
arrows(x0 = 5.5, x1 = 5.5, y0 = v[5], y1 = u[5], code = 3, angle = 90, length = 0.05)
arrows(x0 = 6.7, x1 = 6.7, y0 = v[6], y1 = u[6], code = 3, angle = 90, length = 0.05)
plot2 = barplot(yy, ylab = expression("Net area change [ " * km^2 * "]"), ylim = c(-1000,1000), cex=1.8, cex.axis=2, cex.lab=2)
arrows(x0 = 1.9, x1 = 1.9, y0 = yy[2]-z[2], y1 = yy[2]+z[2], code = 3, angle = 90, length = 0.05)
arrows(x0 = 3.1, x1 = 3.1, y0 = yy[3]-z[3], y1 = yy[3]+z[3], code = 3, angle = 90, length = 0.05)
arrows(x0 = 4.3, x1 = 4.3, y0 = yy[4]-z[4], y1 = yy[4]+z[4], code = 3, angle = 90, length = 0.05)
arrows(x0 = 5.5, x1 = 5.5, y0 = yy[5]-z[5], y1 = yy[5]+z[5], code = 3, angle = 90, length = 0.05)
arrows(x0 = 6.7, x1 = 6.7, y0 = yy[6]-z[6], y1 = yy[6]+z[6], code = 3, angle = 90, length = 0.05)
plot3 = barplot(yyy, ylab = "Rel. area change [%]", ylim = c(-11,11), cex=1.8, cex.axis=2, cex.lab=2)
arrows(x0 = 1.9, x1 = 1.9, y0 = yyy[2]-zz[2], y1 = yyy[2]+zz[2], code = 3, angle = 90, length = 0.05)
arrows(x0 = 3.1, x1 = 3.1, y0 = yyy[3]-zz[3], y1 = yyy[3]+zz[3], code = 3, angle = 90, length = 0.05)
arrows(x0 = 4.3, x1 = 4.3, y0 = yyy[4]-zz[4], y1 = yyy[4]+zz[4], code = 3, angle = 90, length = 0.05)
arrows(x0 = 5.5, x1 = 5.5, y0 = yyy[5]-zz[5], y1 = yyy[5]+zz[5], code = 3, angle = 90, length = 0.05)
arrows(x0 = 6.7, x1 = 6.7, y0 = yyy[6]-zz[6], y1 = yyy[6]+zz[6], code = 3, angle = 90, length = 0.05)
dev.off()
}

#### WRITE FILES FOR SUM AND AVERAGE INTO FOLDER FOR FIGURE 03 ####
setwd("d:/Matthias/Publications/Publications-in-preparation/2011_Baumann-etal_Forest-covr-change-Russia/Figure_03")

subset = subset(table, Footprint == "Sum")
x = subset$Year
y = subset$FC
u = subset$Upper_CI
v = subset$Lower_CI
yy = subset$diff
yyy = subset$rel_ch
filename = c("Sum", ".png")
filename = paste(filename, collapse="")
png(filename,width=4000,height=5000,res=600)
layout(matrix(c(1,1,1,2,2,3,3),7,1,byrow=TRUE))
layout.show(3)
par(mar=c(4,6,4,2)) 
plot1 = barplot(y, main = "Sum", xlab = "Year", ylab = expression("Forest area [ " * km^2 * "]"), names.arg = x, ylim = c(0,200000), cex=2, cex.main=3.5, cex.axis=2, cex.lab=2)
#mtext("Kostroma Region", line = -1)
arrows(x0 = 0.7, x1 = 0.7, y0 = v[1], y1 = u[1], code = 3, angle = 90, length = 0.05)
arrows(x0 = 1.9, x1 = 1.9, y0 = v[2], y1 = u[2], code = 3, angle = 90, length = 0.05)
arrows(x0 = 3.1, x1 = 3.1, y0 = v[3], y1 = u[3], code = 3, angle = 90, length = 0.05)
arrows(x0 = 4.3, x1 = 4.3, y0 = v[4], y1 = u[4], code = 3, angle = 90, length = 0.05)
arrows(x0 = 5.5, x1 = 5.5, y0 = v[5], y1 = u[5], code = 3, angle = 90, length = 0.05)
arrows(x0 = 6.7, x1 = 6.7, y0 = v[6], y1 = u[6], code = 3, angle = 90, length = 0.05)
plot2 = barplot(yy, ylab = expression("Net area change [ " * km^2 * "]"), ylim = c(-5000,5000), cex=1.8, cex.axis=2, cex.lab=2)
plot3 = barplot(yyy, ylab = "Rel. area change [%]", ylim = c(-11,11), cex=1.8, cex.axis=2, cex.lab=2)
dev.off()

subset = subset(table, Footprint == "Average")
x = subset$Year
y = subset$FC
u = subset$Upper_CI
v = subset$Lower_CI
yy = subset$diff
yyy = subset$rel_ch
filename = c("Average", ".png")
filename = paste(filename, collapse="")
png(filename,width=4000,height=5000,res=600)
layout(matrix(c(1,1,1,2,2,3,3),7,1,byrow=TRUE))
layout.show(3)
par(mar=c(4,6,4,2)) 
plot1 = barplot(y, main = "Average", xlab = "Year", ylab = expression("Forest area [ " * km^2 * "]"), names.arg = x, ylim = c(0,25000), cex=2, cex.main=3.5, cex.axis=2, cex.lab=2)
#mtext("Kostroma Region", line = -1)
arrows(x0 = 0.7, x1 = 0.7, y0 = v[1], y1 = u[1], code = 3, angle = 90, length = 0.05)
arrows(x0 = 1.9, x1 = 1.9, y0 = v[2], y1 = u[2], code = 3, angle = 90, length = 0.05)
arrows(x0 = 3.1, x1 = 3.1, y0 = v[3], y1 = u[3], code = 3, angle = 90, length = 0.05)
arrows(x0 = 4.3, x1 = 4.3, y0 = v[4], y1 = u[4], code = 3, angle = 90, length = 0.05)
arrows(x0 = 5.5, x1 = 5.5, y0 = v[5], y1 = u[5], code = 3, angle = 90, length = 0.05)
arrows(x0 = 6.7, x1 = 6.7, y0 = v[6], y1 = u[6], code = 3, angle = 90, length = 0.05)
plot2 = barplot(yy, ylab = expression("Net area change [ " * km^2 * "]"), ylim = c(-1000,1000), cex=1.8, cex.axis=2, cex.lab=2)
plot3 = barplot(yyy, ylab = "Rel. area change [%]", ylim = c(-11,11), cex=1.8, cex.axis=2, cex.lab=2)
dev.off()
