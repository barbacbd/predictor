from copy import deepcopy


def mean(data):
    """
    Calculate the mean of all data vectors

    :param data: list of vectors
    :return: Resultant vector where each component is the mean
    """
    total_vector = deepcopy(data[0])

    num_used = 0
    for idx in range(1, len(data)):
        if data[idx].dimensions == total_vector.dimensions:
            total_vector = total_vector + data[idx]
            num_used += 1

    if len(data) - 1 != num_used:
        if not __debug__:
            print("Failed to use all of the data")

    for var in total_vector:
        if getattr(total_vector, var, None) is not None:
            setattr(total_vector, var, getattr(total_vector, var) / num_used)

    return total_vector
