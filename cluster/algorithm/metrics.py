from .kmeans import create_clusters
from ..data.math import mean, sum
from math import log
from concurrent.futures import ThreadPoolExecutor, as_completed
from .. import __MAX_THREADS


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


def ball_hall(data, centroids, multithread=True):
    """
    Ball-Hall Index Metric

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return: Mean of the mean dispersion across clusters
    """
    clusters = create_clusters(data, centroids, multithread=multithread)

    total_dists_to_center = 0
    for clusterIndex, cluster in clusters.items():
        total_dists_to_center += WGSS_k(cluster) / len(cluster)

    return total_dists_to_center / len(clusters)


def banfeld_raferty(data, centroids, multithread=True):
    """
    Banfeld-Raferty Metric

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return: Weighted Sum of the Log of traces of the variance-covariance matrix of each cluster
    """
    clusters = create_clusters(data, centroids, multithread=multithread)

    total_distance_per_cluster = 0
    for clusterIndex, cluster in clusters.items():
        wgss_k = WGSS_k(cluster)

        if wgss_k / len(cluster) > 0.0:
            # Sum of the Log of traces of the variance-covariance matrix of each cluster
            total_distance_per_cluster += len(cluster) * log(wgss_k / len(cluster))

    return total_distance_per_cluster


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
            total_data_dists.append(futr.result()[0])

    return total_data_dists


def c_index(data, centroids, multithread=True):
    """
    C-Index

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return: Measure of Compactness
    """
    clusters = create_clusters(data, centroids, multithread=multithread)

    total_sum = 0.0
    total_members = 0

    num_threads = __MAX_THREADS if multithread else 1

    for clusterIndex, cluster in clusters.items():

        cluster_dists = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futr_dists = {executor.submit(dist_from_one_to_all, cluster[i], cluster[i+1:]):
                              i for i in range(len(cluster)-1)}
            for futr in as_completed(futr_dists):
                cluster_dists.append(futr.result()[0])

        total_sum += sum(cluster_dists)
        total_members += len(cluster_dists)

    # Perform the same calculation that was performed on each cluster on
    # the entire list of data
    total_data_dists = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futr_dists = {executor.submit(dist_from_one_to_all, data[i], data[i + 1:]):
                          i for i in range(len(data) - 1)}
        for futr in as_completed(futr_dists):
            total_data_dists.append(futr.result()[0])

    sorted_distances = sorted(total_data_dists)
    sum_min_dists = sum(sorted_distances[0:total_members])
    sum_max_dists = sum(sorted_distances[::-1][0:total_members])

    return (total_sum-sum_min_dists) / (sum_max_dists-sum_min_dists)


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

    return total_dists_to_center / (len(centroids)* (min_center_dists**2))


def calinski_harabasz(data, centroids, multithread=True):
    """

    :param data:
    :param centroids:
    :param multithread:
    :return:
    """
    clusters = create_clusters(data, centroids, multithread=multithread)

    k = len(centroids)
    n = len(data)

    return ((n-k)/(k-1)) * (BGSS(data, clusters)/WGSS(clusters))