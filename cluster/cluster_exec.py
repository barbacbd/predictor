import argparse
from .file import read_data
from .utils import *
from .r import ClusterCrit
import pandas as pd
from .selection import metricChoices, select as metricSelection


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
        choices=["all", "k_means", "x_bins", "e_bins", "natural_breaks", "kde"],
        default="k_means",
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


def _highlightSelections(df, selections):
    """
    Function to be applied to a row of the dataframe. For each
    Algorithm (key) Cluster (value) pair, change the color of the
    dataframe cell when it is output to excel.

    :return: Style from pandas that will be applied.
    """
    color = "background-color: yellow;"
    local_df = df.copy()
    local_df.loc[:,:] = ''

    for row, col in selections.items():
        if col is not None:
            local_df.loc[row, col] = 'background-color: yellow'

    return local_df

    
def main():
    """
    main entry point
    """
    parser = create_args()
    args = parser.parse_args()
    
    m = ClusterCrit()
    
    # graceful fail
    data_set = read_data(args.file)
    
    if data_set is None:
        print("Error reading data set.")
        exit(1)
        
    try:
        cluster_data = process_clusters(args.clusters)
    except AttributeError:
        print("ERROR check your cluster values")
        raise

    min_cluster, max_cluster = cluster_data[0], cluster_data[1]

    
    configured_funcs = configure(**vars(args))

    output_file = create_output_file(args.file)

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as w:
        for sheet_name, func in configured_funcs.items():
            excel_dict = {}
            cluster_dict = {}
            
            # Create a dataframe that will be concatenated to 
            cloned_df = None
            
            # batch these results
            for cluster in range(min_cluster, max_cluster+1):
                matching_clusters = func(data_set, cluster, **vars(args))
                fdf = m(data_set, matching_clusters, cluster)
                
                if cloned_df is None:
                    cloned_df = fdf
                else:
                    cloned_df = pd.concat([cloned_df, fdf], axis=1)
                    
                # save the result of the algorithms as well as the clusters for 
                # cluster K .
                excel_dict[cluster] = m(data_set, matching_clusters, cluster)
                cluster_dict[cluster] = matching_clusters
        
            # drop the names from the dataframe that we don't want. 
            for idx in set(cloned_df.index) - set(list(metricChoices.keys())):
                cloned_df.drop(index=idx, inplace=True)


            selections = metricSelection(cloned_df)

            # add the function type from the `metricChoices` dictionary, do a little magic for display
            cloned_df["Function"] = [y.__name__.replace("df_", "").replace("_", " ") for x,y in metricChoices.items()]

            # highlight the row/column pairs where the results were found
            cloned_df.style.apply(_highlightSelections, selections=selections, axis=None).to_excel(w, sheet_name=sheet_name)

            # write all of the cluster information to another sheet
            pd.DataFrame(cluster_dict).to_excel(w, sheet_name=sheet_name + "_clusters")


if __name__ == '__main__':
    main()

