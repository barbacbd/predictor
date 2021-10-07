from rpy2 import robjects
from rpy2.robjects.vectors import FloatVector
from rpy2.robjects.packages import importr, isinstalled
from rpy2.robjects import numpy2ri
from rpy2.robjects.vectors import StrVector
import pandas as pd

# should this be a singleton ? Ehh probably that way its not constantly loading data


class Metrics:

    def __init__(self):
        """
        
        """
        self.rFunc = None  # callable R function 
        
        self._load()

    def _load(self):
        """
        Load the R modules and setup the environment for this script
        """
        # R's utility package
        utils = importr('utils')
        utils.chooseCRANmirror(ind=1)
        
        # R package names
        packnames = ('clusterCrit',)
            
        names_to_install = [x for x in packnames if not isinstalled(x)]
        if len(names_to_install) > 0:
            utils.install_packages(StrVector(names_to_install))
    
        # define the R function that this script will use
        robjects.r(
            '''
            # function to utilize the clusterCrit package in R
            # the sklearn module from python does not contain all
            # matrics that we wish to test
            crit <- function(dataset, labels) {    
                # $cluster: Cluster of each observation
                # $centers: Cluster centers
                # $totss: Total sum of squares
                # $withinss: Within sum of square. The number of components return is equal to `k`
                # $tot.withinss: sum of withinss
                # $betweenss: total sum of square minus within sum of square
                # $size: number of observation within each cluster
                ccData <- clusterCrit::intCriteria(dataset, unlist(labels), "all")
                return(list(ccData, clusterCrit::getCriteriaNames(TRUE)))
            }
            '''
        )
        
        # technically this is global but return the `alias` or the callable
        # to the R function so that it can be used later
        self.rFunc = robjects.globalenv['crit']

    def exec_criteria(self, data_set, labels, k):
        """
        :param data_set:
        :param labels:
        """
        if self.rFunc is not None:
            numpy2ri.activate()
            applied_data, crit_algorithms = self.rFunc(data_set, labels)
            numpy2ri.deactivate()
            return pd.DataFrame(applied_data, index=crit_algorithms, columns=[str(k)])