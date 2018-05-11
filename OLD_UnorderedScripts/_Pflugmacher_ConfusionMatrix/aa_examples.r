#' Accuracy Assessment Examples
#'
#' @title aa_examples
#' @description Accuracy Assessment Examples
#' @param source_name source_name
#' @return dataset
#' @author Dirk Pflugmacher
#' 

aa_examples <- function(source_name) {
  
  if (source_name=='card') {
    m <- t(matrix(c(48,1,1,0,0,0,49,0,1,0,2,0,47,1,0,5,4,3,34,4,0,0,3,12,35), nrow=5))
    w_i <- c(0.4,0.4,0.12,0.04,0.04)
    citation = 'Card, D.H. (1982). Using Known Map Category Marginal Frequencies to Improve Estimates of Thematic Map Accuracy. Photogrammetric Engineering and Remote Sensing, 48, 431-439'
    return(list(m=m,w_i=w_i,citation=citation))
  }

  if (source_name=='congalton') {
    n <- c(65,6,0,4,4,81,11,7,22,5,85,3,24,8,19,90)
    n <- matrix(n, nrow=4)
    p <- c(0.170,0.024,0,0.008,0.101,0.324,0.010,0.013,0.057,0.020,0.074,0.006,0.063,0.032,0.017,0.0173)
    p <- matrix(p, nrow=4)
    w_i <- c(0.3, 0.4, 0.1, 0.2)
    citation = 'Congalton, R. (2009). Assessing the Accuracy of Remotely Sensed Data: Principles and Practices. Page 117'
    return(list(m=m,w_i=w_i, citation=citation))
  }

  if (source_name=='stehman') {
    m <- matrix(c(410,67,26,369), nrow=2)
    A <- c(828837,33067283)
    w_i <- A/sum(A)
    citation = ''
    return(list(m=m,w_i=w_i,A=A,citation=citation))
  }
  
# Olofsson
if (source_name=='olofsson') {
    m <- matrix(c(97,3,2,0,279,1,3,18,97), nrow=3)
    A <- c(22353,1122543,610228)
    w_i <- A/sum(A)
    citation = 'Olofsson, P., Foody, G.M., Stehman, S.V., & Woodcock, C.E. (2013). Making better use of accuracy data in land change studies: Estimating accuracy and area and quantifying uncertainty using stratified estimation. Remote Sensing of Environment, 129, 122-131'
    return(list(m=m,w_i=w_i,A=A,citation=citation))
    }
}