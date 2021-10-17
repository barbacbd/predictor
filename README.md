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


## Metrics 
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


## Algorithms 


### Kmeans / Kmeans1D

### X (even spaced) Bins


### E (even) Bins


### Natural Breaks


### Kernel Density Estimation


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
