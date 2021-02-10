

import sys
import logging
import argparse
import signal
import time
import os
import pandas as pd

from sage.all import TermOrder
from sage.all import BooleanPolynomialRing
from sage.all import Ideal

from bnet_parser import parse_bnet_file, parse_bnet_str
from bnet_parser import boolean_formula_to_boolean_polynomial
from compute_minimal_normal_forms import compute_min_repr
from validation import validate_solution
from tex_writer import write_tex_table

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
logging.getLogger("bnet_parser").setLevel(logging.INFO)
log = logging.getLogger()


def timeout(signum, frame):
    print("time's up")
    sys.exit()


if __name__ == "__main__":

    help_text = f"""
    command line tool for classifier construction of boolean networks using algebraic methods
    """

    parser = argparse.ArgumentParser(description=help_text)
    parser.add_argument("--bnet", type=str, nargs=1, help="path to bnet file")
    parser.add_argument("--phenotype", type=str, nargs=1, help="boolean expression that describes the phenotype")
    parser.add_argument("--tex-file", type=str, nargs=1, default=[], help="file name for output tex table")
    parser.add_argument("--timeout", type=int, nargs=1, help="time out in seconds")
    parser.add_argument("--bench-csv", type=str, nargs=1, help="bench mark csv file")
    parser.add_argument("--assert-steady-states", type=str, nargs="+", help="assert that these steady states exist")
    args = parser.parse_args()

    if args.timeout:
        signal.signal(signal.SIGALRM, timeout)
        signal.alarm(args.timeout[0])

    if args.bench_csv:
        RESET = False
        fname = args.bench_csv[0]

        if not os.path.isfile(fname):
            print(f"benchmark file does not exist: {fname=}")
            sys.exit()

        df = pd.read_csv(fname)

        benchmark_keys = ["t_polynomials", "t_ideals", "t_varphi", "t_solutions", "n_solutions"]
        if "done" not in df.columns or RESET:
            for k in benchmark_keys:
                df[k] = None

            df["done"] = False
            df["exception"] = False
            df["constant_classifier"] = False

        indices = df.index[df["done"] == False].tolist()

        if not indices:
            print("we're done")
            sys.exit()

        i = indices[0]
        print(f"working on {fname}:{i}")
        cols = [x for x in df.columns if x not in ["bnet", "phenotype"] + benchmark_keys]
        print(df.loc[i:i, cols])

        bnet = df.at[i, "bnet"]
        phenotype = df.at[i, "phenotype"]

        start = time.time()
        polys = parse_bnet_str(fstr=bnet)
        end = time.time()
        df.at[i, "t_polynomials"] = round(end - start, 2)

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
        df.at[i, "t_ideals"] = round(end - start, 2)

        start = time.time()
        varphi = None
        formula = phenotype.replace("!", "~")
        exec(f"varphi = {boolean_formula_to_boolean_polynomial(formula=formula)}")
        end = time.time()
        df.at[i, "t_varphi"] = round(end - start, 2)

        start = time.time()
        try:
            min_repr = compute_min_repr(varphi, variables, ideal_generators)
        except SystemError:
            df.at[i, "done"] = True
            df.at[i, "exception"] = True
            df.to_csv(fname, index=False)
            print("system error")
            sys.exit(23)
        end = time.time()

        print(min_repr.to_list())

        steady_states = df.at[i, "steady_states"].split(",")
        phenotype_support = df.at[i, "phenotype"].split(",")

        for names in min_repr.to_list():
            # validate_solution(classifier_support=names, steady_states=steady_states, phenotype=phenotype)
            print(names, end="")
            break

        print()

        sys.exit()

        df.at[i, "t_solutions"] = round(end - start, 2)
        df.at[i, "n_solutions"] = len(min_repr.solutions)
        df.at[i, "n_reductions"] = min_repr.n_reductions
        df.at[i, "constant_classifier"] = min_repr.is_constant
        df.at[i, "done"] = True
        df.at[i, "exception"] = False

        df.to_csv(fname, index=False)
        sys.exit(23)

    if args.phenotype and not args.bnet:
        formula = args.phenotype[0].replace("!", "~")
        poly = boolean_formula_to_boolean_polynomial(formula=formula)
        log.info(f"{poly}")

    if args.phenotype and args.bnet:
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

        f__ = []
        for name, poly in polys.items():
            log.info(f"f__{name} = {poly}")
            exec(f"f__{name} = {poly}")
            exec(f"f__.append(f__{name})")

        if args.assert_steady_states:
            print("testing steady states")
            for state in args.assert_steady_states:
                print(f" {state}")
                for i, value in enumerate(state):
                    state = list(map(int, state))
                    assert f__[i](*state) == int(value)

        ideal_generators = None
        ideal_generator_expr = ', '.join(f'f__{name} + {name}' for name in polys)
        log.debug(f"ideal_generator_expr = [{ideal_generator_expr}]")

        exec(f"ideal_generators = [{ideal_generator_expr}]")
        log.info(f"ideal_generators = {ideal_generators}")

        varphi = None
        formula = args.phenotype[0].replace("!", "~")

        try:
            poly = boolean_formula_to_boolean_polynomial(formula=formula)
            exec(f"varphi = {poly}")
            log.debug(f"varphi = {poly}")

        except NameError as e:
            log.error(f"classifier references unknown variable: {e}")
            exit()

        log.info(f"varphi = {str(varphi)[:10]}..")

        min_repr = compute_min_repr(varphi, variables, ideal_generators)

        log.info("The solutions are:")

        for poly in min_repr.to_polynomials():
            log.info(f"{poly}")

        log.info(f"There are {len(min_repr.solutions)} solutions")

        if args.tex_file:
            write_tex_table(min_repr.solutions, variables, ideal_generators, varphi, args.output[0])
            log.info(f"created {args.output[0]}")





