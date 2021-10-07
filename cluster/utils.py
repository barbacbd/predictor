from .clusters import *


def create_output_file(filename):
    """
    Given the original filename, create the output excel filename.
    
    :param filename: input file name 
    :return: output filename
    """
    # find just the filename
    fn = filename.split("/")[-1]
    
    # remove the extension
    fn = fn.split(".")
    if len(fn) > 1:
        fn = fn[0]
        
    # returning the excel spreadsheet name
    return fn + "_analysis.xlsx"


def process_clusters(clusters):
    """
    The min cluster numbers should be the first element and the 
    max cluster numbers should be the second element. If only one
    element exists, then the upper and lower limit are the same. 
    
    :param clusters: list of cluster values
    """
    if not isinstance(clusters, list):
        raise AttributeError
    
    # never be less than 0 but you never know
    if len(clusters) <= 0:
        raise AttributeError

    if len(clusters) == 1:
        return clusters[0], clusters[0]
    else:
        if clusters[0] < 1 or clusters[1] < 1:
            raise AttributeError
        return min(clusters[0], clusters[1]), max(clusters[0], clusters[1])
        

def configure(**kwargs):
    
    funcs = {}
    clustering = kwargs.get("clustering", None)
    
    if clustering is not None:
        
        if clustering in ("all", "k_means"):
            funcs["k_means"] = k_means_wrapper
            
        if clustering in ("all", "x_bins"):
            funcs["x_bins"] = x_bins
        
        if clustering in ("all", "e_bins"):
            funcs["e_bins"] = e_bins

    return funcs