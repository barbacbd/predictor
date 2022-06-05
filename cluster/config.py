from fileinput import filename
from os.path import exists
import pandas as pd
from yaml import safe_load
from .clusters import ClusterAlgorithm
from .r import CritSelection, crit
from .file import create_output_file, read_data, highlight_selections
from .selection import MetricChoices, select as metric_selection
from .log import get_logger


log = get_logger()


def process_clusters(clusters):
    '''The min cluster numbers should be the first element and the 
    max cluster numbers should be the second element. If only one
    element exists, then the upper and lower limit are the same. 
    
    :param clusters: list of cluster values
    :return: min, max number of clustes
    '''
    if not isinstance(clusters, (list, tuple)):
        raise AttributeError

    # never be less than 0 but you never know
    if len(clusters) <= 0:
        raise AttributeError

    if len(clusters) == 1:
        return clusters[0], clusters[0]

    if clusters[0] < 1 or clusters[1] < 1:
        raise AttributeError
    return min(clusters[0], clusters[1]), max(clusters[0], clusters[1])


class ConfigInstance:
    '''A ConfigInstance is a set of data required to run a full set of
    workups using the cluster crit and cluster algorithms on a filename
    '''
    def __init__(
        self, 
        filename, 
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
                
    def workup(self):
        '''Run the workup:
        Open the file
        Create the clusters using the cluster algorithms
        Analyze the clusters using the Crit algorithms
        Output the data to an excel file
        
        :return: Name of the excel file that was created.
        '''
        log.info("Running workup on %s", self.filename)
        excel_filename = create_output_file(self.filename)

        cluster_creation_algorithm_funcs = self.provision_cluster_algorithms()

        data_set = read_data(self.filename)
        if data_set is None:
            return
        
        with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as w:
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
                    crit_output = crit(data_set, matching_clusters, cluster_num)
                
                    if cloned_df is None:
                        cloned_df = crit_output
                    else:
                        cloned_df = pd.concat([cloned_df, crit_output], axis=1)
                    
                    # save the result of the algorithms as well as the clusters for 
                    # cluster K .
                    log.debug("Crit algorithms")
                    excel_dict[cluster_num] = crit(data_set, matching_clusters, cluster_num)
                    cluster_dict[cluster_num] = matching_clusters
        
                # drop the names from the dataframe that we don't want. 
                for idx in set(cloned_df.index) - set(list(MetricChoices.keys())):
                    cloned_df.drop(index=idx, inplace=True)

                selections = metric_selection(cloned_df)

                # add the function type from the `MetricChoices` dictionary, do a little magic for display
                cloned_df["Function"] = [y.__name__.replace("df_", "").replace("_", " ") for x,y in MetricChoices.items()]

                # highlight the row/column pairs where the results were found
                cloned_df.style.apply(highlight_selections, selections=selections, axis=None).to_excel(w, sheet_name=sheet_name)

                # write all of the cluster information to another sheet
                log.info("Adding sheet %s to %s", sheet_name, self.filename)
                pd.DataFrame(cluster_dict).to_excel(w, sheet_name=sheet_name + "_clusters")


class Config:
 
    '''Configuration class to contain/parse/validate all information
    provided via the configuration file consumed by this executable
    '''
 
    min_clusters = 2
    
    def __init__(self, filename=None):
        self.max_clusters = None
        self.filenames = []
        self.cluster_algorithms = []
        self.crit_algorithms = []
        self.algorithm_extras = {}
        
        if filename is not None:
            self.consume(filename)
        
    def consume(self, filename):
        '''Attempt to set all of the internal variables for the
        configuration via the configuration file.
        
        :param filename: Path to the file to load
        '''
        with open(filename, "r") as config_file:
            yaml_data = safe_load(config_file)
        
        if "filenames" in yaml_data:
            for fname in yaml_data["filenames"]:
                if exists(fname):
                    self.filenames.append(fname)
                else:
                    log.debug("%s does not exist, skipping config", fname)
        
        if "max_number_of_clusters" in yaml_data:
            try:
                _, self.max_clusters = process_clusters(
                    (Config.min_clusters, int(yaml_data["max_number_of_clusters"])))
            except ValueError as error:
                log.debug(error)
        
        if "cluster_algorithms" in yaml_data:
            for cluster_algorithm in yaml_data["cluster_algorithms"]:
                try:
                    self.cluster_algorithms.append(ClusterAlgorithm[cluster_algorithm])
                except ValueError as error:
                    log.debug(error)
                            
        if "crit_algorithms" in yaml_data:
            for crit_algorithm_type in yaml_data["crit_algorithms"]:
                try:
                    self.crit_algorithms.append(CritSelection[crit_algorithm_type])
                except ValueError as error:
                    log.debug(error)
                    
        if "algorithm_settings" in yaml_data:
            self.algorithm_extras["init"] = yaml_data["algorithm_settings"]
            
    @property
    def cluster_sizes(self):
        '''Get the max and min cluster sizes
        
        :return: Min, Max cluster sizes
        '''
        return self.min_clusters, self.max_clusters
    
    @property
    def instances(self):
        '''Create a set of instances 
        
        :return: Set of instances 
        '''
        return [
            ConfigInstance(
                fname, 
                self.cluster_algorithms, 
                self.crit_algorithms, 
                self.min_clusters, 
                self.max_clusters,
                self.algorithm_extras
            ) for fname in self.filenames
        ]
