def check_poly(n):
    n = list(map(int, str(n)))
    return all([n[i - 1] % 2 != n[i] % 2 for i in range(1, len(n))])


def dev(n):
    for x in range(n - 1, 1, -1):
        if n % x == 0:
            return x % 7 == 0
    return False


def get_dev(n):
    for x in range(n - 1, 1, -1):
        if n % x == 0:
            return x


for i in range(1_000_000_000, 10_000_000_000):
    if check_poly(i) and dev(i):
        print(i, get_dev(i))
