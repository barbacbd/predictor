from .kmeans import match_centroid_to_data, group_to_centroids


def ball_hall(data: [Vector], centroids, max_threads: int = 10):
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