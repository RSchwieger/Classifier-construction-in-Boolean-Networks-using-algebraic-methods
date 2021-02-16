

import logging
from typing import List

log = logging.getLogger(__name__)


class Phenotype:
    space: dict

    def __init__(self, conjunction: str):
        self.space = dict([(k[1:], 0) if k.startswith("!") else (k, 1) for k in conjunction.split("&")])

    def __call__(self, state: dict) -> int:
        return int(all(state[k] == self.space[k] for k in self.space))


def validate_solution(steady_states: List[str], phenotype: str, classifier: str, throw: bool = False):
    """
    phenotype = v0*v1*v10*v11*v12*v2*v3*v4*v5*v6*v7*v8*v9
    steady_states = ['0000000000000', '1111111111111']
    classifier = v0&!v2
    """

    pheno = Phenotype(phenotype)

    for state in steady_states:
        s = {f"v{i}": int(k) for i, k in enumerate(state)}

        are_equal = pheno(s) == eval(classifier, s) % 2

        if not are_equal:
            message = f"phenotype and classifier disagree: {phenotype=}, {classifier=}, state={state}"

            if throw:
                raise ValueError(message)
            else:
                log.error(message)


if __name__ == "__main__":

    phenotype = 'v10&v2&!v4&!v5&!v6&v7&v8'
    classifier = 'v0 + v10 + 1'
    states = ["01100111010", "01110101011", "11001111001", "11111000111"]

    pheno = Phenotype(conjunction=phenotype)

    for state in states:
        s = {f"v{i}": int(k) for i, k in enumerate(state)}

        print(pheno(s))
        print(eval(classifier, s) % 2)
        print()


