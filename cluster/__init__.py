from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'VERSION'), encoding='utf-8') as f:
    __version__ = f.read()


from multiprocessing import cpu_count
# The max RECOMMENDED thread count will be 2 * number of cpu cores - 1
__MAX_THREADS = 2 * cpu_count() - 1
