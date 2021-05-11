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


def ball_hall(data, *args, **kwargs):
    """
    Ball-Hall Index Metric

    :param data: list of all data points as vectors
    :param \**kwargs:
        see below

    :keyword arguments:
        * *centroids* (``dict``) --

        * *clusters* (``dict``) --
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
        * *centroids* (``dict``) --

        * *clusters* (``dict``) --
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


def c_index(data, centroids, multithread=True):
    """
    C-Index

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return: Measure of Compactness
    """
    clusters = create_clusters(data, centroids, multithread=multithread)

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


def calinski_harabasz(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)

    k = len(centroids)
    n = len(data)

    return ((n-k)/(k-1)) * (BGSS(data, clusters)/WGSS(clusters))


def davies_bouldin(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def det_ratio(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def dunn(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def baker_hubert_gamma(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def gdi(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def g_plus(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def ksq_detw(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def log_det_ratio(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def log_ss_ratio(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)
    return log(BGSS(data, clusters)/WGSS(clusters))


def mcclain_rao(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def pbm(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def point_biserial(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def ratkowsky_lance(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def ray_turi(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def scott_symons(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def sd(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def s_dbw(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def silhouette(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def tau(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def trace_w(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)
    return WGSS(clusters)


def trace_wib(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def wemmert_gancarski(data, centroids, multithread=True):
    """

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)


def xie_beni(data, centroids, multithread=True):
    """
    Xie-Beni Index

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return: Measure of compactness
    """
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