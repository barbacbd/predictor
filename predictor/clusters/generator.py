from os import mkdir
from os.path import exists, join
import pandas as pd
from .cluster_algorithms import ClusterAlgorithm
from ..file import create_output_file, read_data, highlight_selections
from ..log import get_logger
from .r import CritSelection, crit
from .selection import select as metric_selection
from json import dump, load


log = get_logger()


class ClusterCreator:
    '''A ClusterCreator is a set of data required to run a full set of
    workups using the cluster crit and cluster algorithms on a filename
    '''
    
    WorkupDirectory = "cluster_results"
    
    def __init__(
        self, 
        filename=None, 
        cluster_algorithms=[], 
        crit_algorithms=[], 
        min_clusters=0, 
        max_clusters=50,
        algorithm_extras={}
    ):
        '''Initialize the Instance, but allow the variables to be set later
        as they remain public.
        
        :param filename: Name of the file that should have the workups run against it
        :param cluster_algorithms: List of algorithm types to be used for cluster creation
        :param crit_algorithms: List of cluster crit algorithms to be used for analyzing clusters
        :param min_clusters: Minimum cluster numbers to be generated
        :param max_clusters: Maximum cluster numbers to be generated
        :param algorithm_extras: Dictionary of name and extra values applied to cluster algorithms
        '''
        self.filename = filename
        self.cluster_algorithms = cluster_algorithms
        self.crit_algorithms = crit_algorithms
        self.algorithm_extras = algorithm_extras
        self.min_clusters = min_clusters
        self.max_clusters = max_clusters

        self.selections = {}
        self.dataframes = {}

    def provision_cluster_algorithms(self):
        '''Provision a dictionary containing the cluster algorithm name 
        with the cluster algorithm type
        '''
        cluster_creation_algorithm_funcs = {}
        for cluster_algorithm in self.cluster_algorithms:
            funcs = ClusterAlgorithm.list_functions(cluster_algorithm)
            if len(funcs) > 1:
                log.warning("Too many functions returned for %s", cluster_algorithm.name)
            elif len(funcs) == 0:
                log.warning("No functions returned for %s", cluster_algorithm.name)
            else:
                cluster_creation_algorithm_funcs[cluster_algorithm.name] = funcs[0]

        return cluster_creation_algorithm_funcs
    
    def generate_artifacts(self, generate_excel=True, generate_json=True):
        '''Generate the artifacts. This should only be executed after a workup.
        
        :param generate_excel: When True, generate a single excel file
        :param generate_json: When True, generate a single json file
        :return: List of the artifacts that were generated
        '''
        artifact_names = []
        if generate_excel:
            artifact_names.append(self.generate_excel())
        if generate_json:
            artifact_names.append(self.generate_json())
            
        return artifact_names

    def generate_excel(self):
        '''Generate the excel artifacts from the saved dataframes.
        This file is generally used for analysis purposes only.
        '''
        if not exists(ClusterCreator.WorkupDirectory):
            log.debug("Creating directory: %s", ClusterCreator.WorkupDirectory)
            mkdir(ClusterCreator.WorkupDirectory)        
        excel_filename = join(ClusterCreator.WorkupDirectory, create_output_file(self.filename, "xlsx"))
        log.info("Saving xlsx artifact(s) to %s", excel_filename)

        with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as w:
            for title, df in self.dataframes.items():
                log.info("Adding sheet %s to %s", title, excel_filename)
                if "_clusters" not in title:
                    df.style.apply(
                        highlight_selections, selections=self.selections[title], axis=None
                    ).to_excel(w, sheet_name=title)
                else:
                    df.to_excel(w, sheet_name=title)

        return excel_filename        
    
    def generate_json(self):
        '''Generate the json artifacts from the saved dataframes'''
        if not exists(ClusterCreator.WorkupDirectory):
            log.debug("Creating directory: %s", ClusterCreator.WorkupDirectory)
            mkdir(ClusterCreator.WorkupDirectory)        
        json_filename = join(ClusterCreator.WorkupDirectory, create_output_file(self.filename, "json"))
        log.info("Saving json artifact(s) to %s", json_filename)

        jdict = {
            "filename": self.filename,
            "clusters": {
                "min": self.min_clusters,
                "max": self.max_clusters
            },
            "cluster_algorithms": [x.name for x in self.cluster_algorithms],
            "crit_algorithms": [x.name for x in self.crit_algorithms],
            "algorithm_extras": self.algorithm_extras,
            "dataframes": {},
            "selections": self.selections
        }
        for title, df in self.dataframes.items():
            jdict["dataframes"][title] = df.to_json()
    
        with open(json_filename, "w+") as jfile:
            dump(jdict, jfile, indent=4)
            
        return json_filename
    
    def from_json(self, filename):
        '''Load the cluster and crit information from a json file'''
        if not exists(filename):
            log.error('Failed to create %s from json file %s', self.__class__.__name__, filename)
            return 
        
        with open(filename, "rb") as jfile:
            jdata = load(jfile.read())
        
        if not jdata:
            log.error('Failed to read json data from %s', filename)
            return
                
        if "filename" in jdata:
            self.filename = jdata["filename"]
        
        if "clusters" in jdata:
            if "min" in jdata["clusters"]:
                self.min_clusters = jdata["clusters"]["min"]
            if "max" in jdata["clusters"]:
                self.max_clusters = jdata["clusters"]["max"]
        
        if "cluster_algorithms" in jdata:
            for cg in jdata["cluster_algorithms"]:
                self.cluster_algorithms.append(ClusterAlgorithm[cg])
        
        if "crit_algorithms" in jdata:
            for ca in jdata["crit_algorithms"]:
                self.crit_algorithms.append(CritSelection[ca])
        
        if "algorithm_extras" in jdata:
            self.algorithm_extras = jdata["algorithm_extras"]
        
        if "selections" in jdata:
            self.selections = jdata["selections"]
        
        if "dataframes" in jdata:
            for title, df_json in jdata["dataframes"].items():
                # TODO: do we need to add orient='index'
                self.dataframes[title] = pd.DataFrame.from_dict(df_json)
    
    def workup(self):
        '''Run the workup:
        Open the file
        Create the clusters using the cluster algorithms
        Analyze the clusters using the Crit algorithms
        '''
        log.info("Running workup on %s", self.filename)
        
        cluster_creation_algorithm_funcs = self.provision_cluster_algorithms()

        data_set = read_data(self.filename)
        if data_set is None:
            log.error("Workup failed, no data set found ...")
            return

        crit_algorithm_names = [x.name for x in self.crit_algorithms]
        
        # each sheet in the file will be named for the type of cluster algorithm
        for sheet_name, func in cluster_creation_algorithm_funcs.items():
            log.debug("Executing %s for %s", sheet_name, self.filename)
            excel_dict = {}
            cluster_dict = {}

            # Create a dataframe that will be concatenated to 
            cloned_df = None
        
            # batch these results
            for cluster_num in range(self.min_clusters, self.max_clusters+1):
                log.debug("Creating %d clusters, executing %s for %s", cluster_num, sheet_name, self.filename)
                matching_clusters = func(data_set, cluster_num, **self.algorithm_extras)
                crit_output = crit(data_set, matching_clusters, crit_algorithm_names, cluster_num)
            
                if cloned_df is None:
                    cloned_df = crit_output
                else:
                    cloned_df = pd.concat([cloned_df, crit_output], axis=1)
                
                # save the result of the algorithms as well as the clusters for 
                # cluster K .
                # excel_dict[cluster_num] = crit(data_set, matching_clusters, self.crit_algorithms, cluster_num)
                excel_dict[cluster_num] = crit_output
                cluster_dict[cluster_num] = matching_clusters
    
            # drop the names from the dataframe that we don't want. 
            for idx in set(cloned_df.index) - set(self.crit_algorithms):
                cloned_df.drop(index=idx, inplace=True)

            log.debug("Saving selection for %s", sheet_name)
            self.selections[sheet_name] = metric_selection(cloned_df)
            
            log.debug("Saving dataframes for %s", sheet_name)
            cluster_sheet_name = sheet_name + "_clusters"
            self.dataframes[sheet_name] = cloned_df
            self.dataframes[cluster_sheet_name] = pd.DataFrame(cluster_dict)
