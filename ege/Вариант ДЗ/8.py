from itertools import chain, combinations, permutations


def all_subsets(ss):
    return chain(*map(lambda x: combinations(ss, x), range(0, len(ss) + 1)))


c = 0

for subset in all_subsets(list(range(1, 10))):
    if sum(subset) == 10:
        c += len(list(permutations(subset)))
        print(subset)
print(c)
