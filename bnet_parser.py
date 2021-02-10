

import logging

log = logging.getLogger(__name__)

try:
    import sage.logic.propcalc as propcalc
except Exception as e:
    log.error(e)


def parse_bnet_file(fname: str) -> dict:

    with open(fname, "r") as fp:
        fstr = fp.read()

    return parse_bnet_str(fstr=fstr)


def parse_bnet_str(fstr: str) -> dict:

    newline = "$" if "$" in fstr else "\n"
    lines = fstr.split(newline)

    lines = [x.strip() for x in lines]
    lines = [x for x in lines if x]
    lines = [x for x in lines if not x.startswith("#")]

    formulas = {}
    for line in lines:
        name, eq = line.split(",")

        if name == "targets":
            continue

        formulas[name.strip()] = eq.strip().replace("!", "~")

    polynomials = convert_formulas_to_polynomials(formulas=formulas)

    return polynomials


def formula_tree_to_polynomial_tree(tree: list) -> list:

    if type(tree) != list:
        return str(tree)

    operator = tree[0]

    if operator == "|":
        assert len(tree) == 3

        tree[0] = "+"
        a = formula_tree_to_polynomial_tree(tree[1])
        b = formula_tree_to_polynomial_tree(tree[2])
        tree[1] = a
        tree[2] = b
        tree.append(["*", a, b])

    elif operator == "&":
        assert len(tree) == 3

        tree[0] = "*"
        tree[1] = formula_tree_to_polynomial_tree(tree[1])
        tree[2] = formula_tree_to_polynomial_tree(tree[2])

    elif operator == "~":
        assert len(tree) == 2

        tree[0] = "+"
        a = formula_tree_to_polynomial_tree(tree[1])
        tree[1] = 1
        tree.append(a)

    else:
        raise ValueError(f"unknown operator: {operator}")

    return tree


def polynomial_tree_to_str(tree: list) -> str:

    if type(tree) != list:
        return str(tree)

    operator = tree[0]

    if operator == "+":

        branches = [polynomial_tree_to_str(x) for x in tree[1:]]
        return " + ".join(branches)

    elif operator == "*":

        branches = [f"({polynomial_tree_to_str(x)})" if type(x) == list else f"{polynomial_tree_to_str(x)}" for x in tree[1:]]
        return " * ".join(branches)

    else:
        raise ValueError(f"unknown operator: {operator}")


def boolean_formula_to_boolean_polynomial(formula: str) -> str:

    if formula in "01":
        return formula

    f = propcalc.formula(formula)
    tree = f.full_tree()
    log.debug(f"tree = {tree}")

    if len(tree) == 1:
        return tree[0]

    polynomial_tree = formula_tree_to_polynomial_tree(tree=tree)
    log.debug(f"polynomial_tree = {polynomial_tree}")

    poly = polynomial_tree_to_str(tree=polynomial_tree)
    log.debug(f"polynomial_str = {poly}")

    return poly


def convert_formulas_to_polynomials(formulas: dict) -> dict:
    return {name: boolean_formula_to_boolean_polynomial(formula=formula) for name, formula in formulas.items()}
