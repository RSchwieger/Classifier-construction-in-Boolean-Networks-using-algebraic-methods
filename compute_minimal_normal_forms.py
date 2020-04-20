from __future__ import print_function
from sage.all import *
from timeit import default_timer as timer
#from candidate_sets import excl_forward
from candidate_sets import exclude_backward, exclude_forwardeq, exclude_forward, initialize_candidate_sets, pick_a_set_of_P

        
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
    R = BooleanPolynomialRing(names=components_in_order, order=TermOrder('lex')) # ToDo: Use R.clone()
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

    leadingTerm = varphi.lt()
    variables_in_leading_term = leadingTerm.variables()
    variables_not_in_leading_term = [v for v in components_in_order if (not v in variables_in_leading_term)]
    
    index_i = components_in_order.index(x_i)
    variables_larger_than_xi = components_in_order[:index_i]
    variables_smaller_or_equal_than_xi = components_in_order[index_i:]
    variables_not_in_leading_term_larger_than_xi = [v for v in variables_not_in_leading_term if (v in variables_larger_than_xi)]
    
    S_i = smallereq_of_variables_in_varphi
    S_i.remove(x_i)
    S_i = [v for v in S_i if not (v in variables_not_in_leading_term_larger_than_xi)]
    return S_i
    
    
        
def compute_min_repr(varphi, variables, ideal_generators):
    if len(varphi.variables()) == 0:
	print("classifier is constant "+ str(varphi)+ " on the zero set of the ideal")
	return [varphi]
    P = initialize_candidate_sets(variables)
    S = initialize_candidate_sets(variables)
    
    V = varphi.variables()
    A = get_A_from_V(variables, V)
    
    P = exclude_forwardeq(P, V, variables)
    S = exclude_forward(S, V, variables)
    
    number_of_reductions = 0 # To see how many reductions we need

    # Before running test if varphi is in the ideal
    R, components_in_order = get_order(A)
    components_in_order = [R.variable(i) for i in range(len(components_in_order))]
    varphi = reduce(varphi, R, ideal_generators)
    if len(varphi.variables()) == 0:
	print("classifier is constant zero on the zero set of the ideal")
	return [varphi]
    
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
            print("number_of_reductions = "+str(number_of_reductions))
            return S

def exclude_backward_sets(varphi, components_in_order, P):
    """
    Excludes the backward sets S_i from P
    """
    leadingTerm = varphi.lt()
    variables_in_leading_term = leadingTerm.variables()
    for var in variables_in_leading_term:
        S_i = compute_Si(varphi, components_in_order, var)
        P = exclude_backward(P, S_i, components_in_order)
    return P

def print_to_file(solutions, variables, ideal, varphi, filename="output"):
	"""
	Creates a latex table to save the solutions
	"""
	f = open(filename, 'w')
	f.write("\\begin{longtable}{| p{.30\\textwidth} | p{.70\\textwidth} |}  \hline"+"\n")
	f.write("Components & Expression \\\\"+"\n")
	for sol in solutions:
		block_in_order = {str(a):0 for a in variables}
    		for a in sol.variables():
        		block_in_order[str(a)] = 1
		R, components_in_order = get_order(block_in_order)
		components_in_order = [R.variable(i) for i in range(len(components_in_order))]
		varphi = reduce(varphi, R, ideal)
		print(varphi)
		f.write("\\hline"+" \n")
		f.write(str(sol.variables()).replace("(","").replace(")","")+" & "+str(varphi)+" \\\\"+"\n")
	f.write("\\caption{"+str(len(solutions))+" different representations}"+"\n")
	f.write("\\end{longtable}"+"\n")
	f.close()

if __name__ == "__main__":
	variables = ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10", "x11"]

	R = BooleanPolynomialRing(names=variables, order=TermOrder('lex'))
	R.inject_variables()
	variables = [R.variable(i) for i in range(len(variables))]
	
	f1 = 1+x6
	f2 = x1*x5*(1+x7)
	f3 = (x10+(x4+x2+x2*x4)+x10*(x4+x2+x2*x4)) * (1+x7)
	f4 = x4
	f5 = x6+x3*(1+x7)+x6*x3*(1+x7)
	f6 = x9*(1+x7)
	f7 = x11*x8*(1+x2)
	f8 = (1+x3)*(x10+x4+x4*x10)
	f9 = (1+x7)*(x8+x6+x6*x8)
	f10 = x10
	f11 = (x7+x11+x7*x11) * (1+x5)
	
	ideal_generators = [f1+x1,f2+x2,f3+x3,f4+x4,f5+x5,f6+x6,f7+x7,f8+x8,f9+x9,f10+x10,f11+x11]
	ind_necrosis = (1+x1)*x6
	ind_survival = x7
	ind_apoptosis = (1+ind_survival)*(1+ind_necrosis)
	
	varphi = ind_necrosis
	print("Start computing...")
	solutions = compute_min_repr(varphi, variables, ideal_generators)
	print("There are "+str(len(solutions)))
	print("The solutions are:")

	# Print solutions
	for sol in solutions:
		print(sol.set())
	
	#solutions = solutions.truthtable()
	#vars = solutions.get_table_list()[0]
	#for row in solutions.get_table_list()[1:]:
	#    if row[-1]:
	#        print(5*"---")
	#        A = {str(a):1*b for (a,b) in zip(vars, row[:-1])}
	#        print(A)
	#        R, _ = get_order(A)
	#        varphi = reduce(varphi, R, ideal_generators)
	#        print(varphi)
	#        print(5*"+++")
