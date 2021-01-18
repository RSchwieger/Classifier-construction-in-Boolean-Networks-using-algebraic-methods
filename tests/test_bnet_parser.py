

from bnet_parser import parse_bnet_str
from bnet_parser import polynomial_tree_to_str


def test_parse_bnet_str():

    fstr = """
    a, 1
    b, 0
    c, a | b
    """

    polys = parse_bnet_str(fstr=fstr)

    assert polys == {"a": 1, "b": 0, "c": "a + b + a*b"}


def test_polynomial_tree_to_str():

    tree = ['|', 'v1', ['&', 'v7', ['~', ['|', 'v2', ['&', 'v4', ['~', 'v1']]]]]]
    poly = polynomial_tree_to_str(tree=tree)

    assert type(poly) == str
