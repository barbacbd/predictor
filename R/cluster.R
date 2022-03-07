#!/usr/bin/env Rscript

# install and load missing packages
install.packages("librarian", repos="http://cran.us.r-project.org", quiet=TRUE)

librarian::shelf(clusterCrit, docopt, Ckmeans.1d.dp, discretization, quiet=TRUE)

doc <- '
Usage:
  cluster.R [-h | --help]
  cluster.R [-k=<clusters> (--cols | --rows) -n=<num> -o=<outfile>] [(-h | --help) | <file>]


Options:
  -k<clusters> --clusters=<clusters> Number of k-means clusters [default: 1]
  -n=<num> --num=<num>               Number of Rows or Columns based on type [default: 1]
  -o=<outfile> --output=<outfile>    CSV File to output to [default: output.csv]
  --cols                             Use data as columns
  --rows                             Use data as rows.
  --help                             Dsiplay help information

Arguments:
  file	Space delimited file containing all data points
'

opt <- docopt(doc)

# Graceful fail when the file does not exist
if (!file.exists(opt$file)) {
  stop("File does not exist. Please provide path/to/file.file_extension")
}

# read in the data and convert it to a vector.
data <- scan(opt$file, sep="", skipNul=TRUE)
#data <- table.read(opt$file, sep="", header=FALSE, skipNul=TRUE)
print(data)

# convert the DataFrame to a vector with the transpose of the DataFrame
fileLoadedDataSet <- as.vector(t(data))

# clusterCrit wants the trajectory as a matrix of numerics. Force
# the values to be numerics here in the event that integers were passed
if (opt$cols) {
  fileLoadedMatrix <- matrix(
    as.numeric(fileLoadedDataSet),
    # set the data as columns
    ncol=as.integer(opt$num)
  )
} else {
  fileLoadedMatrix <- matrix(
    as.numeric(fileLoadedDataSet),
    # set the data as rows
    nrow=as.integer(opt$num)
  )
}

# $cluster: Cluster of each observation
# $centers: Cluster centers
# $totss: Total sum of squares
# $withinss: Within sum of square. The number of components return is equal to `k`
# $tot.withinss: sum of withinss
# $betweenss: total sum of square minus within sum of square
# $size: number of observation within each cluster
#kmeansOutput <- kmeans(fileLoadedDataSet, opt$clusters)

ckmeansOutput <- MultiChannel.WUC(
    x=fileLoadedMatrix, 
    matrix(1, nrow=nrow(fileLoadedMatrix), ncol=1), 
    k=c(as.integer(2:50))
)

print(ckmeansOutput)
ccData <- clusterCrit::intCriteria(fileLoadedMatrix, ckmeansOutput$cluster, "all")
#ccData <- clusterCrit::intCriteria(fileLoadedMatrix, kmeansOutput$cluster, "all")

# covert the list from above to a matrix, give the matrix the row values
# corresponding to the algorithm that was run
ccMatrix <- matrix(ccData, ncol=1)
rownames(ccMatrix)<-(clusterCrit::getCriteriaNames(TRUE))

# write the data to the file of choice. Should be a CSV file
# write.table(ccMatrix, file=opt$output, sep=",", row.names=TRUE, col.names=FALSE)
cacc_output <- discretization::cacc(ccMatrix)
print(cacc_output)
