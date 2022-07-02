import numpy as np
from sklearn.base import BaseEstimator

'''
def count_class_probabilities(y):
    # one-hot encoding is representation in matrix with 1 corresponding to a class which object is
    # and 0's which object is not.
    # Calculating number of instances of each class:
    n_obj_by_class = y.sum(axis=0)
    # Probabilities of each class:
    probs = n_obj_by_class/n_obj_by_class.sum()
    return probs
'''

def entropy(y):  
    """
    Computes entropy of the provided distribution. Use log(value + eps) for numerical stability
    
    Parameters
    ----------
    y : np.array of type float with shape (n_objects, n_classes)
        One-hot representation of class labels for corresponding subset
    
    Returns
    -------
    float
        Entropy of the provided subset
    """
    EPS = 0.0005
    
    probs = np.mean(y, axis=0)
    H = - np.sum(probs * np.log(EPS + probs))
    #H = 0
    #for p in probs:
    #    H -= p * np.log(EPS + p)
    
    return H
    
def gini(y):
    """
    Computes the Gini impurity of the provided distribution
    
    Parameters
    ----------
    y : np.array of type float with shape (n_objects, n_classes)
        One-hot representation of class labels for corresponding subset
    
    Returns
    -------
    float
        Gini impurity of the provided subset
    """

    # YOUR CODE HERE
    probs = np.sum(y, axis=0) / y.shape[0]
    H = 1 - np.sum(probs ** 2)
    #for p in probs:
    #    H -= p ** 2
    
    return H
    
def variance(y):
    """
    Computes the variance the provided target values subset
    
    Parameters
    ----------
    y : np.array of type float with shape (n_objects, 1)
        Target values vector
    
    Returns
    -------
    float
        Variance of the provided target vector
    """
    if len(y) == 0:
        return np.inf
    mean = np.mean(y)
    var = np.sum((y - mean) ** 2)/y.shape[0]
    
    return var

def mad_median(y):
    """
    Computes the mean absolute deviation from the median in the
    provided target values subset
    
    Parameters
    ----------
    y : np.array of type float with shape (n_objects, 1)
        Target values vector
    
    Returns
    -------
    float
        Mean absolute deviation from the median in the provided vector
    """

    # YOUR CODE HERE
    median = np.median(y)
    mad = np.sum(np.absolute(y.reshape(-1) - median))/y.shape[0]
    return mad


def one_hot_encode(n_classes, y):
    y_one_hot = np.zeros((len(y), n_classes), dtype=float)
    y_one_hot[np.arange(len(y)), y.astype(int)[:, 0]] = 1.
    return y_one_hot


def one_hot_decode(y_one_hot):
    return y_one_hot.argmax(axis=1)[:, None]


class Node:
    """
    This class is provided "as is" and it is not mandatory to it use in your code.
    Added pred_label by myself
    """
    def __init__(self, feature_index, threshold, pred_label = None, proba=0.):
        self.feature_index = feature_index
        self.value = threshold
        self.pred_label = pred_label  # self-made)
        self.proba = proba
        self.left_child = None
        self.right_child = None
        
