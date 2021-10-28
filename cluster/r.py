from rpy2 import robjects
from rpy2.robjects.vectors import FloatVector
from rpy2.robjects.packages import importr, isinstalled
from rpy2.robjects import numpy2ri
from rpy2.robjects.vectors import StrVector
import pandas as pd
from threading import Lock
from enum import Enum


# should this be a singleton ? Ehh probably that way its not constantly loading data


class ClusterCrit(object):

    _instance = None
    _lock = Lock()
    _func = None

    def __new__(cls, *args, **kwargs):

        if not cls._instance:
            with cls._lock:

                cls._instance = super(ClusterCrit, cls).__new__(cls, *args, **kwargs)

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
                cls._func = robjects.globalenv['crit']

        return cls._instance

    def __call__(self, data_set, labels, k, *args, **kwargs):
        """
        Allow the caller to access the cluster crit package from R.

        :param data_set: Original Data set
        :param labels: Array/List type object that contains (in order of the original data set)
        the cluster number from 1-k where the data point aligns.
        :param k: Number of clusters that the algorithm was run with. This is
        provided for display/label purposes ONLY.
        
        :return: Pandas Dataframe where the column is the number k (provided) and the rows
        are the algorithms run within the cluster crit package
        """
        with self._lock:
            if self._func is not None:
                numpy2ri.activate()
                applied_data, crit_algorithms = self._func(data_set, labels)
                numpy2ri.deactivate()
                return pd.DataFrame(applied_data, index=crit_algorithms, columns=[str(k)])



class CritSelection(Enum):
    """
    All possible values that the Cran (R) package Cluster Crit can receive
    for the intCriteria. The `ALL` type is handled slightly differently as
    it should be the extension of only the valid values in this enumeration
    rather than `ALL` in cluster crit.
    """

    ALL = 0
    Ball_Hall = 1
    Banfeld_Raftery = 2
    C_index = 3
    Calinski_Harabasz = 4
    Davies_Bouldin = 5
    Det_Ratio = 6
    Dunn = 7
    Gamma = 8
    G_plus = 9
    # GDI11 
    # GDI12 
    # GDI13 
    # GDI21 
    # GDI22 
    # GDI23 
    # GDI31 
    # GDI32 
    # GDI33 
    # GDI41 
    # GDI42 
    # GDI43 
    # GDI51 
    # GDI52 
    # GDI53 
    Ksq_DetW = 10
    Log_Det_Ratio = 11
    Log_SS_Ratio = 12
    McClain_Rao = 13
    PBM = 14
    Point_Biserial = 15
    Ray_Turi = 16
    Ratkowsky_Lance = 17
    Scott_Symons = 18
    SD_Scat = 19
    SD_Dis = 20
    S_Dbw = 21
    Silhouette = 22
    Tau = 23
    Trace_W = 24
    Trace_WiB = 25
    Wemmert_Gancarski = 26
    Xie_Beni = 27


def selection_as_str(selection):
    """
    Turn the Selection into a string. The special case is for 
    `ALL` as it returns the combined string for all other values.
    """
    if not isinstance(selection, CritSelection):
        raise TypeError("selection expects %s, received %s" % (str(type(CritSelection)), str(type(selection))))

    if selection == CritSelection.ALL:
        ", ".join([x.name for x in CritSelection if x != CritSelection.ALL])
    else:
        return selection.name