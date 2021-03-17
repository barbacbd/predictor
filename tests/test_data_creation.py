from unittest import TestCase, main
from cluster.data import DataSet, Vector
from cluster.algorithm import create_centroids
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

        num_per_line = randint(0, 20)

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

    def test_2_create_centroids(self):
        """
        ..note::
        This is NOT a test right now as it does not assert anything
        """
        TestDataSetCreation.create_data_file()
        dataset = DataSet(DATA_FILE, dimensions=1)
        data = dataset.data

        centroids, seed = create_centroids(data, 2)
        for centroid in centroids:
            print(str(centroid))


if __name__ == '__main__':
    main()
