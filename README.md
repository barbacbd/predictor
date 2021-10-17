# Cluster ![build workflow](https://github.com/barbacbd/cluster/actions/workflows/python-app.yml/badge.svg) ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![R-Language](https://img.shields.io/badge/R-276DC3?style=for-the-badge&logo=r&logoColor=white)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/barbacbd/cluster/pulse/commit-activity)
[![GitHub latest commit](https://badgen.net/github/last-commit/barbacbd/cluster)](https://github.com/barbacbd/cluster/commit/)
[![PyPi license](https://badgen.net/pypi/license/pip/)](https://pypi.com/project/pip/)

[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![macOS](https://svgshare.com/i/ZjP.svg)](https://svgshare.com/i/ZjP.svg)
<!-- Not sure if this works on windows currently
[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)
-->

## Description

The package is intended to be used as a clustering aid to datasets while providing a wrapper to the [cluster crit](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/viewer.html?pdfurl=https%3A%2F%2Fcran.r-project.org%2Fweb%2Fpackages%2FclusterCrit%2FclusterCrit.pdf&clen=129366&chunk=true) package from `R`.

## Cluster Script (python)

```bash
usage: cluster [-h] [--file FILE] [-k CLUSTERS [CLUSTERS ...]] [-c {all,k_means,x_bins,e_bins,natural_breaks,kde}] [--init {k-means++,random}]

Read in files containing data points and execute a set of metrics on the dataset.

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           File that will be read in, and a dataset will be made out of the data.
                        The data should NOT include headers for rows or columns.
  -k CLUSTERS [CLUSTERS ...], --clusters CLUSTERS [CLUSTERS ...]
                        List of the number of clusters. The first index in the list is the lower 
                        limit number of clusters, while the second is upper limit. For instance: --clusters 3 10 would run the
                        algorithm on all clusters in the range of 3 to 10. <1 will be ignored and lists of length 0 are ignored, 
                        lists of length 1indicates that the upper and lower limit are the same.
  -c {all,k_means,x_bins,e_bins,natural_breaks,kde}, --clustering {all,k_means,x_bins,e_bins,natural_breaks,kde}
                        k_means: normal k_means clustering algorithm.x_bins: use K to create the number of bins spread out 
                        from max to min.e_bins: even number per bin or cluster.all: run all algorithms
  --init {k-means++,random}
                        When present, this option inidcates the use of kmeans vs kmeans++ (default).
```
The script can be run with `cluster` and it is installed to the version of python that was used for
installation. The user will provide a datafile and run it through the cluster crit algorithms.

## Cluster Script (R)

```bash
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
```

The script is run with `rscript cluster.R`. The script will allow the user to provide a file of datapoints
and run the data through the cluster Crit package. The script is also contained within the python code.



## Metrics 

The metrics were all taken from the [cluster crit](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/viewer.html?pdfurl=https%3A%2F%2Fcran.r-project.org%2Fweb%2Fpackages%2FclusterCrit%2FclusterCrit.pdf&clen=129366&chunk=true) package in `R` found [here](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/viewer.html?pdfurl=https%3A%2F%2Fcran.r-project.org%2Fweb%2Fpackages%2FclusterCrit%2FclusterCrit.pdf&clen=129366&chunk=true).

| Cluster Crit Metric | Criteria to determine optimal cluster |
| ------------------- | ------------------------------------- |
| Ball_Hall | max diff |
| Banfeld_Raftery | min |
| C_index | min |
| Calinski_Harabasz | max |
| Davies_Bouldin | min |
| Det_Ratio | min diff |
| Dunn | max |
| Gamma | max |
| G_plus | min |
| Ksq_DetW | max diff |
| Log_Det_Ratio | min diff |
| Log_SS_Ratio | min diff |
| McClain_Rao | min |
| PBM | max |
| Ratkowsky_Lance | max |
| Ray_Turi | min |
| Scott_Symons | min |
| S_Dbw | min |
| Silhouette | max |
| Tau | max |
| Trace_W | max diff |
| Trace_WiB | max diff |
| Wemmert_Gancarski | max |
| Xie_Beni | min |

### Min
Find the minimum value in the entire row 

### Max
Find the maximum value in the entire row

### Min Diff
For each value in the row (except the first), calculate the difference between index n and index n-1. The minimum
value of the differences is the result.

### Max Diff
For each value in the row (except the first), calculate the difference between index n and index n-1. The maximum
value of the differences is the result.


### What does this all mean?

Following the conclusion of each algorithm above run over the dataset for each number of clusters `k`, the second column (function) is applied
to each row. Let's use `Ball_Hall` as an example. 

Metric=`Ball_Hall`
K=`2 to 50`
Clustering=`kmeans`

|    | k=2 | k=3 | k=4 | k=5 | k=6 | ... |
| -- | --- | --- | --- | --- | --- | --- |
| Ball Hall | 0.2342 | 1.23423 | 0.8924 | 1.20312 | 2.231 | ... |

The user supplies a matrix of values, and `kmeans` is run on the dataset for each value of `k` (2 to 50). A dataframe is generated where the row corresponds to the metric and each value in the row is the result of executing that metric on each value of `k`. In this example for `Ball_Hall` the `mas diff` for values of the row are calculated and the result is the value of `k` that best fit that metric.  In the table above (looking at only the values provided), when `k` is 6 the max diff is observed.

## Algorithms 

The following section describes the algroithms that can be selected for clustering. The default algorithm is `kmeans`. 

### Kmeans / Kmeans1D
The [kmeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html) algorithm is applied to multidimensional datasets. When a 1-dimensional dataset has been provided [kmeans1d](https://pypi.org/project/kmeans1d/) is selected. Generally, kmeans is sufficient for clustering because it is an unsupervised form of clustering. Kmeans is _not_ perfect, so the option is also provided to the user to enhance the algorithm a bit more through the `init` parameter. The parameter will ensure that [kmeans++](https://en.wikipedia.org/wiki/K-means%2B%2B) is utilized instead of kmeans. 

### X (even spaced) Bins
Evenly dispersed bins aims to solve a problem has is present with kmeans, singletons. Kmeans (the multidimensional algorithm) does not handle outliers in a single dimension. These singletons that are the result of small cluster sizes cause issues with the metrics (above). Evenly spaced bins are generated by taking the `min` and `max` of the entire dataset and creating equal width `k` bins where `k` is the number of clusters. 

That is correct, this will also not solve the singleton problem, moving on!

### E (even) Bins

Even bins attempts to place the same number of entries in all bins. This isn't clustering, it's more along the lines of forced clustering. The algorithm is left
in the project, but not used as it is not finding natural breaks (see below) or creating realistic clusters.

### Natural Breaks

The algorithm is specifically called out to aid in clustering 1-dimensional datasets and it can be found [here](https://github.com/mthh/jenkspy). 

### Kernel Density Estimation

_NOTE: not currently implemented and tested._

Kernel Density Estimation (_KDE_) is a Gaussian Mixture Model (_GMM_) that attempts to take your data and fit it against a gaussian model. KDE is called out as an exceptional aid in clustering 1-dimensional datasets. 