class DecisionTree(BaseEstimator):
    all_criterions = {
        'gini': (gini, True), # (criterion, classification flag)
        'entropy': (entropy, True),
        'variance': (variance, False),
        'mad_median': (mad_median, False)
    }

    def __init__(self, n_classes=None, max_depth=np.inf, min_samples_split=2, 
                 criterion_name='gini', debug=False):

        assert criterion_name in self.all_criterions.keys(), 'Criterion name must be on of the following: {}'.format(self.all_criterions.keys())
        
        self.n_classes = n_classes
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.criterion_name = criterion_name

        self.depth = 0
        self.root = None # Use the Node class to initialize it later
        self.debug = debug

        
        
    def make_split(self, feature_index, threshold, X_subset, y_subset):
        """
        Makes split of the provided data subset and target values using provided feature and threshold
        
        Parameters
        ----------
        feature_index : int
            Index of feature to make split with

        threshold : float
            Threshold value to perform split

        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels for corresponding subset
        
        Returns
        -------
        (X_left, y_left) : tuple of np.arrays of same type as input X_subset and y_subset
            Part of the providev subset where selected feature x^j < threshold
        (X_right, y_right) : tuple of np.arrays of same type as input X_subset and y_subset
            Part of the providev subset where selected feature x^j >= threshold
        """
        '''
        # YOUR CODE HERE
        X_l = []
        X_r = []
        y_l = []
        y_r = []
        for i in range(0, X_subset.shape[0]):
            if(X_subset[i][feature_index] < threshold):
                X_l.append(X_subset[i])
                y_l.append(y_subset[i])
            else:
                X_r.append(X_subset[i])
                y_r.append(y_subset[i])
        
        X_left = np.array(X_l)
        X_right = np.array(X_r)
        y_left = np.array(y_l)
        y_right = np.array(y_r)
        '''
        left_part = X_subset[:, feature_index] < threshold
        X_left = X_subset[left_part, :]
        y_left = y_subset[left_part, :]
        
        right_part = X_subset[:, feature_index] >= threshold
        X_right = X_subset[right_part, :]
        y_right = y_subset[right_part, :]
        
        return (X_left, y_left), (X_right, y_right)
    
    def make_split_only_y(self, feature_index, threshold, X_subset, y_subset):
        """
        Split only target values into two subsets with specified feature and threshold
        
        Parameters
        ----------
        feature_index : int
            Index of feature to make split with

        threshold : float
            Threshold value to perform split

        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels for corresponding subset
        
        Returns
        -------
        y_left : np.array of type float with shape (n_objects_left, n_classes) in classification 
                   (n_objects, 1) in regression 
            Part of the provided subset where selected feature x^j < threshold

        y_right : np.array of type float with shape (n_objects_right, n_classes) in classification 
                   (n_objects, 1) in regression 
            Part of the provided subset where selected feature x^j >= threshold
        """
        # YOUR CODE HERE
        left_part = X_subset[:, feature_index] < threshold
        y_left = y_subset[left_part, :]
        right_part = X_subset[:, feature_index] >= threshold
        y_right = y_subset[right_part, :]
        
        return y_left, y_right

    def choose_best_split(self, X_subset, y_subset):
        """
        Greedily select the best feature and best threshold w.r.t. selected criterion
        
        Parameters
        ----------
        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels or target values for corresponding subset
        
        Returns
        -------
        feature_index : int
            Index of feature to make split with

        threshold : float
            Threshold value to perform split

        """
        # Need at least two elements to split a node.
        m = y_subset.size
        if m <= 1:
            return None, None
        
        # criterion is loaded 'by name' from dict above in the class
        #criterion = self.all_criterions[self.criterion_name][0]
        criterion = self.criterion
        #criterion = self.all_criterions[self.criterion_name][0]
        # base_criterion = criterion(y_subset)  #H(Q) in formula - criterion of current node alone
        
        min_criterion = 100 # Start value
        feature_index = 0
        threshold = 0
        n_features = X_subset.shape[1]
        
        for i in range(n_features):
            # choosing threshold in unique values of given feature:
            #for t in np.linspace(min_i, max_i, 20):
            for t in np.unique(X_subset[:, i]):
                # need to evaluate criterion here for each t(threshold)
                # splitting y with our desired feature&threshold combination:
                y_left, y_right = self.make_split_only_y(i, t, X_subset, y_subset)
                
                if (y_left.shape[0] == 0) or (y_right.shape[0] == 0):
                    continue
                    
                #base_criterion - \
                new_criterion = (y_left.shape[0]/y_subset.shape[0]) * criterion(y_left) + \
                    (y_right.shape[0]/y_subset.shape[0]) * criterion(y_right)
                
                # for the smallest criterion value saving feature&threshold:
                if(new_criterion < min_criterion):
                    min_criterion = new_criterion
                    feature_index = i
                    threshold = t
            
        return feature_index, threshold
    
    def make_tree(self, X_subset, y_subset, depth=0):
        """
        Recursively builds the tree
        
        Parameters
        ----------
        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels or target values for corresponding subset
        
        Returns
        -------
        root_node : Node class instance
            Node of the root of the fitted tree
        """
        
        # YOUR CODE HERE
        if(self.depth < depth):
            self.depth = depth
        
        feature_ind, threshold = self.choose_best_split(X_subset, y_subset)
        new_node = Node(
            feature_index = feature_ind,
            threshold = threshold,
            proba = 0,
        )
        
        # if max_depth is not reached in the branch and it is possible to make split:
        if(depth < self.max_depth) and feature_ind is not None:
            #self.depth += 1
            (X_left, y_left), (X_right, y_right) = self.make_split(feature_ind, threshold, X_subset, y_subset)
            new_node.left_child = self.make_tree(X_left, y_left, depth + 1)
            new_node.right_child = self.make_tree(X_right, y_right, depth + 1)
        else:
            if self.criterion_name in ["gini", "entropy"]:
                # this node is "the deepest" => it has prediction label in it
                # just the most common class inside of the node
                num_samples_per_class = [np.sum(y_subset == i) for i in range(self.n_classes)]
                #predicted_class = np.argmax(num_samples_per_class)
                new_node.pred_label = np.argmax(np.sum(y_subset, axis=0)) #predicted_class
                new_node.proba = np.mean(y_subset, axis=0)
            elif self.criterion_name == "variance":
                #new_node.proba = 0.
                new_node.pred_label = np.mean(y_subset.reshape(-1))
            elif self.criterion_name == "mad_median": 
                #new_node.proba = 0.
                new_node.pred_label = np.median(y_subset.reshape(-1))
            
        
        return new_node
    
    def fit(self, X, y):
        """
        Fit the model from scratch using the provided data
        
        Parameters
        ----------
        X : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the data to train on

        y : np.array of type int with shape (n_objects, 1) in classification 
                   of type float with shape (n_objects, 1) in regression 
            Column vector of class labels in classification or target values in regression
        
        """
        assert len(y.shape) == 2 and len(y) == len(X), 'Wrong y shape'
        self.criterion, self.classification = self.all_criterions[self.criterion_name]
        if self.classification:
            if self.n_classes is None:
                self.n_classes = len(np.unique(y))
            y = one_hot_encode(self.n_classes, y)

        self.root = self.make_tree(X, y)
    
    def predict_one(self, X):
        node = self.root
        #while we are not in the "predicting" nodes
        while node.pred_label is None:
            if X[node.feature_index] < node.value:
                node = node.left_child
            else:
                node = node.right_child
        return node.pred_label
    
    def predict(self, X):
        """
        Predict the target value or class label  the model from scratch using the provided data
        
        Parameters
        ----------
        X : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the data the predictions should be provided for

        Returns
        -------
        y_predicted : np.array of type int with shape (n_objects, 1) in classification 
                   (n_objects, 1) in regression 
            Column vector of class labels in classification or target values in regression
        
        """
        y_predicted = np.zeros(X.shape[0])
        for index, obj in enumerate(X):
            y_predicted[index] = self.predict_one(obj)
        
        return y_predicted
    
    
    def predict_proba(self, X):
        """
        Only for classification
        Predict the class probabilities using the provided data
        
        Parameters
        ----------
        X : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the data the predictions should be provided for

        Returns
        -------
        y_predicted_probs : np.array of type float with shape (n_objects, n_classes)
            Probabilities of each class for the provided objects
        
        """
        assert self.classification, 'Available only for classification problem'

        # YOUR CODE HERE
        n_objects = X.shape[0]
        y_predicted_probs = np.zeros((n_objects, self.n_classes))
        for index, obj in enumerate(X):
            node = self.root
            while node.pred_label is None:
                if obj[node.feature_index] < node.value:
                    node = node.left_child
                else:
                    node = node.right_child
            y_predicted_probs[index] = node.proba
            
        return y_predicted_probs
