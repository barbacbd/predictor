from ..data.math import mean, sum
from concurrent.futures import ThreadPoolExecutor, as_completed
from .. import __MAX_THREADS


def BGSS(data, clusters):
    """
    Sum of the weighted sum of the squared distances between G_k and G, where G_k
    is the baycenter of a cluster and G is the baycenter of the entire dataset.

    :param data: Dataset of Vectors
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
        futr_dists = {executor.submit(find_min_dist_between_clusters, _clusters[i], _clusters[i + 1:]):
                          i for i in range(len(_clusters) - 1)}
        for futr in as_completed(futr_dists):
            total_min_data_dists.append(futr.result())

    return min(total_min_data_dists)


def dMax(clusters, multithread=True):
    return max([max(pairwise_distance(cluster, multithread=multithread)) for _, cluster in clusters.items()])