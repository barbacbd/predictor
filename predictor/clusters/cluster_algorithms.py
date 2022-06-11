from copy import copy
from enum import Enum
import jenkspy
from kmeans1d import cluster as kmeans1dc
from math import ceil
from numpy import loadtxt, asarray, apply_along_axis, argsort, argsort, zeros, std, linspace, less, greater
import pandas as pd
from scipy.signal import argrelextrema
from sklearn.cluster import k_means
from sklearn.neighbors import KernelDensity


def k_means_wrapper(data_set, k, *args, **kwargs):
    '''The function will call the kmeans algorithm for data where the 
    dimensions are greater than 1, while the kmeans1d algorithm will be
    used for 1-dimensional data. While kmeans can be applied to data of
    any number of dimensions, 1-D data is a special case and should be handled
    appropriately.

    :param data_set: numpy array
    :param k: number of clusters
    
    Keyword Arguments:

    :param init: Applies ONLY to data that has more than one dimension. The 
    `init` should be used to pass the data kmeans. 
    '''

    rows, cols = data_set.shape

    if cols == 1:
        matching_clusters, centroids = kmeans1dc(data_set, k)
    else:
        centroids, matching_clusters, weighted_sum_to_centroids = k_means(
            data_set, k, init=kwargs.get('init', 'k-means++')
        )

    # update the array values, in R the indicies started with 1 not 0
    matching_clusters = asarray(matching_clusters) + 1

    # format the data as a list, this is expected by R
    matching_clusters = matching_clusters.tolist()
    return matching_clusters


def x_bins(data_set, k, *args, **kwargs):
    '''Create K number of even width'd bins. Find the max
    and min values in the dataset. Divide the space between
    max and min into k bins.

    :param data_set: numpy array
    :param k: Number of bins or clusters

    :return: cluster numbers in order for the original dataset
    '''
    mn = data_set.min()
    diff = data_set.max() - mn
    bin_range = diff / k

    bins = [(mn+(bin_range*i), mn+(bin_range*(i+1))) for i in range(k+1)]

    def _find_bin(row):
        """
        :param row: Dataframe row
        """
        for i, bin in enumerate(bins):
            if bin[0] <= row[0] < bin[1]:
                return i + 1 
    
    clusters = apply_along_axis(_find_bin, 1, data_set)
    clusters = clusters.tolist()
    return clusters


def e_bins(data_set, k, *args, **kwargs):
    '''Even numbers per k bins. This is more of a grouping than anything. Separate the
    data into k number of bins where each bin has the same or close to the same number
    of entries.
    
    :param data_set: numpy array
    :param k: number of clusters
    '''
    data_set_copy = copy(data_set)
    
    rows, cols = data_set.shape

    # this may not be the EXACT number per bin as duplicates must be 
    # moved to the same bin to avoid an error where the bin limits 
    # are the same value
    out = pd.qcut(data_set[:,0], q=k, labels=False)
    out += 1  # expects 1 - k, not 0 - k-1
    return out.tolist()


def natural_breaks(data_set, k, *args, **kwargs):
    '''Implementation of the natural breaks or jenks_breaks algorithm
    on the 1-Dimensional dataset. The algorithm will attempt to 
    find the natural break points in the dataset. 

    Sort the dataset (which keeps the original index values) and apply
    the function to the sorted data. 

    :param data_set: Numpy array 
    :param k: number of clusters

    :return: `clusters` or groups of data 
    '''
    df = pd.DataFrame(data_set, columns=["Data Points"])
    df.sort_values(by='Data Points')
    df['bin'] = pd.cut(
        df['Data Points'], 
        bins=jenkspy.jenks_breaks(df['Data Points'], nb_class=k),
        labels=[x for x in range(1, k+1)],
        include_lowest=True
        )
    return df['bin'].to_list()
    

def kde(data_set, k, *args, **kwargs):
    '''Kernel Density Estimation 

    Algorithm that is considered a great metric for 1-Dimensional
    `clustering`. 
    '''
    raise NotImplementedError("KDE")  
    data_std = std(data_set)

    # For gaussian `default`, The formula
    # 1.06n(theta)^(-1/5) was selected
    bw = 1.06*data_std*data_set.size**(-1.0/5.0)
    _kde = KernelDensity(kernel='gaussian', bandwidth=bw).fit(data_set)
    
    # apply the dataset to a linearspace
    s = linspace(0, 50)
    e = _kde.score_samples(s.reshape(-1,1))
    mi, ma = argrelextrema(e, less)[0], argrelextrema(e, greater)[0]
    
    # clusters should be found using mi and ma


class ClusterAlgorithm(Enum):
    ALL = 0
    K_MEANS = 1
    X_BINS = 2
    E_BINS = 3
    NATURAL_BREAKS = 4
    KDE = 5

    @classmethod
    def list_functions(cls, algorithm):
        '''Get the function that implements the algorithm associated with 
        the enumeration type.

        :return: list of functions
        '''
        funcs = []

        func_dict = {
            cls.K_MEANS: k_means_wrapper,
            cls.X_BINS: x_bins,
            cls.E_BINS: e_bins,
            cls.NATURAL_BREAKS: natural_breaks,
            cls.KDE: kde
        }
        
        if algorithm in cls:
            if algorithm == cls.ALL:
                return list(func_dict.values())
            else:
                funcs.append(func_dict.get(algorithm))
        return funcs
