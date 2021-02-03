

import sys
import logging
import argparse
import signal
import time
import os
import json
from collections import defaultdict
import pandas as pd

from sage.all import TermOrder
from sage.all import BooleanPolynomialRing
from sage.all import Ideal

from bnet_parser import parse_bnet_file, parse_bnet_str
from bnet_parser import boolean_formula_to_boolean_polynomial
from compute_minimal_normal_forms import compute_min_repr
from tex_writer import write_tex_table

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
log = logging.getLogger()


def timeout(signum, frame):
    raise Exception("time's up")


if __name__ == "__main__":

    help_text = f"""
    command line tool for classifier construction of boolean networks using algebraic methods
    """

    parser = argparse.ArgumentParser(description=help_text)
    parser.add_argument("--bnet", type=str, nargs=1, help="path to bnet file")
    parser.add_argument("--phenotype", type=str, nargs=1, help="boolean expression that describes the phenotype")
    parser.add_argument("--tex-file", type=str, nargs=1, default=[], help="file name for output tex table")
    parser.add_argument("--timeout", type=int, nargs=1, help="time out in seconds")
    parser.add_argument("--bench", type=str, nargs=1, help="bench mark json file")
    args = parser.parse_args()

    if args.timeout:
        signal.signal(signal.SIGALRM, timeout)
        signal.alarm(args.timeout[0])

    if args.bench:
        data = defaultdict(list)
        data["file_name"].append(args.bench[0])

        with open(args.bench[0], "r") as fp:
            bench = json.load(fp)

        bnet = bench.pop("bnet")
        phenotypes = bench.pop("phenotype")

        start = time.time()
        polys = parse_bnet_str(fstr=bnet)
        end = time.time()
        log.info(f"computation of polynomials: {end - start:.2}")
        data["t_polynomials"].append(end - start)

        for k, v in bench.items():
            data[k].append(v)

        R = BooleanPolynomialRing(names=sorted(polys), order=TermOrder("lex"))
        R.inject_variables()
        variables = [R.variable(i) for i in range(len(polys))]

        for name, poly in polys.items():
            exec(f"f__{name} = {poly}")

        start = time.time()
        ideal_generators = None
        ideal_generator_expr = ', '.join(f'f__{name} + {name}' for name in polys)
        exec(f"ideal_generators = [{ideal_generator_expr}]")
        end = time.time()
        data["t_ideals"].append(end - start)

        start = time.time()
        varphi = None
        formula = phenotypes.replace("!", "~")
        exec(f"varphi = {boolean_formula_to_boolean_polynomial(formula=formula)}")
        end = time.time()
        data["t_varphi"].append(end - start)

        start = time.time()
        solutions = compute_min_repr(varphi, variables, ideal_generators)
        end = time.time()
        data["t_solutions"].append(end - start)

        df = pd.DataFrame(data=data)
        fname = "benchmark.csv"

        if os.path.isfile(fname):
            df.to_csv(fname, mode="a", index=False, header=False)
        else:
            df.to_csv(fname, index=False)

    if args.phenotype:
        log.info("constructing classifiers for phenotype")

        start = time.time()
        polys = parse_bnet_file(fname=args.bnet[0])
        end = time.time()
        log.info(f"computation of polynomials: {end-start:.2}")

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
        formula = args.phenotype[0].replace("!", "~")
        log.debug(f"varphi = {boolean_formula_to_boolean_polynomial(formula=formula)}")

        try:
            exec(f"varphi = {boolean_formula_to_boolean_polynomial(formula=formula)}")
        except NameError as e:
            log.error(f"classifier references unknown variable: {e}")
            exit()

        log.info(f"varphi = {str(varphi)[:10]}..")

        solutions = compute_min_repr(varphi, variables, ideal_generators)

        log.info("The solutions are:")

        for sol in solutions:
            log.info(f"{sol.set()[:20]}..")
            break

        log.info(f"There are {len(solutions)} solutions")

        if args.tex_file:
            write_tex_table(solutions, variables, ideal_generators, varphi, args.output[0])
            log.info(f"created {args.output[0]}")





