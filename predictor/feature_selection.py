from enum import Enum

class FeatureSelectionType(Enum):

    ALL = 0
    CMIM = 1
    discCMIM = 2
    BetaGamma = 3
    discBetaGamma = 4
    CondMI = 5
    discCondMI = 6
    DISR = 7
    discDISR = 8
    ICAP = 9
    discICAP = 10
    JMI = 11
    discJMI = 12
    MIM = 13
    discMIM = 14
    mRMR_D = 15
    disc_mRMR_D = 16
    weightedCMIM = 17
    discWeightedCMIM = 18
    weightedCondMI = 19
    discWeightedCondMI = 20
    weightedDISR = 21
    discWeightedDISR = 22
    weightedJMI = 23
    discWeightedJMI = 24
    weightedMIM = 25
    discWeightedMIM = 26
    
    
    def selection_as_str(selection):
        '''Turn the Selection into a string. The special case is for 
        `ALL` as it returns the combined string for all other values.
        '''
        if not isinstance(selection, FeatureSelectionType):
            raise TypeError("selection expects %s, received %s" % (str(type(FeatureSelectionType)), str(type(selection))))

        if selection == FeatureSelectionType.ALL:
            ", ".join([x.name for x in FeatureSelectionType if x != FeatureSelectionType.ALL])
        else:
            return selection.name


def select_features(files, selected_features):
    '''Execute the provided FEAST algorithms (see FeatureSelectionType) in selected
    features on all data provided in the files. These files should be the artifacts 
    from executing the cluster analysis.
    
    :param files: Files output by the cluster analysis
    :param selected_features: list of FEAST feature selection algorithms.
    '''
    