from ..data.types import Vector
from random import randint, uniform
from sys import maxsize
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from collections import defaultdict


def _find_min_dist_centroid(dp: Vector, centroids, idx):
    """
    Possible Batched run. Find the minimum distance from the point provided
    to each of the centroids.

    :param dp: Data point -> cluster.data.type.Vector
    :param centroids: list of current centroids (cluster.data.type.Vector)
    :param idx: index in the array where the data should be stored
    :return: minimum distance from the point provided to each of the centroids
    """
    closest_centroid_pos = -1
    distance = maxsize

    for pos, c in enumerate(centroids):
        tdist = dp.distance(c)
        if tdist < distance:
            distance = tdist
            closest_centroid_pos = pos

    return distance, idx, closest_centroid_pos


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


def _find_min_max_values(data: [Vector]):
    """
    Find all minimum and maximum values and store them into vectors

    :param data: list of vectors
    :return: min_vector, max_vector
    """
    max_vector = Vector()
    min_vector = Vector()

    for var in ('x', 'y', 'z', 'w'):

        min_var = maxsize
        max_var = -maxsize

        for dp in data:
            if getattr(dp, var, None) is not None:
                min_var = min(getattr(dp, var), min_var)
                max_var = max(getattr(dp, var), max_var)

        setattr(max_vector, var, max_var)
        setattr(min_vector, var, min_var)

    return min_vector, max_vector


def _generate_random_vector(min_v: Vector, max_v: Vector):
    """
    Generate Random Data that is between the min and max values for the vectors

    :param min_v: Vector containing the min extremes for all values
    :param max_v: Vector containing the max extremes for all values
    :return: Resultant Vector of random data
    """
    result = Vector()

    for var in ('x', 'y', 'z', 'w'):
        if getattr(min_v, var, None) is not None and getattr(max_v, var, None) is not None:
            setattr(result, var, uniform(getattr(min_v, var), getattr(max_v, var)))
    return result


def match_centroid_to_data(data: [Vector], centroids: {}, max_threads: int = 10):
    """

    :param data:
    :param centroids:
    :return:
    """
    data_to_closest_centoid = [None] * len(data)

    # find the min distance from every point to every centroid
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futr_dists = {executor.submit(_find_min_dist_centroid, data[idx], centroids, idx):
                          idx for idx in range(0, len(data))}
        for futr in as_completed(futr_dists):
            data_to_closest_centoid[futr.result()[1]] = futr.result()[2]

    return data_to_closest_centoid


def group_to_centroids(data: [Vector], data_to_closest_centroid):
    """

    :param data:
    :param data_to_closest_centroid:
    :return:
    """
    groups = defaultdict(list)

    if len(data) != len(data_to_closest_centroid):
        if not __debug__:
            print("Grouping data, lengths of data do not match.")
    else:
        for idx, centroid in enumerate(data_to_closest_centroid):
            groups[centroid].append(deepcopy(data[idx]))

    return groups


# def kmeans(data: [Vector], k: int, max_threads: int = 10, seed: int = None, kmeans_pp=False):
#     """
#
#     :param data:
#     :param k:
#     :param max_threads:
#     :param seed:
#     :param kmeans_pp:
#     :return:
#     """
#
#     if kmeans_pp:
#         centroids, seed = kmeans_pp(data, k, max_threads=max_threads, seed=seed)
#     else:
#         if not __debug__:
#             print("Not running kmeans")
#
#         return


# def kmeans(data: [Vector], k: int, max_threads: int = 10):
#     """
#
#     :param data:
#     :param k:
#     :return:
#     """
#
#     min_vector, max_vector = _find_min_max_values(data)
#
#     # create ids for the centroids
#     centroids = {
#         c_id+1: _generate_random_vector(min_vector, max_vector) for c_id in range(k)
#     }
#
#     data_to_closest_centroid = _kmeans_assignment(data, centroids, max_threads=max_threads)
#
#     while True:
#         recent_closest = deepcopy(data_to_closest_centroid)
#
#         data_to_closest_centroid = _kmeans_assignment(data, centroids, max_threads=max_threads)
#
#         # if all in recent_closest == data_to_closest_centroid:
#         # break