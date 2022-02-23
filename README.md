# example: classifiers for phenotypes

To run the script use:
```
python3 groebner.py --bnet n7s3.bnet --phenotype "v4 & !v6"
```

# example: steady states

To run the script use:
```
python3 groebner.py --bnet n7s3.bnet --steady-states
```


# bnet format
Syntax for `.bnet` files and classifier definition is
 * `|` means disjunction 
 * `&` means conjunction
 * `!` means negation


# requirements

The main requirement is SAGE:
 * https://www.sagemath.org/


# docker

build image:
```
docker build -t rschwieger .
```

run image:
```
docker run -v $(pwd):/media -it rschwieger
```
 
# about the algorithm

The code implements the algorithm proposed in 

> Schwieger, Robert, Matías R. Bender, Heike Siebert, and Christian Haase. "Classifier construction in Boolean networks using algebraic methods." In _International Conference on Computational Methods in Systems Biology_, pp. 210-233. Springer, Cham, 2020.
> https://doi.org/10.1007/978-3-030-60327-4_12


