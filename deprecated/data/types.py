from os.path import exists
from math import sqrt
from copy import deepcopy


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

    def __iter__(self):
        for var in self.__slots__:
            yield var

    def __str__(self):

        data = {sl: getattr(self, sl) for sl in self.__slots__ if getattr(self, sl) is not None}
        return " ".join(["{} = {}".format(x, y) for x, y in data.items()])

    def __add__(self, other):
        """
        Add two Vectors together
        """
        if self.dimensions != other.dimensions:
            return None

        result = Vector()
        for var in self.__slots__:
            if getattr(self, var, None) is not None and getattr(other, var, None) is not None:
                setattr(result, var, getattr(self, var) + getattr(other, var))

        return result

    def __sub__(self, other):
        """
        Subtract one vector components from another
        """
        if self.dimensions != other.dimensions:
            return None

        result = Vector()
        for var in self.__slots__:
            if getattr(self, var, None) is not None and getattr(other, var, None) is not None:
                setattr(result, var, getattr(self, var) - getattr(other, var))

        return result

    def __mul__(self, other):
        """
        Multiply the two vectors together
        """
        if self.dimensions != other.dimensions:
            return None

        result = Vector()
        for var in self.__slots__:
            if getattr(self, var, None) is not None and getattr(other, var, None) is not None:
                setattr(result, var, getattr(self, var) * getattr(other, var))

        return result

    def __truediv__(self, other):
        """
        Divide the two vector components
        """
        if self.dimensions != other.dimensions:
            return None

        result = Vector()
        for var in self.__slots__:
            if getattr(self, var, None) is not None and getattr(other, var, None) is not None:
                setattr(result, var, getattr(self, var) / getattr(other, var))

        return result

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

    def distance(self, other):
        """
        :param other:
        :return:
        """
        if isinstance(other, Vector) and self.dimensions == other.dimensions:
            sum = 0
            for var in self.__slots__:
                if getattr(self, var) is not None and getattr(other, var) is not None:
                    sum += (getattr(self, var) - getattr(other, var))**2

            return sqrt(sum)


class DataSet:

    def __init__(self, filename, name=None, dimensions=1):
        """
        :param filename: full name of the file (including path) where the data will be stored
        :param name: [optional] name of the data set. 

        .. note::
            if the name is not present. The filename (without extension) will be the name of the dataset.
        :param dimensions: Number of dimensions for the data [options = [1,2,3,4]]
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

    @property
    def data(self):
        return deepcopy(self._data)

    def _read(self):
        """
        ..note:: 
            Only going to Read in Single 
        """
        leftovers = []
        
        if exists(self._filename):
            with open(self._filename) as _f:

                for _, line in enumerate(_f):
                    _line = line.strip()
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
