import argparse
import logging
from inquirer import list_input, text
from os import listdir, mkdir, chdir, getcwd
from os.path import exists, join
from yaml import dump
from predictor.clusters.cluster_algorithms import ClusterAlgorithm
from predictor.config import Config
from predictor.log import get_logger
from predictor.clusters.r import CritSelection, init as rinit
from predictor.features.feature_selection import FeatureSelectionType, select_features
from predictor.clusters.generator import ClusterCreator


config_filename = "configuration.yaml"
log = None


def config(*args, **kwargs):
    '''Create the configuration file by asking for user input.
    The configuration file will be consumed by the other processes
    '''
    log.info("Executing the configuration.")
    if exists(config_filename):
        # file exists already do not do anything !
        log.debug("%s exists, using the confguration file ...", config_filename)
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
        elif num_features <= 0:
            log.error("Number of features to select must be positive.")
            num_features = 2
        num_features = min(num_features, len(feast_algorithms))
        
    except (TypeError, ValueError) as error:
        log.error(error)
        num_features = min(len(feast_algorithms), 2)
    configuration_dict["number_of_features"] = num_features
    
    with open(config_filename, 'w') as yaml_file:
        data = dump(configuration_dict, yaml_file)


def cluster(*args, **kwargs):
    '''Run the clustering algorithms'''
    log.info("Executing cluster.")
    log.debug("Setting config, parsing")
    rinit()
    config_obj = Config(config_filename)
    config_instances = config_obj.instances

    artifacts = []
    for instance in config_instances:
        instance.workup()
        artifacts.extend(instance.generate_artifacts())
    
    log.info("Created artifacts: %s", ", ".join(artifacts))
    return artifacts
    

def load_crit(*args, **kwargs):
    '''Load cluster and crit algorithm artifacts'''
    log.info("Executing load_crit.")

    if not exists(ClusterCreator.WorkupDirectory):
        log.error("Failed to find %s", ClusterCreator.WorkupDirectory)
        return
    
    artifacts = []
    dir = join(getcwd(), ClusterCreator.WorkupDirectory)
    for fname in listdir(dir):
        if fname.endswith(".json"):
            log.debug("Found %s", fname)
            
            cc = ClusterCreator()
            cc.from_json(fname)
            artifacts.append(cc)

    return artifacts

def feast(*args, **kwargs):
    '''Run the feature selection on the output of a previous step
    '''
    log.info("Executing FEAST.")
    return

    if not exists(config_filename):
        log.error("Unable to find configuration file.")
        return
    config_obj = Config(config_filename)
    
    cluster(*args, **kwargs)
    artifacts = load_crit(*args, **kwargs)
    
    feature_output = select_features(artifacts, config.selected_features)

def execute(*args, **kwargs):
    '''Run ALL of the other functions'''
    log.info("Executing execute.")
    config(*args, **kwargs)

    cluster(*args, **kwargs)

    feast(*args, **kwargs)


def main():
    '''Main entry point. The user will select the execution path
    through the argparse commands.
    '''
    global log
    
    parser = argparse.ArgumentParser(prog='cluster')
    parser.add_argument('command', help='Command to execute', 
                        choices=['config', 'cluster','feast', 'execute'])
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Log verbosity')
    parser.add_argument('-d', '--dir', default='.', help='Directory where the executable will run.')
    args = parser.parse_args()

    # verbosity starts at 10 and moves to 50
    if args.verbose > 0:
        verbosity = 50 - (10*(args.verbose-1))
    else:
        verbosity = logging.CRITICAL

    # setup the logger
    log = get_logger(verbosity)
    
    if not exists(args.dir):
        log.debug("Creating directory: %s", args.dir)
        mkdir(args.dir)
    
    log.debug("Moving to %s", args.dir)
    chdir(args.dir)
    
    globals()[args.command](args)


if __name__ == '__main__':
    main()

