from os.path import exists
from yaml import safe_load, dump
from inquirer import list_input, text
from os import listdir, getcwd
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
    output_filename = "configuration.yaml"
    
    def __init__(self, filename=None):
        self.max_clusters = Config.min_clusters
        self.filenames = []
        self.cluster_algorithms = []
        self.crit_algorithms = []
        self.algorithm_extras = {}
        self.number_of_features = 0
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

        self.number_of_features = yaml_data.get("number_of_features", self.number_of_features)
        if "selected_features" in yaml_data:
            for feature_type in yaml_data["selected_features"]:
                try:
                    self.selected_features.append(FeatureSelectionType[feature_type])
                except ValueError as error:
                    log.debug(error)
    
    def produce(self):
        '''Produce the questions/input for the user durng the configuration
        step of the executable.'''
        if exists(Config.output_filename):
            # file exists already do not do anything !
            log.debug("%s exists, using the confguration file ...", Config.output_filename)
            return
    
        configuration_dict = {}
        configuration_dict["extras"] = {}

        # the configuration will only allow a user to add one filename
        # but if the user edits the file manually, more than one can be added
        text_files_found = []
        for fname in listdir(getcwd()):
            if fname.endswith(".txt"):
                text_files_found.append(fname.split("/")[-1])
        
        filename = ""
        if text_files_found:
            if len(text_files_found) > 1:
                text_files_found.insert(0, "ALL")
            filename = list_input(message='Filename(s)', choices=text_files_found)
            if filename == "ALL":
                filename = text_files_found[1:]
            configuration_dict['filenames'] = filename

        # The number of clusters will be 2 - N
        number_of_clusters = text(message='Number of clusters')
        try:
            configuration_dict['max_number_of_clusters'] = int(number_of_clusters)
        except (TypeError, ValueError) as error:
            log.debug(error)
            configuration_dict['max_number_of_clusters'] = 10

        cluster_types = {x: str(x.name) for x in ClusterAlgorithm}
        cluster_algorithm = list_input(
            message='Select the cluster algorithm',
            choices=list(cluster_types.values())
        )

        kmeans_type = None
        if cluster_algorithm in (ClusterAlgorithm.ALL.name, ClusterAlgorithm.K_MEANS.name):
            kmeans_type = list_input(message='kmeans usage', choices=['k-means++', 'random'])
            configuration_dict["extras"]['init'] = kmeans_type
        
        if cluster_algorithm == ClusterAlgorithm.ALL.name:
            cluster_algorithm = [x for x in cluster_types.values() if x != cluster_algorithm]
        else:
            cluster_algorithm = [cluster_algorithm]

        # configuration will create as a list, even for a single entry to allow
        # additional after configuration
        configuration_dict['cluster_algorithms'] = cluster_algorithm
        
        cluster_crit_data = {x: str(x.name) for x in CritSelection}
        crit_algorithms = list_input(
            message='Slect the cluster crit algorithm(s)',
            choices=list(cluster_crit_data.values())
        )
        if crit_algorithms == CritSelection.ALL.name:
            crit_algorithms = [x for x in cluster_crit_data.values() if x != crit_algorithms]
        else:
            crit_algorithms = [crit_algorithms]

        # configuration will create as a list, even for a single entry to allow
        # additional after configuration
        configuration_dict['crit_algorithms'] = crit_algorithms
        
        feast_type = {x: str(x.name) for x in FeatureSelectionType}
        feast_algorithms = list_input(
            message='Select the feature selection algorithm(s)',
            choices=list(feast_type.values())
        )
        
        # dynamic values to be input in the event that BetaGamma is selected
        if feast_algorithms in (
            FeatureSelectionType.ALL.name,
            FeatureSelectionType.BetaGamma.name,
            FeatureSelectionType.discBetaGamma.name
        ):
            def beta_gamma(var):        
                _var = text(message=f'{var} [0.0, 1.0]')
                try:
                    _var = float(_var)
                    if 0.0 > _var > 1.0:
                        log.warning("%s out of bounds: %f, setting to 1.0", var, _var)
                        _var = 1.0
                    
                except (TypeError, ValueError) as error:
                    log.error(error)
                    _var = 1.0
                return _var
                
            configuration_dict["extras"]['beta'] = beta_gamma("beta")
            configuration_dict["extras"]['gamma'] = beta_gamma("gamma")
    
        if feast_algorithms == FeatureSelectionType.ALL.name:
            feast_algorithms = [x for x in feast_type.values() if x != feast_algorithms]
        else:
            feast_algorithms = [feast_algorithms]

        configuration_dict["selected_features"] = feast_algorithms

        num_features = text(message='Number of features to select')
        try:
            num_features = int(num_features)
            if num_features > len(feast_algorithms):
                log.error("Number of features to select is greater than the number of feast algorithms.")
                num_features = 2
            elif num_features <= 0:
                log.error("Number of features to select must be positive.")
                num_features = 2
            num_features = min(num_features, len(feast_algorithms))
            
        except (TypeError, ValueError) as error:
            log.error(error)
            num_features = min(len(feast_algorithms), 2)
        configuration_dict["number_of_features"] = num_features
        
        with open(Config.output_filename, 'w') as yaml_file:
            data = dump(configuration_dict, yaml_file)
    
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
