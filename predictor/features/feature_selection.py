from enum import Enum
from ..log import get_logger


log = get_logger()


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


try:
    from feast.feast import (
        CMIM,
        discCMIM,
        BetaGamma,
        discBetaGamma,
        CondMI,
        discCondMI,
        DISR,
        discDISR,
        ICAP,
        discICAP,
        JMI,
        discJMI,
        MIM,
        discMIM,
        mRMR_D,
        disc_mRMR_D,
        weightedCMIM,
        discWeightedCMIM,
        weightedCondMI,
        discWeightedCondMI,
        weightedDISR,
        discWeightedDISR,
        weightedJMI,
        discWeightedJMI,
        weightedMIM,
        discWeightedMIM
    )
    
    TypeToFeastFunc = {
        FeatureSelectionType.CMIM: CMIM,
        FeatureSelectionType.discCMIM: discCMIM,
        FeatureSelectionType.BetaGamma: BetaGamma,
        FeatureSelectionType.discBetaGamma:discBetaGamma,
        FeatureSelectionType.CondMI: CondMI,
        FeatureSelectionType.discCondMI: discCondMI,
        FeatureSelectionType.DISR: DISR,
        FeatureSelectionType.discDISR: discDISR,
        FeatureSelectionType.ICAP: ICAP,
        FeatureSelectionType.discICAP: discICAP,
        FeatureSelectionType.JMI: JMI,
        FeatureSelectionType.discJMI: discJMI,
        FeatureSelectionType.MIM: MIM,
        FeatureSelectionType.discMIM: discMIM,
        FeatureSelectionType.mRMR_D: mRMR_D,
        FeatureSelectionType.disc_mRMR_D: disc_mRMR_D,
        FeatureSelectionType.weightedCMIM: weightedCMIM,
        FeatureSelectionType.discWeightedCMIM: discWeightedCMIM,
        FeatureSelectionType.weightedCondMI: weightedCondMI,
        FeatureSelectionType.discWeightedCondMI: discWeightedCondMI,
        FeatureSelectionType.weightedDISR: weightedDISR,
        FeatureSelectionType.discWeightedDISR: discWeightedDISR,
        FeatureSelectionType.weightedJMI: weightedJMI,
        FeatureSelectionType.discWeightedJMI: discWeightedJMI,
        FeatureSelectionType.weightedMIM: weightedMIM,
        FeatureSelectionType.discWeightedMIM: discWeightedMIM
    }


    def select_features(feature_selection_type, data, labels, num_features_to_select, weights=[]):
        '''Run the feature selection algorithm provided as an enumeration in the `feature_selection_type`.
        
        :param feature_selection_type: value from `FeatureSelectionType`
        :param data: main dataset 
        :param labels: data set labels
        :param num_features_to_select:
        :param weights: Optional list of weights attached to all data values in the set
        :return: 
        '''
        if feature_selection_type not in TypeToFeastFunc:
            log.error(f"Failed to find feast function matching {feature_selection_type}")
            return None
        
        if num_features_to_select <= 0:
            log.error("Number of features to select must be greater than 0")
            return None
        
        func = TypeToFeastFunc.get(feature_selection_type)
        
        if "weighted" in feature_selection_type.name.lower():
            # check size of weights vs size of data
            if not weights:
                log.error("Weights parameter does not match size of data")
                return None
        
            selected_features, feature_scores = func(data, labels, weights, num_features_to_select)
        elif "BetaGamma" in feature_selection_type.name:
            selected_features, feature_scores = func(data, labels, num_features_to_select, 1.0, 1.0)
        else:
            selected_features, feature_scores = func(data, labels, num_features_to_select)
        
        log.debug(selected_features, feature_scores)
        
        feature_names = data.columns.tolist()
        return [feature_names[idx] for idx in selected_features]
    
except ImportError as error:
    log.error(error)
    
    def select_features(feature_selection_type, data, labels, num_features_to_select, weights=[]):
        # empty function
        return None
