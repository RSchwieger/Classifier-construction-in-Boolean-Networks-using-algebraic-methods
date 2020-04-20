from __future__ import print_function
from sage.all import *
from timeit import default_timer as timer
from compute_minimal_normal_forms import compute_min_repr



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
