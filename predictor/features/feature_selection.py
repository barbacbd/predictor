
from enum import Enum
from os.path import exists
from os import mkdir
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


class FeatureSelector:
    
    ArtifactsDirectory = "feature_results"
    
    def __init__(
        self, 
        feature_algorithms, 
        num_features_to_select, 
        dataframes={}, 
        selections={}, 
        weights={},
        algorithm_extras={}
    ):
        '''
        :param feature_algorithms: List of Feature algorithm(s) to gather data against
        :param num_features_to_select: Number of Features to select from the dataframes
        :param dataframes: Dictionary containing the cluster and crit information as dataframes
        :param selections: Dictionary containing the selected value for each row in the dataframe
        :param weights: Weight of each datapoint in the dataframes
        :param algorithm_extras: Dictionary of name and extra values applied to cluster algorithms
        '''
        self.feature_algorithms = feature_algorithms
        self.num_features_to_select = num_features_to_select
        self.dataframes = dataframes
        self.selections = selections
        self.weights = weights
        self.algorithm_extras = algorithm_extras
        self.labels = self._create_labels()
    
        self.selected_features = {}

        if "beta" not in self.algorithm_extras:
            self.algorithm_extras["beta"] = 1.0
        if "gamma" not in self.algorithm_extras:
            self.algorithm_extras["gamma"] = 1.0

    def _create_labels(self):
        '''Create the labels from dataframes
        '''
        return {}

    def select_features(self):
        '''Run all of the feature algorithms for the cluster information stored in the
        dataframes. When a a disc/discretized feature selection algorithm is encountered
        then the `_clusters` dataframes are used. When a weighted algorithm is encountered
        the weights will be used. All other occurrences will use the normal dataframe without
        extra parameters.
        '''
        for title, df in self.dataframes.items():
            
            # TODO: may need to transpose the dataframe 
            
            df2np = df.to_numpy()
            labels = self.labels[title]
            discretized = "_clusters" in title
            
            for feature in self.feature_algorithms:
                
                if feature not in TypeToFeastFunc:
                    log.warning("Dataframe %s skipping feature algorithm %s", title, feature.name)
                    continue
                
                selected_features = None
                feature_scores = None
                
                if feature == FeatureSelectionType.BetaGamma and not discretized:
                    selected_features, feature_scores = \
                        TypeToFeastFunc[feature](
                            df2np, labels, self.num_features_to_select, 
                            self.algorithm_extras["beta"], self.algorithm_extras["gamma"]
                        )
                elif feature == FeatureSelectionType.discBetaGamma and discretized:
                    selected_features, feature_scores = \
                        TypeToFeastFunc[feature](
                            df2np, labels, self.num_features_to_select, 
                            self.algorithm_extras["beta"], self.algorithm_extras["gamma"]
                        )
                elif "weight" in feature.name.lower():
                    if feature.name.startswith("disc") and discretized:
                        selected_features, feature_scores = \
                            TypeToFeastFunc[feature](df2np, labels, self.weights[title], self.num_features_to_select)
                    elif not feature.name.startswith("disc") and not discretized:
                        selected_features, feature_scores = \
                            TypeToFeastFunc[feature](df2np, labels, self.weights[title], self.num_features_to_select)
                else:
                    # Note: CMIM always uses discretized values
                    if (feature.name.startswith("disc") and discretized) or feature == FeatureSelectionType.CMIM:
                        selected_features, feature_scores = \
                            TypeToFeastFunc[feature](df2np, labels, self.num_features_to_select)
                    elif not feature.name.startswith("disc") and not discretized:
                        selected_features, feature_scores = \
                            TypeToFeastFunc[feature](df2np, labels, self.num_features_to_select)
        
        
                if selected_features is not None and feature_scores is not None:
                    if title not in self.selected_features:
                        self.selected_features[title] = {}
                    
                    # TODO: convert the selected features to the names of the features 
                    # TODO: Add in the scores too
                    
                    self.selected_features[title][feature.name] = selected_features
                    
                else:
                    log.error("Failed to retrieve data for %s with %s algorithm", title, feature.name)

    def generate_artifacts(self):
        '''Generate the artifacts for the feature selector. This should ONLY be
        executed after `select_features` is completed.
        '''
        if not exists(FeatureSelector.ArtifactsDirectory):
            log.info("Creating feature directory: %s", FeatureSelector.ArtifactsDirectory)
            mkdir(FeatureSelector.ArtifactsDirectory)
        
        
