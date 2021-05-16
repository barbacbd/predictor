from .kmeans import create_clusters
from ..data.math import mean, sum
from math import log
from concurrent.futures import ThreadPoolExecutor, as_completed
from .. import __MAX_THREADS


nw = lambda nk : (nk * (nk -1)) / 2
nt = lambda n : (n * (n-1)) / 2


def BGSS(data, clusters):
    """
    Sum of the weighted sum of the squared distances between G_k and G, where G_k
    is the baycenter of a cluster and G is the baycenter of the entire dataset.

    :param data: Dataset of vectorsr
    :param clusters: dictionary containing the cluster information
    :return: Sum of the weighted sum of the squared distances between G_k and G, where G_k
    is the baycenter of a cluster and G is the baycenter of the entire dataset. The weight is
    the number n_k of elements in the cluster
    """
    G = mean(data)
    bgss = 0

    for clusterIndex, cluster in clusters.items():
        G_k = mean(cluster)
        bgss += len(cluster) * G_k.distance(G)**2

    return bgss


def WGSS_k(cluster):
    """
    The within-cluster dispersion. Sum of the square distances between each element
    of the cluster and the cluster baycenter (mean)

    :param cluster: List of elements in the cluster
    :return: sum of the square distances between each element of the cluster and the cluster center
    """
    cluster_center = mean(cluster)
    return sum([dp.distance(cluster_center) ** 2 for dp in cluster])


def WGSS(clusters):
    """
    Sum of the within-cluster dispersions for all clusters

    :param clusters: dictionary containing the cluster information
    :return: sum of the within-cluster dispersion of all clusters
    """
    return sum([WGSS_k(cluster) for clusterIndex, cluster in clusters.items()])


def dist_from_one_to_all(dp, dp_list):
    """
    Find the distance from the data point to all data points in the list

    :param dp: Single Data point
    :param dp_list: List of data points
    :return: list containing the distance from dp to all points in dp_list
    """
    return [dp.distance(list_point) for list_point in dp_list]


def find_min_dist_between_clusters(cluster1, other_clusters):

    all_dists = []
    for dp in cluster1:
        for oc in other_clusters:
            all_dists.extend(dist_from_one_to_all(dp, oc))
    return min(all_dists)


def pairwise_distance(data, multithread=True):
    """

    :param data:
    :param multithread:
    :return:
    """
    num_threads = __MAX_THREADS if multithread else 1

    total_data_dists = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futr_dists = {executor.submit(dist_from_one_to_all, data[i], data[i + 1:]):
                          i for i in range(len(data) - 1)}
        for futr in as_completed(futr_dists):
            total_data_dists.extend(futr.result())

    return total_data_dists


def dMin(clusters, multithread=True):
    num_threads = __MAX_THREADS if multithread else 1

    _clusters = [x for _, x in clusters.items()]

    total_min_data_dists = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futr_dists = {executor.submit(find_min_dist_between_clusters, _clusters[i], _clusters[i+1:]):
                          i for i in range(len(_clusters) - 1)}
        for futr in as_completed(futr_dists):
            total_min_data_dists.append(futr.result())

    return min(total_min_data_dists)

    
def dMax(clusters, multithread=True):
    return max([max(pairwise_distance(cluster, multithread=multithread)) for _, cluster in clusters.items()])


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

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def det_ratio(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


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

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def gdi(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def g_plus(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def ksq_detw(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def log_det_ratio(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


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

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def pbm(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def point_biserial(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def ratkowsky_lance(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def ray_turi(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def scott_symons(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def sd(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def s_dbw(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def silhouette(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def tau(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


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
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def wemmert_gancarski(data, *args, **kwargs):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


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