from .kmeans import match_centroid_to_data, group_to_centroids
from ..data.math import mean
from math import log


def ball_hall(data, centroids, max_threads=10):
    """
    Ball-Hall Index Metric

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param max_threads: number of threads to use when running the algorithm [default = 10]
    :return: Mean of the mean dispersion across clusters
    """
    data_to_closest_centroid = match_centroid_to_data(data, centroids=centroids, max_threads=max_threads)
    groups = group_to_centroids(data, data_to_closest_centroid)

    # find the average distance to each centroid in the list of centroids
    dists = {}
    for x, y in groups.items():
        _sum = sum([y.distance(centroids[x])]) / len(y)
        dists[x] = _sum

    return sum([y for x, y in dists.items()]) / len(dists)


def banfeld_raferty(data, centroids, max_threads=10):
    """
    Banfeld-Raferty Metric

    Weighted Sum of the Log of traces of the variance-covariance matrix of each cluster

    :param data: list of all data points as vectors
    :param centroids: List of all centroids (Vectors)
    :param max_threads: number of threads to use when running the algorithm [default = 10]
    :return:
    """
    data_to_closest_centroid = match_centroid_to_data(data, centroids=centroids, max_threads=max_threads)
    groups = group_to_centroids(data, data_to_closest_centroid)

    total_distance_per_cluster = 0
    for clusterIndex, cluster in groups.items():
        # find the mean or center point of the cluster (Not the cluster point)
        cluster_center = mean(cluster)

        # calculate the distance of all points to the mean point
        distance_to_center = sum([dp.distance(cluster_center) for dp in cluster])

        # Sum of the Log of traces of the variance-covariance matrix of each cluster
        total_distance_per_cluster += (len(cluster) * log(distance_to_center / len(cluster)))

    return total_distance_per_cluster
