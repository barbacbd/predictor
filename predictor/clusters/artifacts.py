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
        :paramdata_frames: Dictionary of data_frames where the key is the name         
        
        :param filename: name/path of the xlsx file
        '''
        # {ClusterAlgorithm: {ClusterNumber: [ClusterNumberByDataValue]}}
        self.clusters = defaultdict(dict)
        
        # {ClusterAlgorithm: {CritAlgorithm: [CritAlgorithmScores]}
        self.cluster_crit_data = defaultdict(dict)
        
        self.data_frames = {}
        
        if filename is not None and exists(filename):
            log.debug("Attempting to create artifacts from %s", filename)
            self.name = filename
            self.load_file(filename)
        else:
            if "data_frames" in kwargs:
                self.data_frames = kwargs.get("data_frames")
                self.load_from_dfs()
            self.name = str(id(self))
        log.info("Set name of artifact to %s", self.name)
    
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
        self.data_frames = pd.read_excel(filename, None)
        self.load_from_dfs()
        
    def load_from_dfs(self):
        '''Load the cluster and crit information from the dataframes
        '''
        for key, df in self.data_frames.items():
            log.debug("Loading dataframe %s", key)                        
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

    @property
    def df_names(self):
        '''Returns all dataframe names'''
        return list(self.data_frames.keys())
    
    def get_df_data(self, df_name):
        '''Get the set of data (excluding headers) for the dataframe matching the name `df_name`
        
        ..Note:: Dataframes containing crit algorithms are transposed, so that the columns contain
        the crit algorithm information and the rows are the number of clusters
        
        :param df_name: Name of the dataframe to get the information from
        :return: NxM Nd-array of the dataset without the headers
        '''
        if df_name not in self.data_frames:
            log.warning("Failed to get data, no matching dataframe %s", df_name)
            return None
        
        df = self.data_frames[df_name]
        
        if "_clusters" not in df_name:
            df = df.transpose()
        
        # TODO Convert here
        
    def get_df_labels(self, df_name):
        '''Get the labels of the data set for the dataframe matching the name `df_name`
        
        ..Note:: Dataframes containing crit algorithms are transposed, so that the columns contain
        the crit algorithm information and the rows are the number of clusters
        
        :param df_name: Name of the dataframe to generate the regression target from
        :return: [N,] Nd-Array for the regression target of the dataframe
        '''
        if df_name not in self.data_frames:
            log.warning("Failed to generate labels, no matching dataframe %s", df_name)
            return None
        
        df = self.data_frames[df_name]
        
        if "_clusters" not in df_name:
            df = df.transpose()
        
        # TODO Generate here