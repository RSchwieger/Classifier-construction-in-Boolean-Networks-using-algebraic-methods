

import logging

from compute_minimal_normal_forms import get_order
from compute_minimal_normal_forms import reduce

log = logging.getLogger(__name__)


def write_tex_table(solutions, variables, ideal, varphi, filename: str):
    """
    Creates a latex table to save the solutions
    """

    with open(filename, "w") as fp:
        fp.write("\\begin{longtable}{| p{.30\\textwidth} | p{.70\\textwidth} |}  \hline"+"\n")
        fp.write("Components & Expression \\\\"+"\n")

        for sol in solutions:
            block_in_order = {str(a):0 for a in variables}
            for a in sol.variables():
                block_in_order[str(a)] = 1
            R, components_in_order = get_order(block_in_order)
            components_in_order = [R.variable(i) for i in range(len(components_in_order))]
            varphi = reduce(varphi, R, ideal)
            fp.write("\\hline"+" \n")
            fp.write(("$"+str(sol.variables()).replace("(", "").replace(")", "").replace(",", "$, $")+"$").replace(", $$", "")+" & "+"$"+str(varphi).replace("*", " \\cdot ").replace("_", "\\_")+"$"+" \\\\"+"\n")
        fp.write("\\caption{"+str(len(solutions))+" different representations}"+"\n")
        fp.write("\\end{longtable}"+"\n")
        fp.close()
