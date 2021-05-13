from unittest import TestCase, main
from cluster.data import DataSet, Vector
from cluster.algorithm import kmeans_pp
from cluster.algorithm.metrics import (
    ball_hall,
    banfeld_raftery,
    c_index,
    xie_beni,
    calinski_harabasz,
    log_ss_ratio,
    trace_w,
    WGSS,
    BGSS
)
from cluster.algorithm.kmeans import create_clusters
from random import uniform, randint
from os import remove

DATA_FILE = 'random_test_data.txt'
NUM_DATA = 1000

class TestDataSetCreation(TestCase):

    def tearDown(self) -> None:
        try:
            remove(DATA_FILE)
        except:
            pass

    @staticmethod
    def create_data_file():
        data = [uniform(0.0, 20.0) for x in range(NUM_DATA)]

        num_per_line = randint(1, 20)

        dim_cpy = data.copy()

        with open(DATA_FILE, 'w') as _file:
            while len(dim_cpy) > 0:
                temp_data = " ".join([str(x) for x in dim_cpy[:num_per_line]])
                _file.write(f"{temp_data}\n")
                dim_cpy = dim_cpy[num_per_line:]

    def test_1_data_set_creation(self):
        """

        """
        TestDataSetCreation.create_data_file()

        for dim in (1, 2, 3, 4):
            _d = DataSet(DATA_FILE, dimensions=dim)
            self.assertEqual(int(NUM_DATA / dim), len(_d._data), f'Testing {NUM_DATA} on {dim} dimensions')

    # def test_2_create_centroids(self):
    #     """
    #     ..note::
    #     This is NOT a test right now as it does not assert anything
    #     """
    #     TestDataSetCreation.create_data_file()
    #     dataset = DataSet(DATA_FILE, dimensions=1)
    #     data = dataset.data
    #
    #     centroids, seed = kmeans_pp(data=data, k=2)
    #
    #     print("Finished Centroids")
    #
    #     # metric = ball_hall(data, centroids)
    #     # print("Ball Hall Metric = {}".format(metric))
    #     #
    #     # metric = banfeld_raftery(data, centroids)
    #     # print("Banfeld Raftery Metric = {}".format(metric))
    #
    #     metric = c_index(data, centroids)
    #     print("C Index Metric = {}".format(metric))
    #
    #     # metric = xie_beni(data, centroids)
    #     # print("Xie Beni Metric = {}".format(metric))

    def test_3_small_data_set_creation(self):
        """

        """
        small_dataset = DataSet("small_test_data.txt", dimensions=1)
        small_data = small_dataset.data

        centroids, seed = kmeans_pp(data=small_data, k=3, seed=6)

        clusters = create_clusters(small_data, centroids, multithread=True)
        bgss = BGSS(small_data, clusters)
        wgss = WGSS(clusters)
        
        metric = ball_hall(small_data, centroids=centroids)
        print("Ball Hall Metric = {}".format(metric))
        metric = ball_hall(small_data, clusters=clusters)
        print("Ball Hall Metric = {}".format(metric))

        metric = banfeld_raftery(small_data, centroids=centroids)
        print("Banfeld Raftery Metric = {}".format(metric))
        metric = banfeld_raftery(small_data, clusters=clusters)
        print("Banfeld Raftery Metric = {}".format(metric))

        metric = c_index(small_data, centroids=centroids)
        print("C Index Metric = {}".format(metric))
        metric = c_index(small_data, clusters=clusters)
        print("C Index Metric = {}".format(metric))

        metric = xie_beni(small_data, centroids=centroids)
        print("Xie Beni Metric = {}".format(metric))
        metric = xie_beni(small_data, clusters=clusters, centroids=centroids)
        print("Xie Beni Metric = {}".format(metric))

        metric = calinski_harabasz(small_data, centroids=centroids)
        print("Calinski Harabasz Metric = {}".format(metric))
        metric = calinski_harabasz(small_data, centroids=centroids, clusters=clusters)
        print("Calinski Harabasz Metric = {}".format(metric))
        metric = calinski_harabasz(small_data, centroids=centroids, wgss=wgss)
        print("Calinski Harabasz Metric = {}".format(metric))
        metric = calinski_harabasz(small_data, centroids=centroids, clusters=clusters, wgss=wgss)
        print("Calinski Harabasz Metric = {}".format(metric))
        metric = calinski_harabasz(small_data, centroids=centroids, bgss=bgss, wgss=wgss)
        print("Calinski Harabasz Metric = {}".format(metric))
        metric = calinski_harabasz(small_data, centroids=centroids, clusters=clusters, wgss=wgss, bgss=bgss)
        print("Calinski Harabasz Metric = {}".format(metric))

        metric = log_ss_ratio(small_data, centroids=centroids)
        print("LOG SS Ratio Metric = {}".format(metric))
        metric = log_ss_ratio(small_data, centroids=centroids, clusters=clusters)
        print("LOG SS Ratio Metric = {}".format(metric))
        metric = log_ss_ratio(small_data, centroids=centroids, wgss=wgss)
        print("LOG SS Ratio Metric = {}".format(metric))
        metric = log_ss_ratio(small_data, centroids=centroids, clusters=clusters, wgss=wgss)
        print("LOG SS Ratio Metric = {}".format(metric))
        metric = log_ss_ratio(small_data, wgss=wgss, bgss=bgss)
        print("LOG SS Ratio Metric = {}".format(metric))
        metric = log_ss_ratio(small_data, centroids=centroids, bgss=bgss, wgss=wgss)
        print("LOG SS Ratio Metric = {}".format(metric))
        metric = log_ss_ratio(small_data, centroids=centroids, clusters=clusters, bgss=bgss, wgss=wgss)
        print("LOG SS Ratio Metric = {}".format(metric))

        metric = trace_w(small_data, centroids=centroids)
        print("Trace W Metric = {}".format(metric))
        metric = trace_w(small_data, centroids=centroids, clusters=clusters)
        print("Trace W Metric = {}".format(metric))
        metric = trace_w(small_data, clusters=clusters)
        print("Trace W Metric = {}".format(metric))
        metric = trace_w(small_data, wgss=wgss)
        print("Trace W Metric = {}".format(metric))
        metric = trace_w(small_data, centroids=centroids, wgss=wgss)
        print("Trace W Metric = {}".format(metric))
        metric = trace_w(small_data, centroids=centroids, clusters=clusters, wgss=wgss)
        print("Trace W Metric = {}".format(metric))





if __name__ == '__main__':
    main()
