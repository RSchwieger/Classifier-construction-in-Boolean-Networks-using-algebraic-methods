from __future__ import print_function
from sage.all import *
from timeit import default_timer as timer
from compute_minimal_normal_forms import compute_min_repr, print_to_file
from sets import Set

if __name__ == "__main__":
	variables = ['ATP', 'BAX', 'BCL2', 'CASP3', 'CASP8', 'Cyt_c',
'DISC_FAS', 'DISC_TNF', 'FADD', 'FASL', 'IKK', 'MOMP',
'MPT', 'NFKB1', 'NonACD', 'RIP1', 'RIP1K', 'RIP1ub', 'ROS', 'SMAC', 'TNF', 'TNFR', 'XIAP', 'apoptosome', 'cFLIP', 'cIAP',
'mROS', 'mXIAP', 'mcIAP']

	R = BooleanPolynomialRing(names=variables, order=TermOrder('lex'))
	R.inject_variables()
	variables = [R.variable(i) for i in range(len(variables))]
	
	f = {}

	f[ATP] = 1+MPT
	f[BAX] = CASP8 * (1+BCL2)
	f[BCL2] = NFKB1
	f[CASP3] = (1+XIAP) * apoptosome
	f[CASP8] = ((1+DISC_TNF)*(1+DISC_FAS)*CASP3*(1+cFLIP) + (1+DISC_TNF)*DISC_FAS*(1+cFLIP) +(1+DISC_TNF)*(1+DISC_FAS)*CASP3*(1+cFLIP) + (1+DISC_TNF)*DISC_FAS*(1+cFLIP))*DISC_TNF*(1+cFLIP) +  ((1+DISC_TNF)*(1+DISC_FAS)*CASP3*(1+cFLIP) + (1+DISC_TNF)*DISC_FAS*(1+cFLIP) +(1+DISC_TNF)*(1+DISC_FAS)*CASP3*(1+cFLIP) + (1+DISC_TNF)*DISC_FAS*(1+cFLIP)) + DISC_TNF*(1+cFLIP)
	f[Cyt_c] = MOMP
	f[DISC_FAS]  = FASL*FADD
	f[DISC_TNF]  = TNFR*FADD
	f[FADD]  = FADD
	f[FASL]  = FASL
	f[IKK]  = RIP1ub
	f[MOMP]  = ((1+BAX)*MPT)*BAX + ((1+BAX)*MPT) + BAX
	f[MPT]  = (1+BCL2)*ROS
	f[NFKB1]  = IKK*(1+CASP3)
	f[NonACD]  = 1+ATP
	f[RIP1]  = (1+TNFR)*DISC_FAS*(1+CASP8)*TNFR*(1+CASP8) + (1+TNFR)*DISC_FAS*(1+CASP8) + TNFR*(1+CASP8)
	f[RIP1K]  = RIP1
	f[RIP1ub]  = RIP1*cIAP
	f[ROS]  = (1+RIP1K)*MPT*mROS * RIP1K*mROS + RIP1K*mROS + (1+RIP1K)*MPT*mROS
	f[SMAC]  = MOMP
	f[TNF]  = (1+TNF)*NFKB1*TNF+(1+TNF)*NFKB1+TNF
	f[TNFR]  = TNF
	f[XIAP]  = (1+SMAC)*mXIAP
	f[apoptosome]  = ATP*Cyt_c*(1+XIAP)
	f[cFLIP]  = NFKB1
	f[cIAP]  = (1+SMAC)*mcIAP
	f[mROS]  = 1+NFKB1
	f[mXIAP]  = NFKB1
	f[mcIAP]  = NFKB1
	
	ideal_generators = [f[key]+key for key in f]
	print(ideal_generators)
	#ideal_generators = [f1+RAS, f2+MOMP, f3+CAS3]
	classifier_survival = NFKB1
	classifier_Apoptosis = CASP3
	classifier_death = ((1+NonACD)*CASP3)*NonACD + ((1+NonACD)*CASP3) + NonACD
	
	print("Start computing...")
	varphi = classifier_survival
	solutions = compute_min_repr(varphi, variables, ideal_generators)
	print("There are "+str(len(solutions))+" solutions")
	print("The solutions are:")

	# Print solutions
	all_components = Set([])
	for sol in solutions:
		print(sol.variables())
		all_components = all_components.union(Set(map(str, sol.variables())))

	print("All componnents ("+ str(len(list(all_components))) + " of " +str(len(variables)) +" components ) used in classifiers.: \n")
	print(list(all_components))
	print("Components  not used in minimal classifiers:\n")
	print(Set(map(str, variables)).difference(all_components))
	print_to_file(solutions,  variables, ideal_generators, varphi, "output")
	
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
