from collections import defaultdict
from numpy import unique, mean
from scipy.spatial.distance import euclidean, pdist
from math import log


class Metric:

    def __init__(self, data, clusters, labels):
        """

        :param data:
        :param clusters:
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

