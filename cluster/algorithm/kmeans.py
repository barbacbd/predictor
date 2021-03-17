from ..data.types import Vector
from random import randint
from sys import maxsize
from concurrent.futures import ThreadPoolExecutor, as_completed


def _find_min_dist_centroid(dp: Vector, centroids, idx):
    """

    :param dp:
    :param centroids:
    :param idx:
    :return:
    """
    return min([maxsize] + [dp.distance(c) for _, c in enumerate(centroids)]), idx


def create_centroids_seeded(data: [Vector], k: int, seed: int, max_threads: int):
    """
    kmeans++ algorithm for generating the centroid points based on a seeded value.
    The seed is used to find the first centroid point, and is ONLY provided for
    the ability to reproduce results. To provide a random seed please use the
    function create_centroids (below).

    :param data: list of cluster.data.type.Vector objects
    :param k: number of centroids to find
    :param seed: index of the data to be used as the first centroid
    :param max_threads: maximum number or threads that can be spun up. Also the batch size
    :return: k generated centroid points
    """
    centroids = [data[seed]]

    # one centroid is already generated
    for c in range(k-1):

        distances = [0.0] * len(data)

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futr_dists = {executor.submit(_find_min_dist_centroid, data[idx], centroids, idx):
                    idx for idx in range(0, len(data))}
            for futr in as_completed(futr_dists):
                distances[futr.result()[1]] = futr.result()[0]

        # Note: this will return the first occurrence of the max, this may cause unwanted behavior
        centroids.append(data[distances.index(max(distances))])

    return centroids

def create_centroids(data: [Vector], k: int, max_threads=10):
    """
    kmeans++ algorithm for generating the centroid points. Generate a random first
    seed that is in the range of 0 to the length of the data. 

    :param data: list of cluster.data.type.Vector objects
    :param k: number of centroids to find
    :param max_threads: maximum number or threads that can be spun up. Also the batch size
    :return: k generated centroid points, seed
    """
    seed = randint(0, len(data)-1)

    return create_centroids_seeded(data, k, seed, max_threads=max_threads), seed
