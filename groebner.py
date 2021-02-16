

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
    raise TimeoutError


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
            log.info(f"benchmark file does not exist: {fname=}")
            sys.exit()

        df = pd.read_csv(fname)

        benchmark_keys = ["t_polynomials", "t_ideals", "t_varphi", "t_solutions", "n_solutions", "avg_size"]
        if "is_done" not in df.columns or RESET:
            for k in benchmark_keys:
                df[k] = None

            df["is_done"] = False
            df["has_crashed"] = False
            df["reached_timeout"] = False
            df["is_constant"] = False

        indices = df.index[df["is_done"] == False].tolist()

        if not indices:
            log.info("we're done")
            sys.exit()

        i = indices[0]
        log.info(f"working on {fname}:{i}")
        cols = [x for x in df.columns if x not in ["bnet", "phenotype"] + benchmark_keys]
        log.info(df.loc[i:i, cols])

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
        ideal_generator_expr = ', '.join(f'f__{name} + {name}' for name in polys)
        ideal_generators = eval(f"[{ideal_generator_expr}]")
        end = time.time()
        df.at[i, "t_ideals"] = round(end - start, 2)

        start = time.time()

        formula = phenotype.replace("!", "~")
        varphi = eval(f"{boolean_formula_to_boolean_polynomial(formula=formula)}")
        end = time.time()
        df.at[i, "t_varphi"] = round(end - start, 2)

        start = time.time()

        try:
            min_repr = compute_min_repr(varphi, variables, ideal_generators)

        except SystemError:
            df.at[i, "is_done"] = True
            df.at[i, "has_crashed"] = True
            df.to_csv(fname, index=False)
            print("system error")
            sys.exit(23)

        except TimeoutError:
            df.at[i, "is_done"] = True
            df.at[i, "reached_timeout"] = True
            df.to_csv(fname, index=False)
            print("time out")
            sys.exit(23)

        except RuntimeError:
            df.at[i, "is_done"] = True
            df.at[i, "has_crashed"] = True
            df.to_csv(fname, index=False)
            print("runtime error")
            sys.exit(23)

        end = time.time()

        steady_states = df.at[i, "steady_states"].split(",")
        phenotype_support = df.at[i, "phenotype"].split(",")

        """
        for poly in min_repr.to_polynomials():
            validate_solution(classifier=str(poly), steady_states=steady_states, phenotype=phenotype)
        """

        df.at[i, "t_solutions"] = round(end - start, 2)
        df.at[i, "n_solutions"] = len(min_repr.solutions)
        df.at[i, "n_reductions"] = min_repr.n_reductions
        df.at[i, "is_constant"] = min_repr.is_constant
        df.at[i, "avg_size"] = min_repr.average_size()
        df.at[i, "is_done"] = True

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

        ideal_generators = None
        ideal_generator_expr = ', '.join(f'f__{name} + {name}' for name in polys)
        log.debug(f"ideal_generator_expr = [{ideal_generator_expr}]")

        exec(f"ideal_generators = [{ideal_generator_expr}]")
        log.debug(f"ideal_generators = {ideal_generators}")

        varphi = None
        try:
            varphi_str = boolean_formula_to_boolean_polynomial(formula=args.phenotype[0].replace("!", "~"))
            exec(f"varphi = {varphi_str}")
            log.debug(f"varphi = {varphi_str}")

        except NameError as e:
            log.error(f"classifier references unknown variable: {e}")
            exit()

        min_repr = compute_min_repr(varphi, variables, ideal_generators)

        log.info("the solutions are:")

        if args.tex_file:
            write_tex_table(min_repr.solutions, variables, ideal_generators, varphi, args.output[0])
            log.info(f"created {args.output[0]}")

        if args.assert_steady_states:

            log.debug("testing steady states")
            for state in args.assert_steady_states:
                log.debug(f" {state}")
                for i, value in enumerate(state):
                    state = list(map(int, state))
                    assert f__[i](*state) == int(value)









