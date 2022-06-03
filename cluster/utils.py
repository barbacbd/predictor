from .clusters import *


def process_clusters(clusters):
    '''The min cluster numbers should be the first element and the 
    max cluster numbers should be the second element. If only one
    element exists, then the upper and lower limit are the same. 
    
    :param clusters: list of cluster values
    :return: min, max number of clustes
    '''
    if not isinstance(clusters, list):
        raise AttributeError

    # never be less than 0 but you never know
    if len(clusters) <= 0:
        raise AttributeError

    if len(clusters) == 1:
        return clusters[0], clusters[0]

    if clusters[0] < 1 or clusters[1] < 1:
        raise AttributeError
    return min(clusters[0], clusters[1]), max(clusters[0], clusters[1])
