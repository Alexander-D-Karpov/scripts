r = {}


def f(n):
    if n in r:
        return r[n]
    if n < 2:
        return 7
    k = 7 * f(n - 2)
    r[n] = k
    return k


for x in range(12950):
    f(x)


print(f(12950) / 7**6473)
