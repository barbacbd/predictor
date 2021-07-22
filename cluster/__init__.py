from os import path
from ._io import read_data_file
from multiprocessing import cpu_count

# Provide the user with Version information about the data.
# Not a traditional approach, but the same information is
# provided with python -pip information
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'VERSION'), encoding='utf-8') as f:
    __version__ = f.read()


# The max RECOMMENDED thread count will be 2 * number of cpu cores - 1
__MAX_THREADS = 2 * cpu_count() - 1

# Expose all of the functions and classes to the public
__all__ = [
    'read_data_file'
]
