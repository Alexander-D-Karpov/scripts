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
    d.remove(1)
    d.remove(n)
    return sum(d) > 460000


for i in range(135790, 163228 + 1):
    if is_d(i):
        print(i)
        d = divisors(i)
        d.remove(1)
        d.remove(i)
        print(len(d), sum(d))
        print()
