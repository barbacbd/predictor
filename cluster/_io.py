from numpy import loadtxt


def read_data_file(filename, delimiter=' ', num_columns=1):
    """
    Positional Arguments
       : :param filename: Name of the file to read from.

    Optional Arguments
      : :param delimiter: Delimiter that separates the values in the file. The same delimiter
        should be used in the file.
      : :param num_columns: Number of columns to separate the data by. All values in the file
        are assumed to be floating point numbers.

    :return: N-D Array
    """
    if num_columns > 1:
        nd_arr = loadtxt(filename, delimiter=delimiter, dtype={'formats': (float,) * num_columns})
    elif num_columns == 1:
        nd_arr = loadtxt(filename, delimiter=delimiter)
    else:
        raise ValueError

    try:
        num_rows, num_cols = nd_arr.shape
    except ValueError as e:
        # Indicates that there was a bad number of columns (probably empty)
        # A 1-D array was created, and it must be reshaped for proper use later.
        nd_arr = nd_arr.reshape(-1, 1)

    return nd_arr