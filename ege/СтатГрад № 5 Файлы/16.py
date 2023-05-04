fs = {}


def f(n):
    if f in fs:
        return fs[f]
    if n > 1000000:
        return n
    k = n + f(2 * n)
    fs[f] = k
    return k


def g(n):
    return f(n) / n


for i in range(1000000, 1, -1):
    f(i)

c = 0
for i in range(1, 100000):
    if g(i) == g(1000):
        print(i)

print(c)
