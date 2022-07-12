from tabnanny import check
from xmlrpc.client import MAXINT, MININT
from predictor.clusters.cluster_algorithms import (
    k_means_wrapper,
    x_bins,
    e_bins,
    natural_breaks,
    kde,
    ClusterAlgorithm
)
from predictor.clusters.selection import (
    check_for_singletons,
    df_min_diff,
    df_max_diff,
    df_min,
    df_max,
    select
)
from predictor.clusters.r import crit, CritSelection, init
from predictor.clusters.artifacts import ClusterArtifact
import pytest
import numpy as np
import pandas as pd
from random import random, shuffle
from math import fabs


def create_1d_dataset(col=12):
    '''Create the 1-Dimensional Dataset for the 
    use of unit tests'''
    data = [random() for x in range(col)]
    return np.array(data).reshape(-1, 1)


def create_dataset(row=3, col=12):
    '''Create the n-dimensional dataset for the
    use of unit tests
    '''
    dataset = []
    for xdata in range(row):
        dataset.append([random() for _ in range(col)])
    return np.array(dataset)


'''Note: Kmeans whether it is a single or multidimensional
problem is a wrapper arounds the Kmeans algorithm. Thus, the
Kmeans function will not be tested to verify the results.
'''

def test_kmeans_normal():
    '''Test a simple/normal k-means execution'''
    k = 3
    dataset = create_dataset()
    clusters = k_means_wrapper(dataset, k, init='random')
    assert len(set(clusters)) == k
    

def test_kmeanspp():
    '''Test a simple kmeans ++ example'''
    k = 5
    dataset = create_dataset(row=k, col=14)
    clusters = k_means_wrapper(dataset, k, init='k-means++')
    assert len(set(clusters)) == k


def test_kmeans_1d():
    '''Test a 1-Dimensional example of kmeans'''
    k = 3
    dataset = create_1d_dataset()
    clusters = k_means_wrapper(dataset, k)
    assert len(set(clusters)) == k


def test_x_bins():
    '''Test an example of splitting the dataset into k bins
    of even width based on the extent of the dataset
    '''
    k = 3
    dataset = create_1d_dataset(30)
    clusters = x_bins(dataset, k)
    assert len(set(clusters)) == k


def test_e_bins():
    '''Test an example of splitting the dataset where the
    amount per bin are even (or roughly even).
    '''
    k = 5
    dataset = create_1d_dataset(30)
    clusters = e_bins(dataset, k)
    
    assert len(set(clusters)) == k
    
    # find the number of entries per cluster
    cluster_lens = []    
    for cluster in set(clusters):
        cluster_lens.append(clusters.count(cluster))

    diff = max(cluster_lens) - min(cluster_lens) 
    assert 1.0 >= diff >= -1.0


def test_natural_breaks():
    '''Test splitting the data by natural break points in the 
    dataset. This is an extension of the natural breaks of jenkspy
    '''
    k = 3
    dataset = create_1d_dataset()
    clusters = natural_breaks(dataset, k)
    
    assert len(set(clusters)) == k

    
def test_kde():
    '''Test a Kernel Density Estimation Example

    -- Currently unavailable
    '''
    with pytest.raises(NotImplementedError):
        dataset = create_1d_dataset()
        output = kde(dataset, 2)


def test_check_for_singletons_found():
    '''Test finding singletons'''
    max_k = 20
    
    dataset = {}
    for k in range(2, max_k):
        dataset[str(k)] = k_means_wrapper(create_1d_dataset(30), k)
    df = pd.DataFrame.from_dict(dataset, orient='index')
    df = df.transpose()
    
    assert True in list(check_for_singletons(df).values())
    

def test_check_for_singletons_not_found():
    '''Test finding singletons none fond'''
    max_k = 4
    
    dataset = {}
    for k in range(2, max_k):
        dataset[str(k)] = k_means_wrapper(create_1d_dataset(30), k)
    df = pd.DataFrame.from_dict(dataset, orient='index')
    df = df.transpose()
    
    assert True not in list(check_for_singletons(df).values())


