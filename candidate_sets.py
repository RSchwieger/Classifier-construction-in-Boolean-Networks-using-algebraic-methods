

from brial.frontend import Polynomial
from brial.frontend import *
from brial.frontend import *


# ToDo: Variables need to be always from the same ring.
# ToDo Better with class
def change_variables(variables):
    """
    We want that the order depends only on the variable names and is not ring dependend.
    """

    if change_variables.internal_variables is None:
        change_variables.internal_variables = variables
        change_variables.varnames_to_vars = {str(var): var for var in change_variables.internal_variables}

        return change_variables.internal_variables

    else:
        variables = map(str, variables)
        variables = [change_variables.varnames_to_vars[varname] for varname in variables]

        return variables

change_variables.internal_variables = None
change_variables.varnames_to_vars = None


def power_set(variables):
    variables = change_variables(variables)

    if not variables:
        return get_set_of_empty_set()  # BooleConstant(1)

    variables = sorted(set(variables), reverse=True, key=top_index)
    res = Polynomial(1, variables[0].ring()).set()
    for v in variables: 
        res = if_then_else(v,res,res)

    return res


def exclude_backward(candidate_sets, list_of_backward_variables, all_components=None):
        """
        Exclude the backward set.
        Example: exclude_backward({{1,2,3},{2,3,4},{1,2},{2}}, {1,2})
        results in {{1,2,3},{2,3,4}}.
        """
        powerSet_of_S = power_set(list_of_backward_variables)
        res = candidate_sets.diff(powerSet_of_S)

        return res


def exclude_forwardeq(candidate_sets, list_of_forward_variables, list_of_all_variables):
    """
    Exclude the forwardeq set. That is, all sets with subset V.
    Example: exclude_forwardeq({{1,2,3},{2,3,4},{1,2},{2}}, {1,2})
    results in {{2,3,4},{2}}.
    """

    # ToDo: better algorithm
    list_of_forward_variables = change_variables(list_of_forward_variables)
    list_of_all_variables = change_variables(list_of_all_variables)
    new_candidate_sets = candidate_sets.diff(candidate_sets)  # ToDo: Find function for empty set

    for elem in list_of_forward_variables:
        complement = set(list_of_all_variables).difference({elem})
        complement = list(complement)
        powerSet_of_complement = power_set(complement)
        new_candidate_sets = new_candidate_sets.union(candidate_sets.intersect(powerSet_of_complement))

    return new_candidate_sets


def turn_list_into_booleset(variables):
    variables = change_variables(variables)
    if not variables: 
        print("Exception in turn_list_into_booleset. Length of input is zero")  # ToDo: Exception

    res = Polynomial(1, variables[0].ring())

    for var in variables:
        res *= var

    return res.set()


def exclude_forward(candidate_sets, list_of_forward_variables, list_of_all_variables):
    """
    Exclude the forward set. That is, all sets with proper subset V.
    Example: exclude_forward({{1,2,3},{2,3,4},{1,2},{2}}, {1,2})
    results in {{2,3,4},{1,2},{2}}.
    """
    new_candidate_sets = exclude_forwardeq(candidate_sets, list_of_forward_variables, list_of_all_variables)

    return new_candidate_sets.union(turn_list_into_booleset(list_of_forward_variables))


def pick_a_set_of_P(candidate_sets, A, variables):
    """
    Returns none if empty otherwise
    returns a set satisfting P. A is not used
    
    P is a boolean formula
    """

    if len(candidate_sets) == 0:
        return None

    new_A = {str(a): 0 for a in variables}
    list_of_variables = next(iter(candidate_sets)).variables()

    for a in list_of_variables:
        new_A[str(a)] = 1

    return new_A


def initialize_candidate_sets(variables):
    """
    Initialize the candidate set with the power set
    """
    return power_set(variables)


def get_set_of_empty_set():  # ToDo
    # ToDo: Find a better way
    if change_variables.internal_variables is None or len(change_variables.internal_variables) == 0:
        print("Exception in get_empty_set(R)")

    return Polynomial(1, change_variables.internal_variables[0].ring()).set()
