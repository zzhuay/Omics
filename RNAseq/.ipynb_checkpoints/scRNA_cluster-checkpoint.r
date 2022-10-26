library(ggplot2)
library(preprocessCore)
library(ConsensusClusterPlus)
library(parallelDist)

setwd('~/Documents/Research/scRNA/')

mgdata <- read.csv('./single_cell_expression.txt',sep='\t')

# Z score transformation for each gene
cellid <- colnames(mgdata)
mgdata <- apply(mgdata, 1, scale)
mgdata <- t(mgdata)
colnames(mgdata) <- cellid


title="single cell clustering"
hcResults <- ConsensusClusterPlus(as.matrix(mgdata), maxK=10, reps=100, pItem=0.8, pFeature= 1,
                                title=title, clusterAlg="hc", distance="euclidean", innerLinkage = "ward.D", 
                                finalLinkage = "ward.D", seed=1, plot="png")

coph = c()
for(i in c(2:10)){
  d <- parallelDist(1-hcResults[[i]][["consensusMatrix"]]) # distance d in consensus matrix
  hc2 <- hclust(d, "complete")
  d2 <- cophenetic(hc2) # distance d2 in clustering of consensus matrix
  coph <- append(coph,cor(d, d2))
  print(coph)
}

# save results and visualization
write.csv(coph, 'ward.complete.coph.csv')
pdf("ward.complete.coph.pdf")
plot(c(2:10),coph)
dev.off()