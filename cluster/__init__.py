from os import path
from ._io import read_data_file

# Provide the user with Version information about the data.
# Not a traditional approach, but the same information is
# provided with python -pip information
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'VERSION'), encoding='utf-8') as f:
    __version__ = f.read()

# Expose all of the functions and classes to the public
__all__ = [
    'read_data_file'
]
