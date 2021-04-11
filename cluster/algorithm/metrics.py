from .kmeans import create_clusters
from ..data.math import mean, sum
from math import log
from concurrent.futures import ThreadPoolExecutor, as_completed


def ball_hall(data, centroids, multithread=True):
    """
    Ball-Hall Index Metric

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param multithread: when true, multithread the algorithm with the suggested number of threads
    :return: Mean of the mean dispersion across clusters
    """
    clusters = create_clusters(data, centroids, multithread=multithread)

    # find the average distance to each centroid in the list of centroids
    dists = {}
    for x, y in clusters.items():
        dists[x] = sum([_y.distance(centroids[x]) for _y in y]) / len(y)

    return sum([y for x, y in dists.items()]) / len(dists)


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
        # find the mean or center point of the cluster (Not the cluster point)
        cluster_center = mean(cluster)

        # calculate the distance of all points to the mean point
        distance_to_center = sum([dp.distance(cluster_center) for dp in cluster])

        # Sum of the Log of traces of the variance-covariance matrix of each cluster
        total_distance_per_cluster += (len(cluster) * log(distance_to_center / len(cluster)))

    return total_distance_per_cluster


def dist_from_one_to_all(dp, dp_list):
    """
    Find the distance from the data point to all data points in the list

    :param dp: Single Data point
    :param dp_list: List of data points
    :return: list containing the distance from dp to all points in dp_list
    """
    return [dp.distance(list_point) for list_point in dp_list]


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

    for clusterIndex, cluster in clusters.items():

        cluster_dists = []
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futr_dists = {executor.submit(dist_from_one_to_all, cluster[i], cluster[i+1:]):
                              i for i in range(len(cluster)-1)}
            for futr in as_completed(futr_dists):
                cluster_dists.extend(futr.result()[0])

        total_sum += sum(cluster_dists)
        total_members += len(cluster_dists)

    # Perform the same calculation that was performed on each cluster on
    # the entire list of data
    total_data_dists = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futr_dists = {executor.submit(dist_from_one_to_all, data[i], data[i + 1:]):
                          i for i in range(len(data) - 1)}
        for futr in as_completed(futr_dists):
            total_data_dists.extend(futr.result()[0])

