

import sys
import logging
import argparse
from sage.all import TermOrder
from sage.all import BooleanPolynomialRing

from bnet_parser import parse_bnet_file
from bnet_parser import boolean_formula_to_boolean_polynomial
from compute_minimal_normal_forms import compute_min_repr
from tex_writer import write_tex_table

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")
log = logging.getLogger()


if __name__ == "__main__":

    help_text = f"""
    command line tool for classifier construction of boolean networks using algebraic methods
    """

    parser = argparse.ArgumentParser(description=help_text)
    parser.add_argument("--bnet", type=str, nargs=1, required=True, help="path to bnet file")
    parser.add_argument("--classifier", type=str, nargs=1, required=True, help="boolean expression that describes the classifier")
    parser.add_argument("--output", type=str, nargs=1, default=[], help="file name for output tex table")
    args = parser.parse_args()

    polys = parse_bnet_file(fname=args.bnet[0])

    log.info("classifier construction of boolean networks using algebraic methods")
    log.info(f"bnet file = {args.bnet[0]}")

    R = BooleanPolynomialRing(names=sorted(polys), order=TermOrder("lex"))
    R.inject_variables()
    variables = [R.variable(i) for i in range(len(polys))]
    log.info(f"variables = {variables}")

    for name, poly in polys.items():
        log.info(f"f__{name} = {poly}")
        exec(f"f__{name} = {poly}")

    ideal_generators = None
    ideal_generator_expr = ', '.join(f'f__{name} + {name}' for name in polys)
    log.debug(f"ideal_generator_expr = [{ideal_generator_expr}]")

    exec(f"ideal_generators = [{ideal_generator_expr}]")
    log.info(f"ideal_generators = {ideal_generators}")

    varphi = None
    formula = args.classifier[0].replace("!", "~")
    log.debug(f"varphi = {boolean_formula_to_boolean_polynomial(formula=formula)}")

    try:
        exec(f"varphi = {boolean_formula_to_boolean_polynomial(formula=formula)}")
    except NameError as e:
        log.error(f"classifier references unknown variable: {e}")
        exit()

    log.info(f"varphi = {varphi}")

    solutions = compute_min_repr(varphi, variables, ideal_generators)
    log.info(f"There are {len(solutions)} solutions")
    log.info("The solutions are:")
    for sol in solutions:
        log.info(sol.set())

    if args.output:
        write_tex_table(solutions, variables, ideal_generators, varphi, args.output[0])
        log.info(f"created {args.output[0]}")





