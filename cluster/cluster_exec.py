import argparse
from .file import read_data
from .utils import *
from .r import Metrics
import pandas as pd


def create_args():
    """
    Function to stow away the information for arguments
    
    :return: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Read in files containing data points and execute a set of metrics on the dataset."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="File that will be read in, and a dataset will be made out of the data."
             "The data should NOT include headers for rows or columns."
    )    
    parser.add_argument(
        "-k", "--clusters",
        type=int,
        nargs='+',
        help="List of the number of clusters. The first index in the list is the lower"
             " limit number of clusters, while the second is upper limit."
             " For instance: --clusters 3 10 would run the algorithm on all clusters"
             " in the range of 3 to 10."
             " <1 will be ignored and lists of length 0 are ignored, lists of length 1"
             "indicates that the upper and lower limit are the same."
    )
    parser.add_argument(
        "-c", "--clustering",
        type=str,
        choices=["all", "k_means", "x_bins", "e_bins"],
        default="all",
        help="k_means: normal k_means clustering algorithm."
             "x_bins: use K to create the number of bins spread out from max to min."
             "e_bins: even number per bin or cluster."
             "all: run all algorithms"
    )
    parser.add_argument(
        "--init",
        type=str,
        choices=['k-means++', 'random'],
        default='k-means++',
        help="When present, this option inidcates the use of kmeans vs kmeans++ (default)."
    )
    return parser

    
def main():
    """
    main entry point
    """
    parser = create_args()
    args = parser.parse_args()
    
    m = Metrics()
    
    # graceful fail
    data_set = read_data(args.file)
    
    if data_set is None:
        print("Error reading data set.")
        exit(1)
        
    try:
        cluster_data = process_clusters(args.clusters)
    except AttributeError:
        print("ERROR check your cluster values")
        exit(1)

    min_cluster, max_cluster = cluster_data[0], cluster_data[1]

    
    configured_funcs = configure(**vars(args))

    output_file = create_output_file(args.file)

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as w:
        for sheet_name, func in configured_funcs.items():
            excel_dict = {}
            cluster_dict = {}
            # batch these results
            for cluster in range(min_cluster, max_cluster+1):
                matching_clusters = func(data_set, cluster, **vars(args))
                excel_dict[cluster] = m.exec_criteria(data_set, matching_clusters, cluster)
                cluster_dict[cluster] = matching_clusters
    
            # Write the output to the excel file
            col = 0

            # write all of the metric information to the first sheet
            for sheet, data in excel_dict.items():
                data.to_excel(w, sheet_name=sheet_name, startcol=col, index=col==0)
                col = col + 1 if col > 0 else col + 2
        
            # write all of the cluster information to another sheet
            pd.DataFrame(cluster_dict).to_excel(w, sheet_name=sheet_name + "_clusters")


if __name__ == '__main__':
    main()

