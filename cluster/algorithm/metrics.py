from .kmeans import create_clusters
from ..data.math import mean, sum
from math import log
from .helper import WGSS, WGSS_k, BGSS, pairwise_distance, dMin, dMax

nw = lambda nk : (nk * (nk -1)) / 2
nt = lambda n : (n * (n-1)) / 2


def ball_hall(data, *args, **kwargs):
    """
    Ball-Hall Index Metric

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Mean of the mean dispersion across clusters
    """
    multithread = kwargs.get("multithread", True)

    if "clusters" in kwargs:
        clusters = kwargs.get("clusters")
    else:
        if "centroids" in kwargs:
            clusters = create_clusters(data, kwargs.get("centroids"), multithread=multithread)
        else:
            # TODO: should this return -float('inf')?
            return 0  # return opposite of max diff

    total_dists_to_center = 0
    for clusterIndex, cluster in clusters.items():
        total_dists_to_center += WGSS_k(cluster) / len(cluster)

    return total_dists_to_center / len(clusters)


def banfeld_raftery(data, *args, **kwargs):
    """
    Banfeld-Raferty Metric

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Weighted Sum of the Log of traces of the variance-covariance matrix of each cluster
    """
    multithread = kwargs.get("multithread", True)

    if "clusters" in kwargs:
        clusters = kwargs.get("clusters")
    else:
        if "centroids" in kwargs:
            clusters = create_clusters(data, kwargs.get("centroids"), multithread=multithread)
        else:
            return float('inf')  # return opposite of min

    total_distance_per_cluster = 0
    for clusterIndex, cluster in clusters.items():
        wgss_k = WGSS_k(cluster)

        if wgss_k / len(cluster) > 0.0:
            # Sum of the Log of traces of the variance-covariance matrix of each cluster
            total_distance_per_cluster += len(cluster) * log(wgss_k / len(cluster))

    return total_distance_per_cluster


def c_index(data, *args, **kwargs):
    """
    C-Index

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """
    multithread = kwargs.get("multithread", True)

    if "clusters" in kwargs:
        clusters = kwargs.get("clusters")
    else:
        if "centroids" in kwargs:
            clusters = create_clusters(data, kwargs.get("centroids"), multithread=multithread)
        else:
            return float('inf')  # C-Index is min acceptable, so instead of 0 return max value

    sw = 0
    _nw = 0
    for clusterIndex, cluster in clusters.items():
        c_pdist = pairwise_distance(cluster, multithread=multithread)
        sw += sum(c_pdist)
        _nw += int(nw(len(cluster)))

    pdists = pairwise_distance(data, multithread=multithread)
    s_pdists = sorted(pdists)
    s_min = sum(s_pdists[0:_nw])
    s_max = sum(s_pdists[::-1][0:_nw])

    try:
        return (sw - s_min) / (s_max - s_min)
    except ZeroDivisionError:
        # C-Index is min acceptable, so instead of 0 return max value
        return float('inf')


def calinski_harabasz(data, *args, **kwargs):
    """
    Calinski-Harabasz Index

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) --
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

        * *k* (``uint``) -- Provide for efficiency
          Number of centroids 
        
        * *bgss* (``float``) -- Provide for efficiency
          See BGSS function above for details
        
        * *wgss* (``float``) -- Provide for efficiency
          See WGSS function above for details

    :return:
    """
    multithread = kwargs.get("multithread", True)

    n = len(data)
    bgss = kwargs.get("bgss", None)
    wgss = kwargs.get("wgss", None)
    k = kwargs.get("k", None)
    clusters = kwargs.get("clusters", None)
    centroids = kwargs.get("centroids", None)

    if None not in (bgss, wgss, k, clusters):
        return ((n-k)/(k-1)) * (bgss/wgss)
    elif None not in (clusters, k):
        if not bgss:
            bgss = BGSS(data, clusters)
        
        if not wgss:
            wgss = WGSS(clusters)
    
        return ((n-k)/(k-1)) * (bgss/wgss)
    else:
        if clusters is None:
            if centroids is not None:
                if not k:
                    k = len(centroids)
                clusters = create_clusters(data, centroids, multithread=multithread)
            else:
                return -float('inf')  # CH looks for max, return min
        
        if k is None:
            if not centroids:
                return -float('inf')
            else:
                k = len(centroids)

        return ((n-k)/(k-1)) * (BGSS(data, clusters)/WGSS(clusters))


