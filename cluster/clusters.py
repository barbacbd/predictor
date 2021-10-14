from numpy import loadtxt, asarray, apply_along_axis, argsort, argsort, zeros, std, linspace, less, greater
from sklearn.cluster import k_means
from copy import copy
from math import ceil
import pandas as pd
import jenkspy
from sklearn.neighbors import KernelDensity
from scipy.signal import argrelextrema


# The following functions can be passed to the class created above
# these functions should create bins and put the data points into bins
# or clusters. The bins or clusters should be returned as a list. 
# each data point in the list will be the bin number 1 to n in the SAME
# order as the original data set.
def k_means_wrapper(data_set, k, *args, **kwargs):
    """
    
    :param data_set:
    :param k:
    
    \keyword args\
    
    :param init:
    """
    centroids, matching_clusters, weighted_sum_to_centroids = k_means(
        data_set, k, init=kwargs.get('init', 'k-means++')
    )
    
    # update the array values, in R the indicies started with 1 not 0
    matching_clusters = asarray(matching_clusters) + 1

    # format the data as a list, this is expected by R
    matching_clusters = matching_clusters.tolist()
    return matching_clusters


def x_bins(data_set, k, *args, **kwargs):
    """
    :param data_set: Pandas dataframe 
    :param k: Number of bins or clusters
    """
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
    """
    Even numbers per k bins. This is more of a grouping than anything. Separate the
    data into k number of bins where each bin has the same or close to the same number
    of entries.
    
    :param data_set:
    :param k:
    """
    data_set_copy = copy(data_set)
    
    rows, cols = data_set.shape
    fl = zeros((rows, 1))

    per_bin = int(round(rows / k))
    extra = rows - (per_bin * k)

    if extra > 0:
        # start in the middle and add some to each side to balance out 
        # the distribution
        bins = []
        num_to_each = ceil(extra / k)

        # setup if we have odd or even number of bins add a bit extra to those first        
        for i in range(2-(k%2)):
            bins.append(per_bin + min(num_to_each, extra))
            extra = max(extra - num_to_each, 0)
        
        # now we can add extra to each side, if enough
        for i in range(0, k-len(bins), 2):

            # NOTE: this does front load the lists
            bins.insert(0, per_bin + min(num_to_each, extra))
            extra = max(extra - num_to_each, 0)
            
            # could half it here
            bins.append(per_bin + min(num_to_each, extra))
            extra = max(extra - num_to_each, 0)
    else:
        bins = [per_bin] * k

    x = argsort(data_set_copy[:, 0])
    
    for i, bin in enumerate(bins):
    
        # get the indices of the elements in the bin
        spl = x[:bin]
        
        fl[spl, ] = i+1

        # adjust     
        x = x[bin:]
        
        # remove singletons
        if i == k-1 and len(x) > 0:
            # grouping a bit odd here
            for data in x:
                fl[data] = i+1
                
    return fl.T.astype(int)[0].tolist()



def natural_breaks(data_set, k, *args, **kwargs):
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
    
    data_std = std(data_set)
    #print(data_std)
    bw = 1.06*data_std*data_set.size**(-1.0/5.0)
    #print(bw)
    
    print(type(data_set))
    _kde = KernelDensity(kernel='gaussian', bandwidth=bw).fit(data_set)
    print(_kde.score_samples(data_set))
    #_kde = KernelDensity(kernel='gaussian', bandwidth=k).fit(data_set)
    
    #print(_kde)
    
    s = linspace(0, 50)
    e = _kde.score_samples(s.reshape(-1,1))
    print(e)
    mi, ma = argrelextrema(e, less)[0], argrelextrema(e, greater)[0]
    
    print(s[mi])
    print(s[ma])
    
