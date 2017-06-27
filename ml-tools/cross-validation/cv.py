""" This module contains various methods for conducting cross-validation over a set of models and given a training set.

Author: Alberto Mizrahi
Last modified: 06/15/17
"""

from typing import List
from random import sample
from math import ceil


def f_split(lst, fraction):
    """ Splits the given list into two subsets: one containing f% of the of all the elements and the other containing the rest of the (1-f)% of them.

    Args:
        lst: the list of objects to be split.
        fraction: fraction of elements that will be contained in one subset.

    Returns:
        A list of the two subsets.
    """
    size1 = ceil(len(lst)*fraction)
    shuffled = sample(lst, len(lst))

    return [shuffled[0:size1], shuffled[size1:len(shuffled)]] 


def random_split(lst, chunks):
    """ Given a list and a number of chunks, it will shuffle the list and then split it into the specified number of chunks.

    Args:
        lst: the list of objects to be split
        chunks: the number of subsets the list will be partitioned into

    Returns:
        The list of chunks
    """
    if len(lst) % chunks != 0: 
        print("ERROR: the size of the list that you are trying to split is not divisible by the number of chunks that you want.")
        return None
    
    # calculate how many elements will each chunk have
    size = len(lst) // chunks
    # returns a new copy of the list but shuffled
    shuffled = sample(lst, len(lst))

    return [shuffled[i:i+size] for i in range(0, len(shuffled), size)]


def hold_out_cv(models, training_set):
    """ In hold-out cross validation, the training set is split into two sets S1 and S2. S1 contains 70% of the 
examples and S2 contains the other 30%. S1 is then used to train each model and S2 to test it

    Args:
        models: a list containing all the models being considered
        training_set: a list of all the examples

    Returns:
        The model with the best accuracy
    """

    [training_examples, test_examples] = f_split(training_set, 0.7)

    best_accuracy = 0
    best_model = None
    for model in models:
        model.train(training_examples)
        accuracy = model.test(test_examples)
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model

    # Once the best model is selected with train with the entire training set
    best_model.clear()
    best_model.train(training_set)

    return best_model


def k_fold_cv(models, training_set, k):
    """ In k-fold cross validation, the training set is randomly split into k disjoint subsets S_1, ..., S_k.
    For j=1,..., each model M_i is trained with the sets S_1, S_2, ..., S_(j-1), S_(j+1), ..., S_k and its 
    accuracy is determined by testing it on S_j. The average of these accuracies (over all j) is then 
calculated and the best model is then chosen.
	

    Args:
        models: a list containing all the models being considered
        training_set: a list of all the examples
        k: number of subsets to split the training set into

    Returns:
        The model with the best accuracy
    """
    subsets = random_split(training_set, k)

    best_avg_accuracy = 0
    best_model = None
    for model in models:
        sum_accuracy = 0
        for i in range(0, k):
            # remove the subset with which the model will be tested
            test_examples = subsets.pop(i)
            # flatten the rest of the subsets, i.e. join the rest of the subsets into a single one, which will be used to train the model
            training_examples = [item for subset in subsets for item in subset]

            model.train(training_examples)
            sum_accuracy += model.test(test_examples)

            subsets.insert(i, test_examples)
            model.clear()

        avg_accuracy = sum_accuracy / k
        if avg_accuracy > best_avg_accuracy:
            best_avg_accuracy = avg_accuracy
            best_model = model

    # Once the best model is selected with train with the entire training set
    best_model.clear()
    best_model.train(training_set)

    return best_model

def leave_one_out_cv(models, training_set):
    """ Leave-one-out cross validation is just k-fold cross validation where k = no. of examples in training set.

    Args:
        models: a list containing all the models being considered
        training_set: a list of all the examples

    Returns:
        The model with the best accuracy
    """
    return k_fold_cv(models, training_set, len(training_set))
