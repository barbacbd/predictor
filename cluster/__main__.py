from inquirer import prompt, list_input, text
import argparse
from yaml import dump
from os.path import exists
from r import CritSelection



def config(*args, **kwargs):
    '''Create the configuration file by asking for user input.
    The configuration file will be consumed by the other processes
    '''
    if exists('configuration.yaml'):
        # file exists already do not do anything !
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
        # log.debug(error)
        configuration_dict['max_number_of_clusters'] = 10

    cluster_types = ["k_means", "x_bins", "e_bins", "natural_breaks", "kde"]
    cluster_algorithm = list_input(
        message='Select the cluster algorithm',
        choices=["All"] + cluster_types
    )

    kmeans_type = None
    if cluster_algorithm in ('k_means', 'All'):
        kmeans_type = list_input(message='kmeans usage', choices=['k-means++', 'random'])
        configuration_dict['algorithm_settings'] = kmeans_type
    
    if cluster_algorithm == "All":
        cluster_algorithm = cluster_types
    else:
        cluster_algorithm = [cluster_algorithm]

    # configuration will create as a list, even for a single entry to allow
    # additional after configuration
    configuration_dict['cluster_algorithms'] = cluster_algorithm
    
    cluster_crit_data = {x: str(x.name).replace("_", " ") for x in CritSelection}
    crit_algorithms = list_input(
        message='Slect the cluster crit algorithm(s)',
        choices=list(cluster_crit_data.values())
    )
    if crit_algorithms == "ALL":
        crit_algorithms = [x for x in cluster_crit_data.values() if x != crit_algorithms]
    else:
        crit_algorithms = [crit_algorithms]

    # configuration will create as a list, even for a single entry to allow
    # additional after configuration
    configuration_dict['crit_algorithms'] = crit_algorithms
    
    with open('configuration.yaml', 'w') as yaml_file:
        data = dump(configuration_dict, yaml_file)


def feast(*args, **kwargs):
    '''Run the feature selection on the output of a previous step
    '''



def execute(*args, **kwargs):
    '''Run ALL of the other functions'''
    config(*args, **kwargs)
    
        

def main():
    '''Main entry point. The user will select the execution path
    through the argparse commands.
    '''
    parser = argparse.ArgumentParser(prog='docu')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    config = subparsers.add_parser(
        'config',
        help="Create the configuration file"
    )
    
    feast = subparsers.add_parser(
        'feast',
        help="Feature Selection"
    )
    execute = subparsers.add_parser(
        'execute',
        help="Execute all stages"
    )

    args = parser.parse_args()

    globals()[args.command](args)


if __name__ == '__main__':
    main()

