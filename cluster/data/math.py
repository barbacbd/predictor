from copy import deepcopy


def sum(data):
    """
    Calculate the sume of all data Vectors

    :param data:
    :return:
    """
    total_vector = deepcopy(data[0])

    for idx in range(1, len(data)):
        total_vector = total_vector + data[idx]

    return total_vector


def mean(data):
    """
    Calculate the mean of all data vectors

    :param data: list of vectors
    :return: Resultant vector where each component is the mean
    """
    total_vector = sum(data)

    for var in total_vector:
        if getattr(total_vector, var, None) is not None:
            setattr(total_vector, var, getattr(total_vector, var) / len(data))

    return total_vector
