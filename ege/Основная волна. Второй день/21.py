def f(x, p):
    if x >= 165 or p > 5:
        return p in [3, 5]

    x = [f(x + 1, p + 1), f(x * 2, p + 1)]
    if p % 2 == 0:
        return any(x)
    return all(x)


for s in range(1, 165):
    if f(s, 1):
        print(s)
