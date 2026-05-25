import peak
import trace

################################################################################
################################## Algorithms ##################################
################################################################################

def algorithm1(problem, trace = None):
    pass

def algorithm2(problem, location = (0, 0), trace = None):
    pass

def algorithm3(problem, bestSeen = None, trace = None):
    pass

def algorithm4(problem, bestSeen = None, rowSplit = True, trace = None):
    pass


################################################################################
################################ Helper Methods ################################
################################################################################


def crossProduct(list1, list2):
    """
    Returns all pairs with one item from the first list and one item from 
    the second list.  (Cartesian product of the two lists.)

    The code is equivalent to the following list comprehension:
        return [(a, b) for a in list1 for b in list2]
    but for easier reading and analysis, we have included more explicit code.
    """

    answer = []
    for a in list1:
        for b in list2:
            answer.append ((a, b))
    return answer
