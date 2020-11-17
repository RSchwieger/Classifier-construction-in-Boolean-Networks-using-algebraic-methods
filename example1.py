from __future__ import print_function
from sage.all import *
from timeit import default_timer as timer
from compute_minimal_normal_forms import compute_min_repr



if __name__ == "__main__":
    variables = ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10", "x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19", "x20", "x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29", "x30"]

    R = BooleanPolynomialRing(names=variables, order=TermOrder('lex'))
    R.inject_variables()
    variables = [R.variable(i) for i in range(len(variables))]
    
    f1 = 1+x6*x11+x3*x30
    f2 = x1*x5*(1+x7)
    f3 = x2*x3+x6
    f4 = x20+x7*x11
    f5 = x6+x15*(1+x7)+x6*x3*(1+x7)
    f6 = x9*(1+x7)
    f7 = x11*x8*(1+x2)
    f8 = (1+x3)*(x10+x4+x4*x10)+x22
    f9 = (1+x7)*(x8+x6+x6*x8)+x30
    f10 = x10*x7+x3
    f11 = (x7+x11+x7*x11) * (1+x5)
    f12 = (x1+1)*(x2+x3)
    f13 = (x19+1)*(x16+x15)
    f14 = (x1+1)*(x19+x11)+x3
    f15 = x6+x16*(1+x7)+x20*x3*(1+x7)+1
    f16 = x3*x1*(1+x2)
    f17 = (x3+x18*x20) * (1+x5)
    f18 = (x5*x11) * (1+x20)
    f19 = x4*x6*x7
    f20 = x21*x11+x1+1
    f21 = x1+x2+x3
    f22 = x3+x7+x11
    f23 = x24+x23*x25
    f24 = x21*x22+x21
    f25 = x23*x1*x2*x3*x5
    f26 = x4*x7*x27*x28*x25
    f27 = x4*x7*x28*x25+x30*x1
    f28 = x2*x7*x26+x3
    f29 = x20*x25*x13*x17+x2*x21
    f30 = x29*x2*x6+x12*x11

    
    ideal_generators = [f1+x1,f2+x2,f3+x3,f4+x4,f5+x5,f6+x6,f7+x7,f8+x8,f9+x9,f10+x10,f11+x11,f12+x12,f13+x13,f14+x14,f15+x15,f16+x16,f17+x17,f18+x18, f19+x19,f20+x20, f21+x21, f22+x22, f23+x23, f24+x24, f25+x25, f26+x26, f27+x27, f28+x28, f29+x29, f30+x30]
    classifier = x1*x3*x7+x11+x25*x24*x23+x30
    
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
