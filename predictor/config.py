from os.path import exists
from yaml import safe_load
from .clusters.cluster_algorithms import ClusterAlgorithm
from .log import get_logger
from .clusters.r import CritSelection
from .features.feature_selection import FeatureSelectionType
from .clusters.generator import ClusterCreator


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


class Config:
 
    '''Configuration class to contain/parse/validate all information
    provided via the configuration file consumed by this executable
    '''
 
    min_clusters = 2
    
    def __init__(self, filename=None):
        self.max_clusters = Config.min_clusters
        self.filenames = []
        self.cluster_algorithms = []
        self.crit_algorithms = []
        self.algorithm_extras = {}
        self.selected_features = []
        
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
            
            if not isinstance(yaml_data["filenames"], list):
                filenames = [yaml_data["filenames"]]
            else:
                filenames = yaml_data["filenames"]
            
            for fname in filenames:
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
        
        # grab all extra data
        self.algorithm_extras = yaml_data.get("extras", {})
        
        if "selected_features" in yaml_data:
            for feature_type in yaml_data["selected_features"]:
                try:
                    self.selected_features.append(FeatureSelectionType[feature_type])
                except ValueError as error:
                    log.debug(error)
        
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
            ClusterCreator(
                fname, 
                self.cluster_algorithms, 
                self.crit_algorithms, 
                self.min_clusters, 
                self.max_clusters,
                self.algorithm_extras
            ) for fname in self.filenames
        ]
