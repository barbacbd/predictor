from os.path import exists


class Vector:

    __slots__ = [
        'x', 'y', 'z', 'w'
    ]
    
    def __init__(self, x=None, y=None, z=None, w=None):
        """
        :param x:
        :param y:
        :param z:
        :param w:
        """
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    @property
    def dimensions(self):
        """
        :return: number of dimensions that we are utilizing
        """
        index = 0
        for _s in self.__slots__[:]:
            if getattr(self, _s) is None:
                break
            index += 1
        
        return index


class DataSet:

    def __init__(self, filename, name=None, dimensions=1):
        """
        :param filename: full name of the file (including path) where the data will be stored
        :param name: [optional] name of the data set. 

        .. note::
            if the name is not present. The filename (without extension) will be the name of the dataset.
        :param dimension: Number of dimensions for the data [options = [1,2,3,4]]
        """
        if name is None:
            self._name = filename.split("/")[-1].split(".")[0]
        else:
            self._name = name

        self._filename = filename
        self._dimensions = dimensions if dimensions in (1, 2, 3, 4) else 1

        self._data = []
        
        self._read()
        
    @property
    def name(self):
        return self._name

    @property
    def filename(self):
        return self._filename

    def _read(self):
        """
        ..note:: 
            Only going to Read in Single 
        """

        temp_data = []
        leftovers = []
        
        if exists(self._filename):
            with open(self._filename) as _f:

                _line = _f.readline().strip()
                leftovers.extend([float(x) for x in _line.split() if x])

                while len(leftovers) >= self._dimensions:
                    # make a new data point from this information before reading more
                    make_into_data = leftovers[:self._dimensions]
                    self._data.append(Vector(
                        x=make_into_data[0] if self._dimensions >=1 else None,
                        y=make_into_data[1] if self._dimensions >= 2 else None,
                        z=make_into_data[2] if self._dimensions >= 3 else None,
                        w=make_into_data[3] if self._dimensions == 4 else None
                    ))
                    leftovers = leftovers[self._dimensions:]
