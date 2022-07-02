from codecs import open as copen
from numpy import loadtxt
from .log import get_logger


log = get_logger()


def create_output_file(filename, extension):
    '''Provide the original filename and convert the name to 
    use the extension provided. The filename will be local (no 
    longer include the full path).

    :param filename: input file name
    :param extension: new extension for the filename
    :return: output filename
    '''
    if not filename:
        log.error("Bad Filename: %s")
        return None

    if not extension:
        log.error("Bad extension: %s")
        return None
    
    split_fname = filename.split("/")[-1].split(".")
    return ".".join(split_fname[:len(split_fname)-1] + [extension])


def read_data(filename):
    '''Attempt to read the data file into a pandas Dataframe. The 
    following encodings are considered valid: UTF-8, UTF-16,
    ascii
    
    :param filename: name (including path) to the file
    :return: pandas DataFrame on success, None otherwise
    '''

    data = None
    encodings = ('UTF-8', 'UTF-16', 'ascii')
    
    for enc in encodings:
        with copen(filename, encoding=enc) as f:
            try:
                data = loadtxt(f)
                break
            except UnicodeDecodeError:
                continue

    if data is not None:
        try:
            num_rows, num_cols = data.shape
        except ValueError as e:
            # Indicates that there was a bad number of columns (probably empty)                                                                                                                                 
            # A 1-D array was created, and it must be reshaped for proper use later.                                                                                                                            
            data = data.reshape(-1, 1)

    return data


def highlight_selections(df, selections):
    '''Function to be applied to a row of the dataframe. For each
    Algorithm (key) Cluster (value) pair, change the color of the
    dataframe cell when it is output to excel.

    :param df: Dataframe
    :param selections:
    :return: Style from pandas that will be applied.
    '''
    color = "background-color: yellow;"
    local_df = df.copy()
    local_df.loc[:,:] = ''

    for row, col in selections.items():
        if col is not None:
            local_df.loc[row, col] = 'background-color: yellow'

    return local_df
