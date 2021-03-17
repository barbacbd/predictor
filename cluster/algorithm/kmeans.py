from ..data.types import Vector
from random import randint
from sys import maxsize
from concurrent.futures import ThreadPoolExecutor, as_completed


def _find_min_dist_centroid(dp: Vector, centroids, idx):
    """
    Possible Batched run. Find the minimum distance from the point provided
    to each of the centroids.

    :param dp: Data point -> cluster.data.type.Vector
    :param centroids: list of current centroids (cluster.data.type.Vector)
    :param idx: index in the array where the data should be stored
    :return: minimum distance from the point provided to each of the centroids
    """
    return min([maxsize] + [dp.distance(c) for _, c in enumerate(centroids)]), idx


def kmeans_pp(data: [Vector], k: int, max_threads: int = 10, seed: int = None):
    """
    kmeans++ algorithm for generating the centroid points. If provided,
    the seed is used to find the first centroid point. Providing the seed is
    ONLY intended for convenience and the ability to reproduce results.

    To provide a random seed the following is a simple example:
        randint(0, len(data)-1)

    :param data: list of cluster.data.type.Vector objects
    :param k: number of centroids to find
    :param max_threads: maximum number or threads that can be spun up (Batch size) [default=10]
    :param seed: index of the data to be used as the first centroid
    ..note::
        If None [default] is provided, then the seed will be chosen randomly

    :return: k generated centroid points
    """
    if seed is None:
        # no seed provided, generate our own
        seed = randint(0, len(data))

    if 0 > seed >= len(data) or k <= 0:
        # bad data return the empty set
        return [], None

    # the first centroid is the data point at position seed
    centroids = [data[seed]]

    # one centroid is already generated
    for c in range(k-1):

        distances = [0.0] * len(data)

        # find the min distance from every point to every centroid
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futr_dists = {executor.submit(_find_min_dist_centroid, data[idx], centroids, idx):
                    idx for idx in range(0, len(data))}
            for futr in as_completed(futr_dists):
                distances[futr.result()[1]] = futr.result()[0]

        # The 'next' centroid is the point whose distance is the largest from ANY centroid
        # Note: this will return the first occurrence of the max, this may cause unwanted behavior
        centroids.append(data[distances.index(max(distances))])

    return centroids, seed
