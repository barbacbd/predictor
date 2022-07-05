import argparse
import logging
from os import listdir, mkdir, chdir, getcwd
from os.path import exists, join
from predictor.config import Config
from predictor.log import get_logger
from predictor.clusters.r import init as rinit
from predictor.features.feature_selection import select_features
from predictor.clusters.generator import ClusterCreator


log = None


def config(*args, **kwargs):
    '''Create the configuration file by asking for user input.
    The configuration file will be consumed by the other processes
    '''
    log.info("Executing the configuration.")
    c = Config()
    c.produce()


def cluster(*args, **kwargs):
    '''Run the clustering algorithms'''
    log.info("Executing cluster.")
    log.debug("Setting config, parsing")
    rinit()
    config_obj = Config(Config.output_filename)
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

