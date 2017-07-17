""" This file contains the abstract classes that represent general concept used throughout machine learning algorithms. Any of the ML tools developed by the team assume that the objects passed to them inherit from these abstract classes, e.g. when passing a list of models to the cross-validation tool, the methods assume that these models implement the methods train(...), test(...), etc.

Author: Alberto Mizrahi
Last modified: 06/26/17
"""

import cv
import random

class DummyExample:
    """ Represents an example data point that the learning model will use to train on or to test its acuuracy with """

    def __init__(self, feat, out):
        self.feature = feat
        self.output = out

    def get_features(self):
        """ Returns the features (or input variables) of the example.

        Returns:
            A dict containing all the features names and their corresponding values for this example
        """
        return {'feature1': self.feature} 

    def get_output(self):
        """ Returns the target (or output) variable of the example. """
        return self.output

    def __repr__(self):
        """ Return a string that represents this example"""
        return str(self.get_features()) + "->" + str(self.get_output())

class DummyLearningModel:
    """ Represents a test learning model that will be trained and then used to solve learning problems """

    def __init__(self, acc):
        self.accuracy = acc

    def train(self, examples):
        """ Trains the model with the given training examples.

        Args:
            examples: A list of Example objects.
        """
        pass

    def test(self, examples):
        """ Assuming that the model has been trained, it predicts the target variable for each example and checks whether its prediction is accurate.

        Args:
            examples: A list of Example objects.

        Returns:
            A percentage representing what fraction of the examples were predicted accurately.
        """
        return self.accuracy
    

    def clear(self):
        """ It clears, or "untrains", the model """
        pass

    def __repr__(self):
        return "Accuracy: %f" % (self.accuracy)

SIZE_TRAINING_SET = 100
SIZE_LEARNING_MODELS = 10
training_set = []
learning_models = []

for i in range(0, SIZE_TRAINING_SET):
    training_set.append(DummyExample(i, i))
    
# print(training_set)

rand_accuracy = 0
highest_accuracy = 0
for i in range(0, SIZE_LEARNING_MODELS):
    rand_accuracy = random.random()
    if rand_accuracy > highest_accuracy: highest_accuracy = rand_accuracy
    learning_models.append(DummyLearningModel(rand_accuracy))

# print(learning_models)

print("Highest accuracy: %f" % highest_accuracy)
print("Model with highest accuracy with Hold-out CV: %f"
      % cv.hold_out_cv(learning_models, training_set).accuracy)
print("Model with highest accuracy with k-fold CV: %f"
      % cv.k_fold_cv(learning_models, training_set, 10).accuracy)
print("Model with highest accuracy with Leave-one-out CV: %f"
      % cv.leave_one_out_cv(learning_models, training_set).accuracy)

