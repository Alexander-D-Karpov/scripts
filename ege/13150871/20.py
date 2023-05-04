def f(x, p):
    if x >= 41 or p > 4:
        return p == 4

    s = [f(x + 1, p + 1), f(x + 5, p + 1), f(x * 3, p + 1)]
    if p % 2 == 1:
        return any(s)
    return all(s)


for s in range(1, 41):
    if f(s, 1):
        print(s)