def test_df_min_diff():
    '''Find the min diff between values in the Dataframe
    with multiple correct values, but first is selected
    '''    
    # start is also the min
    start = 10
    data = [x for x in range(start, start+10)]
    shuffle(data)
    
    local_idx = 1
    local_min = MAXINT
    for i in range(1, len(data)):
        if fabs(data[i] - data[i-1]) < local_min:
            local_min = fabs(data[i] - data[i-1])
            local_idx = i

    row_data = {"1": data}
    df = pd.DataFrame.from_dict(row_data, orient='index')
    
    output = []
    for idx, row in df.iterrows():
        output.append(df_min_diff(row))
    
    assert local_idx == output[0]
    
    
def test_df_max_diff():
    '''Find the max diff between values in the Dataframe
    with multiple correct values, but first is selected
    '''
    # start is also the min
    start = 10
    data = [x for x in range(start, start+10)]
    shuffle(data)
    
    local_idx = 1
    local_max = MININT
    for i in range(1, len(data)):
        if fabs(data[i] - data[i-1]) > local_max:
            local_max = fabs(data[i] - data[i-1])
            local_idx = i

    row_data = {"1": data}
    df = pd.DataFrame.from_dict(row_data, orient='index')
    
    output = []
    for idx, row in df.iterrows():
        output.append(df_max_diff(row))
    
    assert local_idx == output[0]


def test_df_min():
    '''Find the min between values in the Dataframe
    with multiple correct values, but first is selected
    '''
    # start is also the min
    start = 10
    data = [x for x in range(start, start+10)]
    shuffle(data)
    
    local_idx = data.index(min(data))

    row_data = {"1": data}
    df = pd.DataFrame.from_dict(row_data, orient='index')
    
    output = []
    for idx, row in df.iterrows():
        output.append(df_min(row))
    
    assert local_idx == output[0]

    
def test_df_max():
    '''Find the max between values in the Dataframe
    with multiple correct values, but first is selected
    '''
    # start is also the min
    start = 10
    data = [x for x in range(start, start+10)]
    shuffle(data)
    
    local_idx = data.index(max(data))

    row_data = {"1": data}
    df = pd.DataFrame.from_dict(row_data, orient='index')
    
    output = []
    for idx, row in df.iterrows():
        output.append(df_max(row))

    assert local_idx == output[0]


def test_select_valid_rows():
    '''Test selection and ensure that values are correctly
    found/selected from the valid rows'''
    # start is also the min
    start = 10
    data = [x for x in range(start, start+10)]
    shuffle(data)
    
    local_idx = 1
    local_max = MININT
    for i in range(1, len(data)):
        if fabs(data[i] - data[i-1]) > local_max:
            local_max = fabs(data[i] - data[i-1])
            local_idx = i

    row_data = {"Ball_Hall": data}
    df = pd.DataFrame.from_dict(row_data, orient='index')
    selections = select(df)
    
    assert selections["Ball_Hall"] == local_idx
    

def test_select_invalid_rows():
    '''Test selection and ensure that no values are selected
    due to invlaid row names
    '''
    start = 10
    data = [x for x in range(start, start+10)]
    shuffle(data)
    
    row_data = {"Random": data}
    df = pd.DataFrame.from_dict(row_data, orient='index')
    selections = select(df)
    
    assert "Random" not in selections


def test_crit_invalid_option():
    '''Test the CRIT algorithms from R with an invalid algorithm'''
    k = 3
    dataset = create_1d_dataset()
    clusters = k_means_wrapper(dataset, k)
    output = crit(dataset, clusters, "bad data", k)
    assert output is None


def test_crit_valid_single_option():
    '''Test the CRIT algorithms from R with a valid single algorithm'''
    k = 3
    init()
    dataset = create_1d_dataset()
    clusters = k_means_wrapper(dataset, k)
    output = crit(dataset, clusters, [CritSelection.Ball_Hall], k)

    assert CritSelection.Ball_Hall.name in output.index.values
        

def test_crit_valid_multiple_options():
    '''Test the CRIT algorithms from R with valid algorithms'''
    k = 3
    init()
    dataset = create_1d_dataset()
    clusters = k_means_wrapper(dataset, k)
    output = crit(dataset, clusters, [
        CritSelection.Ball_Hall,
        CritSelection.Banfeld_Raftery], 
        k
    )

    assert CritSelection.Ball_Hall.name in output.index.values
    assert CritSelection.Banfeld_Raftery.name in output.index.values


def main():
    test_crit_valid_single_option()

if __name__ == '__main__':
    main()
