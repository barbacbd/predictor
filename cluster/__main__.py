from inquirer import prompt, list_input, text
import argparse
from yaml import dump
from os.path import exists
from cluster.r import CritSelection
from cluster.clusters import ClusterAlgorithm
from cluster.config import Config
from multiprocessing import Process
from cluster.log import get_logger
import logging


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

    # the configuration will only allow a user to add one filename
    # but if the user edits the file manually, more than one can be added
    configuration_dict['filenames'] = []
    filename = text(message='Path to file')
    configuration_dict['filenames'].append(filename)

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
        configuration_dict['algorithm_settings'] = kmeans_type
    
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
    
    with open(config_filename, 'w') as yaml_file:
        data = dump(configuration_dict, yaml_file)


def feast(*args, **kwargs):
    '''Run the feature selection on the output of a previous step
    '''
    log.info("Executing FEAST.")



def execute(*args, **kwargs):
    '''Run ALL of the other functions'''
    log.info("Executing execute.")
    config(*args, **kwargs)

    log.debug("Setting config, parsing")
    config_obj = Config(config_filename)
    config_instances = config_obj.instances

    processes = []
    log.info("Creating %d processes to run workup ...", len(config_instances))
    for instance in config_instances:
        processes.append(Process(target=instance.workup))

    log.info("Starting %d processes ...", len(config_instances))
    for process in processes:
        process.start()


def main():
    '''Main entry point. The user will select the execution path
    through the argparse commands.
    '''
    global log
    
    parser = argparse.ArgumentParser(prog='cluster')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    config = subparsers.add_parser('config', help="Create the configuration file")
    config.add_argument('-v', '--verbose', action='count', default=0, help='Log verbosity')
    
    feast = subparsers.add_parser('feast', help="Feature Selection")
    feast.add_argument('-v', '--verbose', action='count', default=0, help='Log verbosity')
        
    execute = subparsers.add_parser('execute',help="Execute all stages")
    execute.add_argument('-v', '--verbose', action='count', default=0, help='Log verbosity')

    args = parser.parse_args()

    # verbosity starts at 10 and moves to 50
    if args.verbose > 0:
        verbosity = 50 - (10*(args.verbose-1))
    else:
        verbosity = logging.CRITICAL

    # setup the logger
    log = get_logger(verbosity)
        
    globals()[args.command](args)


if __name__ == '__main__':
    main()

