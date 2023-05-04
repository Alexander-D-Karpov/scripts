import math


def divisors(n):
    divs = [1]
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divs.extend([i, n // i])
    divs.extend([n])
    return list(set(divs))


def is_d(n):
    d = divisors(n)
    return len(d) == 5


for i in range(81234, 134690):
    if is_d(i):
        print(i)
        for j in range(2, i):
            if i % j == 0:
                print(j)
        print()
