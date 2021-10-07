from codecs import open as copen
from numpy import loadtxt


def read_data(filename):
    """
    Attempt to read the data file into a pandas Dataframe.
    
    Attempting to decode with encoding:
        UTF-8
        UTF-16
        ascii
    
    :param filename: name (including path) to the file
    :return: pandas DataFrame on success, None otherwise
    """

    data = None
    encodings = ('UTF-8', 'UTF-16', 'ascii')
    
    for enc in encodings:
        if data is not None:
            break
        
        with copen(filename, encoding=enc) as f:
            try:
                data = loadtxt(f)
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