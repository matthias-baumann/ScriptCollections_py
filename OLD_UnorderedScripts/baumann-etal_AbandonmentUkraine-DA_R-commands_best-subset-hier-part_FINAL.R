data = read.table(file.choose(), header = T)
data
xvariables = cbind(data(,[c(data$X1-data$X12)])
xvariables = cbind(data[,c(data$X1-data$X12)])
xvariables
xvariables = cbind(data[c(data$X1-data$X12)])
xvariables
xvariables = cbind(data(c(data$X1-data$X12)))
xvariables = cbind(data[c(data$X1-data$X12)])
xvariables
data
xvariables = cbind(data[c(data$X1-data$X12)])
xvariables
data
?subset
data = read.table(file.choose(), header = F)
data
xvariables = data[,2:13]
xvariables
library(leaps)
yvariable = data[,1]
yvariable
leaps(y=yvariable, x=xvariables)
leaps(y=yvariable, x=xvariables, nbest = 20, method = "adjr2")
adjr2.bestsubset = cbind(leaps$size, leaps$adjr2)
cbind(leaps$size, leaps$adjr2)
adjr2.bestsubset = cbind(leaps$which, leaps$adjr2)
leaps$size
bestsubset = leaps(y=yvariable, x=xvariables, nbest = 20, method = "adjr2")
bestsubset
cbind(bestsubset$size, bestsubset$adjr2)
library(hier.part)
utils:::menuInstallPkgs()
mod4.1 = data[,2,3]
mod4.1
data
mod4.1 = data[,V2,V3]
attach(data)
mod4.1 = data[,V2,V3]
mod4.1
xvariables
mod4.1 = cbind(xvariables[,c(1,5,9,10)])
mod4.1
hierpart(yvariable,mod4.1)
hier.part(yvariable,mod4.1)
library(hier.part)
hier.part(yvariable,mod4.1)
hier.part(yvariable,mod4.1[,-1])
hier.part(yvariable,mod4.1)
mod4.2 = cbind(xvariables[,c(1,9,11,12)])
hier.part(yvariable,mod4.2)
mod4.3 = cbind(xvariables[,c(1,5,9,11)])
hier.part(yvariable,mod4.3)
mod4.4 = cbind(xvariables[,c(1,4,5,10)])
hier.part(yvariable,mod4.4)
mod4.5 = cbind(xvariables[,c(1,5,11,12)])
hier.part(yvariable,mod4.5)
data.table = read.table(file.choose(), header = T)
data.table
yvariable = data.table[,1]
yvariable
yvariable = cbind(data.table[c(,1)])
y.variable = cbind(data.table[,c(data$X1-data$X12)])
data.table = read.table(file.choose(), header = F)
data.table
attach(data.table)
detach(data.table)
data.table
yvariable = data.table[,1]
yvariable
y.variable = data.table[,1]
y.variable
x.variables = data.table[,2:20]
x.variables
library(leaps)
best.subset = leaps(y = y.variable, x = x.variables, nbest = 20, method = "adjr2")
best.subset
data.table = read.table(file.choose(), header = F)
data.table
yvariable = data.table[,1]
x.variables = data.table[,2:19]
y.variable = yvariable
x.variables
y.variable
best.subset = leaps(y = y.variable, x = x.variables, nbest = 20, method = "adjr2")
best.subset
cbind(best.subset$size, best.subset$adjr2)
mod4.1 = cbind(x.variables[,c(5,10,14,15)])
hier.part(y.variable,mod4.1)
x.variables
mod4.2 = cbind(x.variables[,c(1,9,11,15)])
hier.part(y.variable,mod4.2)
mod4.3 = cbind(x.variables[,c(1,4,6,15)])
hier.part(y.variable,mod4.3)
mod4.4 = cbind(x.variables[,c(1,5,10,15)])
hier.part(y.variable,mod4.4)
mod4.5 = cbind(x.variables[,c(1,5,9,15)])
hier.part(y.variable,mod4.5)
mod4.6 = cbind(x.variables[,c(5,10,14,15)])
hier.part(y.variable,mod4.6)
mod4.6 = cbind(x.variables[,c(5,11,14,15)])
hier.part(y.variable,mod4.6)
mod4.7 = cbind(x.variables[,c(1,9,11,17)])
hier.part(y.variable,mod4.7)
mod4.8 = cbind(x.variables[,c(5,10,15,18)])
hier.part(y.variable,mod4.8)
mod4.9 = cbind(x.variables[,c(9,11,14,15)])
hier.part(y.variable,mod4.9)
mod4.10 = cbind(x.variables[,c(1,4,10,15)])
hier.part(y.variable,mod4.10)
mod4.11 = cbind(x.variables[,c(1,9,11,14)])
hier.part(y.variable,mod4.11)
mod4.12 = cbind(x.variables[,c(5,9,10,14)])
hier.part(y.variable,mod4.12)
mod4.13 = cbind(x.variables[,c(1,5,11,15)])
hier.part(y.variable,mod4.13)
mod4.14 = cbind(x.variables[,c(1,4,9,15)])
hier.part(y.variable,mod4.14)
mod4.15 = cbind(x.variables[,c(1,4,10,17)])
hier.part(y.variable,mod4.15)
mod4.16 = cbind(x.variables[,c(2,5,10,14)])
hier.part(y.variable,mod4.16)
mod4.17 = cbind(x.variables[,c(1,9,10,15)])
hier.part(y.variable,mod4.17)
mod4.18 = cbind(x.variables[,c(1,11,12,17)])
hier.part(y.variable,mod4.18)
mod4.19 = cbind(x.variables[,c(1,5,9,10)])
hier.part(y.variable,mod4.19)
mod4.20 = cbind(x.variables[,c(1,9,11,12)])
hier.part(y.variable,mod4.20)
mod5.1 = cbind(x.variables[,c(5,9,10,14,15)])
hier.part(y.variable,mod5.1)
mod5.2 = cbind(x.variables[,c(1,9,11,14,15)])
hier.part(y.variable,mod5.2)
mod5.3 = cbind(x.variables[,c(2,5,10,14,15)])
hier.part(y.variable,mod5.3)
mod5.4 = cbind(x.variables[,c(1,5,9,10,15)])
hier.part(y.variable,mod5.4)
mod5.5 = cbind(x.variables[,c(5,10,14,15,18)])
hier.part(y.variable,mod5.5)
mod5.6 = cbind(x.variables[,c(5,9,11,14,15)])
hier.part(y.variable,mod5.6)
mod5.7 = cbind(x.variables[,c(1,5,9,11,15)])
hier.part(y.variable,mod5.7)
mod5.8 = cbind(x.variables[,c(1,4,9,10,15)])
hier.part(y.variable,mod5.8)
mod5.9 = cbind(x.variables[,c(1,5,10,14,15)])
hier.part(y.variable,mod5.9)
mod5.10 = cbind(x.variables[,c(1,5,10,15,18)])
hier.part(y.variable,mod5.10)
mod5.11 = cbind(x.variables[,c(1,9,11,15,17)])
hier.part(y.variable,mod5.11)
mod5.12 = cbind(x.variables[,c(4,5,10,14,15)])
hier.part(y.variable,mod5.12)
mod5.13 = cbind(x.variables[,c(1,9,11,13,17)])
hier.part(y.variable,mod5.13)
mod5.14 = cbind(x.variables[,c(1,5,11,14,15)])
hier.part(y.variable,mod5.14)
mod5.15 = cbind(x.variables[,c(1,4,10,15,17)])
hier.part(y.variable,mod5.15)
mod5.16 = cbind(x.variables[,c(1,4,9,11,15)])
hier.part(y.variable,mod5.16)
mod5.17 = cbind(x.variables[,c(1,9,11,12,17)])
hier.part(y.variable,mod5.17)
mod5.18 = cbind(x.variables[,c(1,4,6,10,15)])
hier.part(y.variable,mod5.18)
mod5.19 = cbind(x.variables[,c(5,10,14,15,16)])
hier.part(y.variable,mod5.19)
mod5.20 = cbind(x.variables[,c(1,9,11,15,18)])
hier.part(y.variable,mod5.20)
mod6.1 = cbind(x.variables[,c(1,5,9,10,14,15)])
hier.part(y.variable,mod6.1)
mod6.2 = cbind(x.variables[,c(2,5,9,10,14,15)])
hier.part(y.variable,mod6.2)
mod6.3 = cbind(x.variables[,c(1,5,9,11,14,15)])
hier.part(y.variable,mod6.3)
mod6.4 = cbind(x.variables[,c(5,9,10,14,15,18)])
hier.part(y.variable,mod6.4)
mod6.5 = cbind(x.variables[,c(5,9,10,14,15,16)])
hier.part(y.variable,mod6.5)
mod6.6 = cbind(x.variables[,c(5,7,9,10,14,15)])
hier.part(y.variable,mod6.6)
mod6.7 = cbind(x.variables[,c(1,9,11,14,15,16)])
hier.part(y.variable,mod6.7)
mod6.8 = cbind(x.variables[,c(5,9,10,14,15,17)])
hier.part(y.variable,mod6.8)
mod6.9 = cbind(x.variables[,c(3,5,9,10,14,15)])
hier.part(y.variable,mod6.9)
mod6.10 = cbind(x.variables[,c(2,5,10,14,15,18)])
hier.part(y.variable,mod6.10)
mod6.11 = cbind(x.variables[,c(1,9,11,14,15,17)])
hier.part(y.variable,mod6.11)
mod6.12 = cbind(x.variables[,c(2,5,10,12,14,15)])
hier.part(y.variable,mod6.12)
mod6.13 = cbind(x.variables[,c(4,5,9,10,14,15)])
hier.part(y.variable,mod6.13)
mod6.14 = cbind(x.variables[,c(5,8,9,10,14,15)])
hier.part(y.variable,mod6.14)
mod6.15 = cbind(x.variables[,c(1,3,9,11,14,15)])
hier.part(y.variable,mod6.15)
mod6.16 = cbind(x.variables[,c(1,4,9,10,15,17)])
hier.part(y.variable,mod6.16)
mod6.17 = cbind(x.variables[,c(5,6,9,10,14,15)])
hier.part(y.variable,mod6.17)
mod6.18 = cbind(x.variables[,c(5,9,10,12,14,15)])
hier.part(y.variable,mod6.1)
hier.part(y.variable,mod6.18)
mod6.19 = cbind(x.variables[,c(1,5,9,10,15,18)])
hier.part(y.variable,mod6.19)
mod6.20 = cbind(x.variables[,c(5,9,10,11,14,15)])
hier.part(y.variable,mod6.20)
