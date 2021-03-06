# Algorithms 

The following document describes the algroithms that can be selected for clustering. All listed algorithms are available during configuration. The default algorithm is `kmeans`. 


## Kmeans / Kmeans1D

The [kmeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html) algorithm is applied to multidimensional datasets. When a 1-dimensional dataset has been provided [kmeans1d](https://pypi.org/project/kmeans1d/) is selected. Generally, kmeans is sufficient for clustering because it is an unsupervised form of clustering. Kmeans is _not_ perfect, so the option is also provided to the user to enhance the algorithm a bit more through the `init` parameter. The parameter will ensure that [kmeans++](https://en.wikipedia.org/wiki/K-means%2B%2B) is utilized instead of kmeans. 


## X (even spaced) Bins

Evenly dispersed bins aims to solve a problem has is present with kmeans, singletons. Kmeans (the multidimensional algorithm) does not handle outliers in a single dimension. These singletons that are the result of small cluster sizes cause issues with the metrics (above). Evenly spaced bins are generated by taking the `min` and `max` of the entire dataset and creating equal width `k` bins where `k` is the number of clusters. 

That is correct, this will also not solve the singleton problem, moving on!

## E (even) Bins

Even bins attempts to place the same number of entries in all bins. This isn't clustering, it's more along the lines of forced clustering. The algorithm is left
in the project, but not used as it is not finding natural breaks (see below) or creating realistic clusters.

## Natural Breaks

The algorithm is specifically called out to aid in clustering 1-dimensional datasets and it can be found [here](https://github.com/mthh/jenkspy). 


## Kernel Density Estimation

**Note**: _Selection not currently implemented and tested._

Kernel Density Estimation (_KDE_) is a Gaussian Mixture Model (_GMM_) that attempts to take your data and fit it against a gaussian model. KDE is called out as an exceptional aid in clustering 1-dimensional datasets. 

