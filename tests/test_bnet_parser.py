

from bnet_parser import parse_bnet_str
from bnet_parser import polynomial_tree_to_str, formula_tree_to_polynomial_tree


def test_parse_bnet_str():

    text = """
    a, 1
    b, 0
    c, a | b
    """

    polys = parse_bnet_str(fstr=text)

    assert polys == {"a": 1, "b": 0, "c": "a + b + a*b"}


def test_polynomial_tree_to_str():

    expression_tree = ['|', 'v1', ['&', 'v7', ['~', ['|', 'v2', ['&', 'v4', ['~', 'v1']]]]]]
    polynomial_tree = formula_tree_to_polynomial_tree(tree=expression_tree)

    assert 2 == 1


def test_disjunction():
    expression_tree = ['|', 'v1', 'v2']
    polynomial_tree = formula_tree_to_polynomial_tree(tree=expression_tree)
    poly = polynomial_tree_to_str(tree=polynomial_tree)

    assert poly == "v1 + v2 + v1 * v2"


def test_repeated_disjunction():
    expression_tree = ['|', ['|', 'v1', 'v2'], "v3"]
    polynomial_tree = formula_tree_to_polynomial_tree(tree=expression_tree)

    assert polynomial_tree == ['+', ['+', 'v1', 'v2', ['*', 'v1', 'v2']], 'v3', ['*', ['+', 'v1', 'v2', ['*', 'v1', 'v2']], 'v3']]
