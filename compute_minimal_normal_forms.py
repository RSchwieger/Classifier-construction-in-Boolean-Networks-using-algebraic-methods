

import sys
import logging
from dataclasses import dataclass
from typing import List

from sage.all import TermOrder
from sage.all import BooleanPolynomialRing
from sage.all import Ideal
from sage.rings.polynomial.pbori import BooleSet
from sage.rings.polynomial.pbori import BooleanMonomial
from sage.rings.polynomial.pbori import BooleanPolynomial


from candidate_sets import exclude_backward, exclude_forwardeq, exclude_forward, initialize_candidate_sets, pick_a_set_of_P

if sys.version_info[0] < 3:
    raise Exception("must be using Python 3")

log = logging.getLogger(__name__)

        
def get_order(A):
    """
    Build an order > with Complement(A) > A
    The set A is represented as a dictionary. e.g. {x2, x3} as {"x1": 0, "x2": 1, "x3": 1} 
    Entries with 1 represents the elements
    
    Returns BooleanPolynomialRing equiped with an order > as above
    and a list components_in_order starting with the largest variables/components.
    """
    ones = [key for key in A if A[key] == 1]
    zeros = [key for key in A if A[key] == 0]
    components_in_order = zeros+ones
    R = BooleanPolynomialRing(names=components_in_order, order=TermOrder('lex'))  # ToDo: Use R.clone()
    return R, components_in_order


def get_maximum_element(set_of_elements, components_in_order):
    """
    Returns the index in components_in_order of the largest element in set_of_elements
    """

    # Get maximal element in set_of_elements (that is the variables of varphi)
    for i in range(len(components_in_order)):
        if components_in_order[i] in set_of_elements:
            index_of_max_elem = i
            break

    return index_of_max_elem


def get_A_from_V(variables, V):
    """
    A representation of V as a dictionary with variables as key. Zero for element
    not occuring, one for occuring
    """
    return {var: (1 if (var in map(str,V)) else 0) for var in variables}
    
    
def reduce(varphi, R, ideal_generators):

    ideal_generators = [R(elem) for elem in ideal_generators]
    I = Ideal(ideal_generators)
    ideal_generators = I.groebner_basis() 
    varphi = R(varphi)
    varphi = varphi.reduce(ideal_generators)

    return varphi


def compute_Si(varphi, components_in_order, x_i):
    """
    Varphi is a polynomial in a Boolean Polynomial Ring
    A list components_in_order of ordered components with respect to the order of the Boolean Polynomial Ring and
    the components ordered in descending order.
    """
    
    variables_in_varphi = varphi.variables()
    index_of_largest_var_in_varphi = get_maximum_element(variables_in_varphi, components_in_order)
    smallereq_of_variables_in_varphi = components_in_order[index_of_largest_var_in_varphi:]

    leading_term = varphi.lt()
    variables_in_leading_term = leading_term.variables()
    variables_not_in_leading_term = [v for v in components_in_order if (not v in variables_in_leading_term)]
    
    index_i = components_in_order.index(x_i)
    variables_larger_than_xi = components_in_order[:index_i]
    variables_smaller_or_equal_than_xi = components_in_order[index_i:]
    variables_not_in_leading_term_larger_than_xi = [v for v in variables_not_in_leading_term if (v in variables_larger_than_xi)]
    
    S_i = smallereq_of_variables_in_varphi
    S_i.remove(x_i)
    S_i = [v for v in S_i if not (v in variables_not_in_leading_term_larger_than_xi)]

    return S_i


@dataclass()
class MinRepresentations:
    solutions: BooleSet
    is_constant: bool
    n_reductions: int
    variables: List[BooleanMonomial]
    ideal_generators: List[BooleanPolynomial]
    varphi: BooleanPolynomial

    def to_list(self) -> List[List[str]]:
        return [[str(x) for x in sol.set()] for sol in self.solutions]

    def to_polynomials(self) -> List[str]:
        polys = []
        block_in_order = {str(a): 0 for a in self.variables}

        for sol in self.solutions:
            for a in sol.variables():
                block_in_order[str(a)] = 1

            r, components_in_order = get_order(block_in_order)
            varphi = reduce(self.varphi, r, self.ideal_generators)

            polys.append(str(varphi))

        return polys


def compute_min_repr(varphi, variables, ideal_generators) -> MinRepresentations:
    if len(varphi.variables()) == 0:
        log.info(f"classifier is constant {varphi} on the zero set of the ideal: 1")

        return MinRepresentations(solutions=[varphi], is_constant=True, n_reductions=0, variables=variables, ideal_generators=ideal_generators, varphi=varphi)

    P = initialize_candidate_sets(variables)
    S = initialize_candidate_sets(variables)
    
    V = varphi.variables()
    A = get_A_from_V(variables, V)
    
    P = exclude_forwardeq(P, V, variables)
    S = exclude_forward(S, V, variables)
    
    number_of_reductions = 0  # To see how many reductions we need

    # Before running test if varphi is in the ideal
    R, components_in_order = get_order(A)
    components_in_order = [R.variable(i) for i in range(len(components_in_order))]
    varphi = reduce(varphi, R, ideal_generators)

    if len(varphi.variables()) == 0:
        log.info("classifier is constant zero on the zero set of the ideal: 2")

        return MinRepresentations(solutions=[varphi], is_constant=True, n_reductions=1, variables=variables, ideal_generators=ideal_generators, varphi=varphi)
    
    while True:

        R, components_in_order = get_order(A)
        components_in_order = [R.variable(i) for i in range(len(components_in_order))]
        #print("Reduce to ")
        varphi = reduce(varphi, R, ideal_generators)
        #print(varphi)
        number_of_reductions += 1
        
        V = varphi.variables()
        A = get_A_from_V(variables, V)

        P = exclude_forwardeq(P, V, variables)
        P = exclude_backward_sets(varphi, components_in_order, P)
        
        S = exclude_forward(S, V, variables)
        S = exclude_backward_sets(varphi, components_in_order, S)

        #print("P has "+str(len(P))+" elements left.")
        A = pick_a_set_of_P(P, A, variables)

        if A is None:
            log.info("number_of_reductions = "+str(number_of_reductions))
            return MinRepresentations(solutions=S, is_constant=False, n_reductions=number_of_reductions, variables=variables, ideal_generators=ideal_generators, varphi=varphi)


def exclude_backward_sets(varphi, components_in_order, p):
    """
    Excludes the backward sets S_i from P
    """

    leading_term = varphi.lt()
    variables_in_leading_term = leading_term.variables()

    for var in variables_in_leading_term:
        S_i = compute_Si(varphi, components_in_order, var)
        p = exclude_backward(p, S_i, components_in_order)

    return p

