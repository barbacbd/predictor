def df_min_diff(row):
    """
    The function is applied to columns start + 1 - n

    For instance columns 2 to 50 would apply the data to 

    3 - 50 as the function is the minimum difference 
    between columns n and n-1 for the row.

    :param df: Pandas Dataframe row
    :return: Column number where the value contains the min difference
    """
    local_min_idx = None
    local_min_value = None

    for i in range(1, len(row.values.tolist()), 1):
        if local_min_value is None or row[i] - row[i-1] < local_min_value:
            local_min_idx = i

    return local_min_idx  # column containing min diff

def df_max_diff(row):
    """
    The function is applied to columns start + 1 - n

    For instance columns 2 to 50 would apply the data to 

    3 - 50 as the function is the maximum difference 
    between columns n and n-1 for the row.

    :param df: Pandas Dataframe row
    :return: Column number where the value contains the max difference
    """
    local_max_idx = None
    local_max_value = None

    for i in range(1, len(row.values.tolist()), 1):
        if local_max_value is None or row[i] - row[i-1] > local_max_value:
            local_max_idx = i

    return local_max_idx  # column containing max diff

def df_min(row):
    """
    :param row: Pandas dataframe row
    :return: column name of the min value in the row 
    """
    return row.idxmin()

def df_max(row):
    """
    :poaram row: Pandas dataframe row
    :return: Column name of the max value in the row
    """
    return row.idxmax()

# The dictionary of Algorithms with the name/kind of function
# that should be applied to the entire set of outcomes for 
# clusters k (Ex: k = 2 ... 50)
metricChoices = {
    "Ball_Hall": df_max_diff,
    "Banfeld_Raftery": df_min,
    "C_index": df_min,
    "Calinski_Harabasz": df_max,
    "Davies_Bouldin": df_min,
    "Det_Ratio": df_min_diff,
    "Dunn": df_max,
    # "GDI": df_max,
    "Gamma": df_max,
    "G_plus": df_min,
    "Ksq_DetW": df_max_diff,
    "Log_Det_Ratio": df_min_diff,
    "Log_SS_Ratio": df_min_diff,
    "McClain_Rao": df_min,
    "PBM": df_max,
    # "Point_biserial": df_max,
    "Ratkowsky_Lance": df_max,
    "Ray_Turi": df_min,
    "Scott_Symons": df_min,
    # "SD": df_min,
    "S_Dbw": df_min,
    "Silhouette": df_max,
    "Tau": df_max,
    "Trace_W": df_max_diff,
    "Trace_WiB": df_max_diff,
    "Wemmert_Gancarski": df_max,
    "Xie_Beni": df_min
}


def select(df):
    """
    For each algorithm in `metricChoices` run the function
    that should be applied for the algorithm on the row in the dataframe.
    The column that is the result of the function is saved and the 
    dictionary of the algorithm with the column name (cluster) is returned.

    :param df: Pandas dataframe containing the metrics as the index from the 
    `metricChoices`.

    :return: dictionary of algorithms (key) to their resulting column (cluster). 
    It is possible for `None` to be in the resultant value field.
    """
    # result 
    selections = {}

    # create a reference list of all column names to be looked
    # up later (this isn't required, but it makes it easier for later)
    ref_cols = df.columns.values.tolist()

    for idx, row in df.iterrows():

        # Get the function associated with the row (algorithm)
        # if this is a function and not some mistake, run the function
        # and store the result.
        func = metricChoices.get(idx, None)

        if callable(func):
            ret = func(row)

            # get the column name as the max diff and min diff functions return 
            # integers instead of column names. Turn it into a column name
            if isinstance(ret, int):
                ret = ref_cols[ret]

            selections[idx] = ret
        else:
            selections[idx] = None
    
    return selections