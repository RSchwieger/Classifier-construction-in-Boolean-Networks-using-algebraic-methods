from sage.all import *
from timeit import default_timer as timer
from compute_minimal_normal_forms import compute_min_repr, print_to_file


if __name__ == "__main__":
    variables = ['ATP', 'BAX', 'BCL2', 'CASP3', 'CASP8', 'Cytc', 'DISC_FAS', 'DISCTNF', 'FADD', 'FASL', 'IKK', 'MOMP', 'MPT', 'NFKB1', 'RIP1', 'RIP1K', 'RIP1ub', 'ROS', 'SMAC', 'TNF', 'TNFR', 'XIAP', 'apoptosome', 'cFLIP', 'cIAP']

    R = BooleanPolynomialRing(names=variables, order=TermOrder('lex'))
    R.inject_variables()
    variables = [R.variable(i) for i in range(len(variables))]
    
    f = {}

    f[ATP] = 1+MPT
    f[BAX] = CASP8 * (1+BCL2) 
    f[BCL2] = NFKB1
    f[CASP3] = (1+XIAP) * apoptosome
    #f[CASP8] = ((1+DISCTNF)*(1+DISC_FAS)*CASP3*(1+cFLIP) + (1+DISCTNF)*DISC_FAS*(1+cFLIP) +(1+DISCTNF)*(1+DISC_FAS)*CASP3*(1+cFLIP) + (1+DISCTNF)*DISC_FAS*(1+cFLIP))*DISCTNF*(1+cFLIP) +  ((1+DISCTNF)*(1+DISC_FAS)*CASP3*(1+cFLIP) + (1+DISCTNF)*DISC_FAS*(1+cFLIP) +(1+DISCTNF)*(1+DISC_FAS)*CASP3*(1+cFLIP) + (1+DISCTNF)*DISC_FAS*(1+cFLIP)) + DISCTNF*(1+cFLIP)
    f[CASP8] = DISCTNF*DISC_FAS + DISCTNF*CASP3 + DISCTNF*cFLIP + DISC_FAS*CASP3 + DISC_FAS*cFLIP + CASP3*cFLIP + DISCTNF*DISC_FAS*CASP3 + DISCTNF*DISC_FAS*cFLIP + DISCTNF*CASP3*cFLIP + DISC_FAS*CASP3*cFLIP + DISCTNF*DISC_FAS*CASP3 + DISCTNF + DISC_FAS + CASP3
    f[Cytc] = MOMP
    f[DISC_FAS]  = FASL*FADD
    f[DISCTNF]  = TNFR*FADD
    f[FADD]  = FADD
    f[FASL]  = FASL
    f[IKK]  = RIP1ub
    f[MOMP]  = ((1+BAX)*MPT)*BAX + ((1+BAX)*MPT) + BAX
    f[MPT]  = (1+BCL2)*ROS
    f[NFKB1]  = IKK*(1+CASP3)
    # f[RIP1]  = (1+TNFR)*DISC_FAS*(1+CASP8)*TNFR*(1+CASP8) + (1+TNFR)*DISC_FAS*(1+CASP8) + TNFR*(1+CASP8)
    f[RIP1] = TNFR*DISC_FAS + TNFR*CASP8 + DISC_FAS*CASP8 + TNFR*DISC_FAS*CASP8 + TNFR + DISC_FAS
    f[RIP1K]  = RIP1
    f[RIP1ub]  = RIP1*cIAP
    # f[ROS]  = (1+RIP1K)*MPT*NFKB1 * RIP1K*(1+NFKB1) + RIP1K*(1+NFKB1) + (1+RIP1K)*MPT*NFKB1
    f[ROS] = RIP1K*NFKB1 + RIP1K*MPT + NFKB1*MPT + RIP1K*NFKB1*MPT + RIP1K + MPT
    f[SMAC]  = MOMP
    f[TNF]  = TNF
    f[TNFR]  = TNF
    f[XIAP]  = (1+SMAC)*NFKB1
    f[apoptosome]  = ATP*Cytc*(1+XIAP)
    f[cFLIP]  = NFKB1
    # f[cIAP]  = (1+NFKB1)*(1+SMAC)*cIAP * NFKB1*(1+SMAC) + (1+NFKB1)*(1+SMAC)*cIAP + NFKB1*(1+SMAC)
    f[cIAP] = NFKB1*SMAC + NFKB1*cIAP + SMAC*cIAP + NFKB1*SMAC*cIAP + NFKB1 + cIAP
    
    ideal_generators = [f[key]+key for key in f]
    print(ideal_generators)
    #ideal_generators = [f1+RAS, f2+MOMP, f3+CAS3]
    classifier_survival = NFKB1
    classifier_Apoptosis = CASP3
    classifier_NonACD = 1+ATP
    
    print("Start computing...")
    varphi = classifier_Apoptosis # Insert here the classifier you want to compute
    solutions = compute_min_repr(varphi, variables, ideal_generators)
    print("There are "+str(len(solutions))+" solutions")
    print("The solutions are:")

    # Print solutions
    all_components = set([])
    for sol in solutions:
        print(sol.variables())
        all_components = all_components.union(set(map(str, sol.variables())))

    print("All componnents ("+ str(len(list(all_components))) + " of " +str(len(variables)) +" components ) used in classifiers.: \n")
    print(list(all_components))
    print("Components  not used in minimal classifiers:\n")
    print(set(map(str, variables)).difference(all_components))
    print_to_file(solutions,  variables, ideal_generators, varphi, "output")
