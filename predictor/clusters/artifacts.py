import pandas as pd
from os.path import exists
from ..log import get_logger
from collections import defaultdict



log = get_logger()


class ClusterArtifact:
    
    def __init__(self, filename=None, *args, **kwargs):
        '''If a filename is provided, load the data in the file, otherwise
        the data that is provided via the keyword arguments are used to set
        the internal variables. 
        
        Keyword Arguements:
        
        
        :param filename: name/path of the xlsx file
        '''
        # {ClusterAlgorithm: {ClusterNumber: [ClusterNumberByDataValue]}}
        self.clusters = defaultdict(dict)
        
        # {ClusterAlgorithm: {CritAlgorithm: [CritAlgorithmScores]}
        self.cluster_crit_data = defaultdict(dict)
        
        if filename is not None and exists(filename):
            log.debug("Attempting to create artifacts from %s", filename)
            self.load_file(filename)
        else:
            # attempt to load data from the keyword args
            if "clusters" in kwargs:
                self.clusters = kwargs.get("clusters")
            
            if "cluster_crit" in kwargs:
                self.cluster_crit_data = kwargs.get("cluster_crit")
    
    def load_file(self, filename):
        '''Load the artifact data from a file. The intended file must
        be an xlsx file. The artifacts are produced from the same data that
        is created during the clustering & crit selection stage of the execution.
        
        :param filename: Name of the xlsx file 
        '''
        if not filename.endswith(".xlsx"):
            log.warning("Failed to create artifacts from %s", filename)
            return
        
        # Do not specify the sheetname (None) so that all dataframes are stored as a dict
        dfs = pd.read_excel(filename, None)
        
        for key, df in dfs.items():
            log.debug("Loaded dataframe from sheet %s", key)                        
            df.rename(columns=df.iloc[0][1:]).drop(df.index[0])
            if "_clusters" in key:
                # cut the first row since these are just the indexes
                df = df.iloc[: , 1:]
                dict_key = key.replace("_clusters", "")

                for idx, column in enumerate(df):
                    self.clusters[dict_key][idx] = df[column].tolist()
            else:
                for _, row in df.iterrows():                    
                    rowlist = row.tolist()
                    crit_algorithm = rowlist[0]
                    self.cluster_crit_data[dict_key][crit_algorithm] = rowlist[1:]
