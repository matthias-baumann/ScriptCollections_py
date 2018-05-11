#' Confusion matrix
#'
#' @title aa_confusion_matrix
#' @description Calculates confusion matrix adjusted for selection probabilities
#' @param ref reference sample vector
#' @param map map sample vector
#' @param prob selection probabilties
#' @return confusion matrix
#' @author Dirk Pflugmacher
#' 

aa_confusion_matrix <- function(ref, map, prob=NULL) {
  
  classes = unique(c(ref,map))
  classes = sort(classes)
  
  if (is.null(prob)) prob <- rep(1, length(ref))
  
  cm = matrix(data=0, nrow=max(classes), ncol=max(classes))
  
#  for (i in 1:length(ref)) {
#    cm[map[i],ref[i]] <- cm[map[i],ref[i]] + prob[i]
#s  }
  
  for (i in 1:length(classes)) {
    for (j in 1:length(classes)) {
      k = which(ref == classes[i] & map == classes[j])
      if (length(k) > 0) cm[j,i] <- cm[j,i] + sum(prob[k])
    }
    
  }
  
  tt <- apply(cm,1,sum) + apply(cm,2,sum)
  i  <- which(tt==0)
  if (length(i)>0)
    cm <- cm[-i,-i]
  
  row.names(cm) <- classes
  colnames(cm) <- classes
  
  return(cm)
  
}