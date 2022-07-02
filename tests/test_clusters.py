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
from predictor.clusters.r import crit, CritSelection
from predictor.clusters.artifacts import ClusterArtifact
import pytest
import numpy as np



def create_1d_dataset():
    '''Create the 1-Dimensional Dataset for the 
    use of unit tests'''
    data = [float(x+1) for x in range(12)]
    return np.array(data)


def create_dataset():
    '''Create the n-dimensional dataset for the
    use of unit tests
    '''
    data = [float(x+1) for x in range(12)]
    data = [data, data]
    return np.array(data)


def test_kmeans_normal():
    '''Test a simple/normal k-means execution'''
    k = 3
    dataset = create_dataset()
    clusters = k_means_wrapper(dataset, k, init='random')
    assert len(set(clusters)) == k
    

def test_kmeanspp():
    '''Test a simple kmeans ++ example'''
    k = 3
    dataset = create_dataset()
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
    dataset = create_1d_dataset()
    clusters = x_bins(dataset, k)
    
    assert len(set(clusters)) == k


def test_e_bins():
    '''Test an example of splitting the dataset where the
    amount per bin are even (or roughly even).
    '''
    k = 3
    dataset = create_1d_dataset()
    clusters = x_bins(dataset, k)
    
    assert len(set(clusters)) == k
    
    # find the number of entries per cluster


def test_natural_breaks():
    '''Test splitting the data by natural break points in the 
    dataset. This is an extension of the natural breaks of jenkspy
    '''

    
def test_kde():
    '''Test a Kernel Density Estimation Example

    -- Currently unavailable
    '''
    with pytest.raises(NotImplementedError):
        dataset = create_1d_dataset()
        output = kde(dataset, 2)


def test_check_for_singletons_found():
    '''Test finding singletons'''


def test_check_for_singletons_not_found():
    '''Test finding singletons none fond'''


def df_min_diff_single():
    '''Find the min diff between values in the Dataframe
    with only one correct value'''
    
    
def df_min_diff_multiple():
    '''Find the min diff between values in the Dataframe
    with multiple correct values, but first is selected
    '''

    
def df_max_diff_single():
    '''Find the max diff between values in the Dataframe
    with only one correct value'''
    
    
def df_max_diff_multiple():
    '''Find the max diff between values in the Dataframe
    with multiple correct values, but first is selected
    '''
    
    
def df_min_single():
    '''Find the min between values in the Dataframe
    with only one correct value'''
    
    
def df_min_multiple():
    '''Find the min between values in the Dataframe
    with multiple correct values, but first is selected
    '''

    
def df_max_single():
    '''Find the max between values in the Dataframe
    with only one correct value'''
    
    
def df_max_multiple():
    '''Find the max between values in the Dataframe
    with multiple correct values, but first is selected
    '''


def test_select_valid_rows():
    '''Test selection and ensure that values are correctly
    found/selected from the valid rows'''
    
    
def test_select_invalid_rows():
    '''Test selection and ensure that no values are selected
    due to invlaid row names
    '''


def test_crit_invalid_option():
    '''Test the CRIT algorithms from R with an invalid algorithm'''
    

def test_crit_valid_single_option():
    '''Test the CRIT algorithms from R with a valid single algorithm'''
    

def test_crit_valid_multiple_options():
    '''Test the CRIT algorithms from R with valid algorithms'''
    
    
def test_valid_cluster_artifacts():
    '''Create and read a cluster artifact file setting the object
    and verify that the data was correctly created'''


def test_invalid_cluster_artifacts():
    '''Create and read a cluster artifact file that is invalid'''

