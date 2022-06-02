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
    """
    Find the minimum distance between clusters. Find the minimum distance
    between all clusters, and return the minimum of those distances.

    :param cluster1: Cluster to compare to all other clusters
    :param other_clusters: Rest of the clusters
    :return: minimum of the minimum distances between clusters
    """
    all_dists = []
    for dp in cluster1:
        for oc in other_clusters:
            all_dists.extend(dist_from_one_to_all(dp, oc))
    return min(all_dists)


def pairwise_distance(data, multithread=True):
    """
    Find the distance between all pairs of points

    :param data: list of all data points as Vectors
    :param multithread: When true, thread the execution
    :return: List of distances between all points in no particular order
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
    """
    Find the minimum of the minimum intracluster distances

    :param clusters: dictionary containing the cluster information
    :param multithread: When true, thread the execution
    :return: Min of the min intracluster distances
    """
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
    """
    Find the maximum intercluster distances for all clusters.

    :param clusters: dictionary containing the cluster information
    :param multithread: When true, thread the execution
    :return: Return the max, of the max intercluster distances
    """
    return max([max(pairwise_distance(cluster, multithread=multithread)) for _, cluster in clusters.items()])


def det(matrix):
    """
    Determinant for the matrix. Recursive function where the base case is a
    1x1 matrix (or a single element)

    :param matrix:
    :return: Determinant of the matrix
    """
    # determinant is only calculated for square matrices
    row_len_set = set()
    if isinstance(matrix, list):
        row_len_set.add(len(matrix))
        for x in matrix:
            if isinstance(x, list):
                row_len_set.add(len(x))
            else:
                row_len_set.add(-1)

    if len(row_len_set) != 1 or -1 in row_len_set:
        return 0

    if len(matrix) == 1:
        # technically we should only allow a single element
        # but we will just return the first element
        return matrix[0][0]

    sum = 0

    # grab the top row from the matrix
    for column, row in enumerate(matrix[0]):

        # alternate signs following a pattern like +-+-+- ...
        sign = 1 if column % 2 == 0 else -1

        # remove the first row and first column, shrinks the matrix by 1 element in each direction
        sub_det = [sub_mat[:column] + sub_mat[column + 1:] for sub_mat in matrix[1:]]

        sum += sign * row * det(sub_det)

    return sum

