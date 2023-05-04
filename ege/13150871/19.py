def f(x, p):
    if x >= 41 or p > 3:
        return p == 3

    s = [f(x + 1, p + 1), f(x + 5, p + 1), f(x * 3, p + 1)]
    return any(s)


for s in range(1, 41):
    if f(s, 1):
        print(s)
        break
