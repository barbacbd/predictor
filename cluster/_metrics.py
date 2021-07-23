from numpy import unique, mean
import numpy
from scipy.spatial.distance import euclidean, pdist, cdist
from math import log
# from concurrent.futures import ThreadPoolExecutor, as_completed
from . import __MAX_THREADS
from ._io import read_data_file
from sklearn.cluster import k_means


class Metric:

    def __init__(self, data, labels):
        """

        :param data:
        :param labels:
        """
        self.data = data

        self.clusters = {}
        for cluster_id in unique(labels):
            idx = [i for i, cluster in enumerate(labels) if cluster == cluster_id]
            self.clusters[cluster_id] = data[idx, :]

        # once these values are defined once they wont need to be
        # defined again. However, for efficiency, we will fill them as needed
        self._wgss = None
        self._bgss = None
        self.cluster_dispersion = {}
        self._pdist_value = None

    def _pdist(self):
        if not self._pdist_value:
            self._pdist_value = pdist(self.data)

    @staticmethod
    def BGSS(data, clusters):
        """
        Sum of the weighted sum of the squared distances between G_k and G, where G_k
        is the baycenter of a cluster and G is the baycenter of the entire dataset.

        :param data: Dataset of all values
        :param clusters: Dictionary {key: cluster ID, value: list of elements in the cluster}

        :return: Sum of the weighted sum of the squared distances between G_k and G, where G_k
        is the baycenter of a cluster and G is the baycenter of the entire dataset. The weight is
        the number n_k of elements in the cluster
        """
        G = mean(data)
        bgss = 0

        for clusterIndex, cluster in clusters.items():
            G_k = mean(cluster)
            # TODO: this is the weighted sum, should i actually divide by len cluster here
            bgss += len(cluster) * euclidean(G_k, G)**2

        return bgss

    def _BGSS(self):
        """
        Sum of the weighted sum of the squared distances between G_k and G, where G_k
        is the baycenter of a cluster and G is the baycenter of the entire dataset.

        :return:
        """
        if self._bgss is not None:
            return self._bgss
        else:
            self._bgss = Metric.BGSS(self.data, self.clusters)

    @staticmethod
    def WGSS_k(cluster):
        """
        The within-cluster dispersion. Sum of the square distances between each element
        of the cluster and the cluster baycenter (mean)

        :param cluster: List of elements in the cluster
        :return: sum of the square distances between each element of the cluster and the cluster center
        """
        cluster_center = mean(cluster)
        return sum([euclidean(dp, cluster_center) ** 2 for dp in cluster])

    def _wgss_k_all(self):
        for cluster_id, cluster_data in self.clusters.items():
            if cluster_id not in self.cluster_dispersion:
                self.cluster_dispersion[cluster_id] = Metric.WGSS_k(cluster_data)

    @staticmethod
    def WGSS(clusters):
        """
        Sum of the within-cluster dispersions for all clusters

        :param clusters: Dictionary {key: cluster ID, value: list of elements in the cluster}
        :return: sum of the within-cluster dispersion of all clusters
        """
        return sum([Metric.WGSS_k(cluster) for clusterIndex, cluster in clusters.items()])

    def _WGSS(self):
        """
        Sum of the within-cluster dispersions for all clusters

        :return: sum of the within-cluster dispersion of all clusters
        """
        if self._wgss is not None:
            return self._wgss
        else:
            self._wgss = Metric.WGSS(self.clusters)

    def BallHall(self):
        """
        Ball-Hall Index Metric

        :return: Mean of the mean dispersion across clusters
        """
        self._wgss_k_all()

        return sum([
            wgss_val/len(self.clusters[cluster_id])
            for cluster_id, wgss_val in self.cluster_dispersion.items()
        ]) / len(self.clusters)

    def BanfeldRaftery(self):
        """
        Banfeld-Raferty Metric

        :return: Weighted Sum of the Log of traces of the variance-covariance matrix of each cluster
        """
        self._wgss_k_all()

        return sum([
            len(self.clusters[cluster_id]) * log(wgss_val) / len(self.clusters[cluster_id])
            for cluster_id, wgss_val in self.cluster_dispersion.items()
            if wgss_val / len(self.clusters[cluster_id]) > 0.0
        ])

    def CIndex(self):
        """
        C-Index

        :return: Measure of Compactness
        """
        sw = 0  # sum of the NW distances between all pairs of points in each cluster
        nw = 0  # total number of points in the entire dataset

        # TODO: save the pairwise distances for all clusters
        for cluster_id, cluster_data in self.clusters.items():
            cluster_pairwise = pdist(cluster_data)
            sw += sum(cluster_pairwise)
            nw += len(cluster_pairwise)

        self._pdist()

        # sort the list for easier search operations
        sorted_pdist = sorted(self._pdist_value)

        # Sum of the NW smallest distances between all pairs of points
        min_sum = sum(sorted_pdist[0 : nw])

        # Sum of the NW largest distances between all pairs of points
        max_sum = sum(sorted_pdist[::-1][0 : nw])

        return (sw - min_sum) / (max_sum - min_sum)

    def CalinskiHarabasz(self):
        """
        Calinski-Harabasz Index

        :return:
        """
        N = len(self.data)
        K = len(self.clusters)
        self._WGSS()
        self._BGSS()

        return ((N-K) * self._bgss) / ((K-1) * self._wgss)

    def DaviesBouldin(self):
        """

        :return:
        """

    def DetRatio(self):
        """

        :return:
        """

    def DunnIndex(self):
        """

        :return:
        """
        # Denote dMin as the minimal distance between points of different clusters
        # TODO Can we batch thread this ? -- sure we can !
        min_cdists = numpy.ndarray()
        enumerated_clusters = list(self.clusters.values())
        for i in range(len(enumerated_clusters) - 1):
            for j in range(i+1, len(enumerated_clusters) - 1):
                numpy.append(min_cdists, numpy.min(cdist(enumerated_clusters[i], enumerated_clusters[j])))
        d_min = numpy.min(min_cdists)

        # Denote dMax as the largest within cluster distance
        self._wgss_k_all()
        d_max = max(list(self.cluster_dispersion.values()))

        return d_min / d_max


class _ConvenientMetric(Metric):

    def __init__(self, filename, *args, **kwargs):
        """

        :param filename: full file path and name of the file

        :param \**kwargs:
            see below

        :keyword arguments:
            * *delimiter* (``string``) --
              Separation character for the data file.

            * *num_columns* (``int``) --
              Number of columns to separate data by, dimensions of the data points

            * *num_clusters* (``int``) --
              See sklearn.cluster.k_means

            * *random_state* (``int``) --
              See sklearn.cluster.k_means
              None, or int

            * *init* (``string``) --
              See sklearn.cluster.k_means
              k-means++, random
        """
        delim = kwargs.get('delimiter', ' ')
        num_columns = kwargs.get('num_columns', 1)
        npdata = read_data_file(filename, delimiter=delim, num_columns=num_columns)

        centroids, matching_clusters, weighted_sum_to_centroids = k_means(
            npdata,
            kwargs.get('num_clusters', 3),
            random_state=kwargs.get('random_state', None),
            init=kwargs.get('init', 'k-means++')
        )

        super(_ConvenientMetric, self).__init__(npdata, matching_clusters)