def davies_bouldin(data, *args, **kwargs):
    """
    Davies-Bouldin

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def det_ratio(data, *args, **kwargs):
    """
    Determinant Ratio

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def dunn(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) --
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

        * *dmin* (``float``) -- Provide for efficiency
          min inter-cluster distance

        * *dmax* (``float``) -- Provide for efficiency
          Max intra-cluster distance

    :return:
    """
    multithread=kwargs.get("multithread", True)

    d_min = kwargs.get("dmin", None)
    d_max = kwargs.get("dmax", None)

    if None in (d_min, d_max):
        clusters = kwargs.get("clusters", None)
        if clusters is None:
            centroids = kwargs.get("centroids", None)
            if centroids is None:
                return -float('inf')
            else:
                clusters = create_clusters(data, centroids, multithread=multithread)

        if d_min is None:
            d_min = dMin(clusters, multithread=multithread)

        if d_max is None:
            d_max = dMax(clusters, multithread=multithread)

    return d_min / d_max


def baker_hubert_gamma(data, *args, **kwargs):
    """
    Baker Hubert Gamma

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def gdi(data, *args, **kwargs):
    """
    GDI

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def g_plus(data, *args, **kwargs):
    """
    G-Plus

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def ksq_detw(data, *args, **kwargs):
    """


    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def log_det_ratio(data, *args, **kwargs):
    """
    Log of the Determinant Ratio

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def log_ss_ratio(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) --
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

        * *bgss* (``float``) -- Provide for efficiency
          See BGSS function above for details
        
        * *wgss* (``float``) -- Provide for efficiency
          See WGSS function above for details

    :return:
    """
    multithread = kwargs.get("multithread", True)
    bgss = kwargs.get("bgss", None)
    wgss = kwargs.get("wgss", None)
    clusters = kwargs.get("clusters", None)
    centroids = kwargs.get("centroids", None)

    if None in (bgss, wgss):
        if not clusters:
            if centroids:
                clusters = create_clusters(data, centroids, multithread=multithread)
            else:
                return float('inf')  # opposite of min diff
        
        if not bgss:
            bgss = BGSS(data, clusters)
        
        if not wgss:
            wgss = WGSS(clusters)

        return log(BGSS(data, clusters)/WGSS(clusters))

    return log(bgss/wgss)


def mcclain_rao(data, *args, **kwargs):
    """
    McClain-Rao

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def pbm(data, *args, **kwargs):
    """


    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def point_biserial(data, *args, **kwargs):
    """
    Point Biserial

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def ratkowsky_lance(data, *args, **kwargs):
    """


    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def ray_turi(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def scott_symons(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def sd(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def s_dbw(data, *args, **kwargs):
    """
    C-Index

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def silhouette(data, *args, **kwargs):
    """
    C-Index

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def tau(data, *args, **kwargs):
    """
    C-Index

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def trace_w(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) -- Required
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

        * *wgss* (``float``) --
          See WGSS function above for details

    :return:
    """
    multithread = kwargs.get("multithread", True)

    wgss = kwargs.get("wgss", None)
    if not wgss:

        clusters = kwargs.get("clusters", None)
        if not clusters:

            centroids = kwargs.get("centroids", None)
            if not centroids:
                return -float('inf')
            
            clusters = create_clusters(data, centroids, multithread=multithread)
        
        wgss = WGSS(clusters)
    
    return wgss


def trace_wib(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def wemmert_gancarski(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) --
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of Compactness
    """


def xie_beni(data, *args, **kwargs):
    """
    Xie-Beni Index

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``list``) -- Required
          List of all centroids (Vectors)

        * *clusters* (``dict``) -- Provide for efficiency
          When present, ignore centroids. The clusters is a dictionary of cluster index to the
          list of Vectors in the cluster.

        * *multithread* (``bool``) --
          When True [default], multithread the algorithm using a suggested number of threads

    :return: Measure of compactness
    """
    multithread = kwargs.get("multithread", True)

    centroids = kwargs.get("centroids", None)
    if not centroids:
        return float('inf')

    clusters = kwargs.get("clusters", None)
    if not clusters:
        clusters = create_clusters(data, centroids, multithread=multithread)

    cluster_means = []
    all_distances_to_center = []
    for clusterIndex, cluster in clusters.items():
        # find the mean or center point of the cluster (Not the cluster point)
        cluster_center = mean(cluster)
        cluster_means.append(cluster_center)

        # calculate the distance of all points to the mean point
        all_distances_to_center.extend([dp.distance(cluster_center)**2 for dp in cluster])

    total_dists_to_center = sum(all_distances_to_center)
    min_center_dists = min(pairwise_distance(cluster_means, multithread=multithread))

    return total_dists_to_center / (len(centroids) * (min_center_dists**2))