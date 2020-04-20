from __future__ import print_function
from sage.all import *
from timeit import default_timer as timer
from compute_minimal_normal_forms import compute_min_repr



if __name__ == "__main__":
	variables = ["RAS", "MOMP"]

	R = BooleanPolynomialRing(names=variables, order=TermOrder('lex'))
	R.inject_variables()
	variables = [R.variable(i) for i in range(len(variables))]
	
	f1 = RAS*MOMP
	f2 = RAS
	
	ideal_generators = [f1+RAS, f2+MOMP]
	classifier = MOMP*RAS
	
	print("Start computing...")
	solutions = compute_min_repr(classifier, variables, ideal_generators)
	print("There are "+str(len(solutions))+" solutions")
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
