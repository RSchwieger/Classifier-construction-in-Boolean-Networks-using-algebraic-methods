

from sage.all import *
from compute_minimal_normal_forms import compute_min_repr



if __name__ == "__main__":
    variables = ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10", "x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19", "x20", "x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29", "x30", "x31", "x32", "x33", "x34", "x35", "x36", "x37", "x38"]

    R = BooleanPolynomialRing(names=variables, order=TermOrder('lex'))
    R.inject_variables()
    variables = [R.variable(i) for i in range(len(variables))]
    
    f1 = 1+x6*x11+x3*x30
    f2 = x8*x20*(1+x7)
    f3 = x2*x23+x36+1
    f4 = x20+x7*x11
    f5 = x6+x15*(1+x7)+x6*x3*(1+x7)
    f6 = x9*(1+x7)
    f7 = x11*x8*(1+x2)
    f8 = (1+x3)*(x10+x4+x4*x10)+x22
    f9 = (1+x7)*(x8+x6+x6*x8)+x30
    f10 = x38*x7+x3*x34
    f11 = (x7+x11+x7*x11) * (1+x5)
    f12 = (x1+1)*(x15+x3)
    f13 = (x19+1)*(x16+x1)
    f14 = (x1+1)*(x19+x11)+x3
    f15 = x6+x16*(1+x7)+x20*x3*(1+x7)+1
    f16 = x3*x1*(1+x2)
    f17 = (x3+x18*x20) * (1+x5)
    f18 = (x5*x11) * (1+x20) + x36
    f19 = x32*x11*x2+x18+1
    f20 = x21*x11+x1*x35+1
    f21 = x1+x2+x3+x31
    f22 = x3+x7+x11
    f23 = x24+x23*x25
    f24 = x21*x22+x21
    f25 = x23*x1*x2*x3*x5
    f26 = x4*x7*x27*x28*x25
    f27 = x4*x7*x34*x25+x30*x1
    f28 = x2*x7*x26+x3
    f29 = x20*x25*x13*x17+x2*x21
    f30 = x32*x2*x6+x12*x11

    f31 = x32*x33 + x1
    f32 = x31+1
    f33 = x31 + x10 + x37
    f34 = x31*x32+x33

    f35 = x1 + x2*x17+1
    f36 = x31+1
    f37 = x4+1
    f38 = x31*(1+x34)

    
    ideal_generators = [f1+x1,f2+x2,f3+x3,f4+x4,f5+x5,f6+x6,f7+x7,f11+x11,f12+x12,f13+x13,f14+x14,f15+x15,f16+x16,f17+x17,f18+x18, f19+x19,f20+x20, f21+x21, f22+x22, f27+x27, f28+x28, f29+x29, f30+x30, f31+x31, f32+x32, f33+x33, f34+x34, f35+x35, f36+x36, f37+x37, f38+x38]
    classifier = x1+x2*x11*x37
    
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
