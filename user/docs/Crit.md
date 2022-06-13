# Crit

The following metrics were all taken from the [cluster crit](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/viewer.html?pdfurl=https%3A%2F%2Fcran.r-project.org%2Fweb%2Fpackages%2FclusterCrit%2FclusterCrit.pdf&clen=129366&chunk=true) package in `R` found [here](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/viewer.html?pdfurl=https%3A%2F%2Fcran.r-project.org%2Fweb%2Fpackages%2FclusterCrit%2FclusterCrit.pdf&clen=129366&chunk=true). To view more information about these algorithms see the [cluster crit documentation](./clusterCrit.pdf). 

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

## Min
Find the minimum value in the entire row 

## Max
Find the maximum value in the entire row

## Min Diff
For each value in the row (except the first), calculate the difference between index n and index n-1. The minimum
value of the differences is the result.

## Max Diff
For each value in the row (except the first), calculate the difference between index n and index n-1. The maximum
value of the differences is the result.


# What does this all mean?

The user will select one or more algorithms above using the configuration. Each algorithm will be run on all 2 through `k` clusters. The second column above is the function that will be applied to the output when all clusters are created. To demonstrate, examine the example below. Take the following configuration variables 

- Metric = `Ball_Hall`
- K = `2-50`
- Clustering = `kmeans`

|    | k=2 | k=3 | k=4 | k=5 | k=6 | ... |
| -- | --- | --- | --- | --- | --- | --- |
| Ball Hall | 0.2342 | 1.23423 | 0.8924 | 1.20312 | 2.231 | ... |

The user supplies a file containing all values, and `kmeans` is run on the dataset for each value of `k` (2 to 50). A pandas dataframe is generated where the row corresponds to the metric and each value in the row is the result of executing that metric on each value of `k`. In this example for `Ball_Hall` the `max diff` for values of the row are calculated and the result is the value of `k` that best fit that metric.  In the table above (looking at only the values provided), when `k` is 6 the max diff is observed.

