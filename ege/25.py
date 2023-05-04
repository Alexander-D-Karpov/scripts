def is_prime(n):
    for i in range(2, int(n**0.5) + 2):
        if n % i == 0:
            return False
    return True


primes = []
for i in range(2, 500_000):
    if is_prime(i):
        primes.append(i)


def get_dev(n):
    res = []
    for i in range(2, int(n**0.5) + 2):
        if n % i == 0 and i in primes:
            res.append(i)
    return res


for i in range(124729, 500_001):
    s = get_dev(i)
    if len(s) >= 4:
        p = []
        for j in range(1, len(s)):
            p.append(s[j] - s[j - 1])
        if len(list(set(p))) == 1:
            print(i, len(s) * p[0])
