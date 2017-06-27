""" This file contains the abstract classes that represent general concept used throughout machine learning algorithms. Any of the ML tools developed by the team assume that the objects passed to them inherit from these abstract classes, e.g. when passing a list of models to the cross-validation tool, the methods assume that these models implement the methods train(...), test(...), etc.

Author: Alberto Mizrahi
Last modified: 06/15/17
"""

from abc import ABC, abstractmethod

class Example(ABC):
    """ Represents an example data point that the learning model will use to train on or to test its acuuracy with """

    @abstractmethod
    def get_features(self):
        """ Returns the features (or input variables) of the example.

        Returns:
            A hash containing all the features names and their corresponding values for this example
        """
        pass

    @abstractmethod
    def get_output(self):
        """ Returns the target (or output) variable of the example. """
        pass

    def __repr__(self):
        """ Return a string that represents this example"""
        return str(self.get_features()) + "->" + str(self.get_output())

class LearningModel(ABC):
    """ Represents a learning model that will be trained and then used to solve learning problems """

    @abstractmethod
    def train(self, examples):
        """ Trains the model with the given training examples.

        Args:
            examples: A list of Example objects.
        """
        pass

    @abstractmethod
    def test(self, examples):
        """ Assuming that the model has been trained, it predicts the target variable for each example and checks whether its prediction is accurate.

        Args:
            examples: A list of Example objects.

        Returns:
            A percentage representing what fraction of the examples were predicted accurately.
        """
        pass
    
    @abstractmethod
    def clear(self):
        """ It clears, or "untrains", the model """
        pass
