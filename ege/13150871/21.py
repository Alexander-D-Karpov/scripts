def f(x, p):
    if x >= 41 or p > 3:
        return p == 3

    s = [f(x + 1, p + 1), f(x + 5, p + 1), f(x * 3, p + 1)]
    return any(s)


for s in range(1, 41):
    if f(s, 1):
        print(s)

print("---")


def f(x, p):
    if x >= 41 or p > 5:
        return p in [3, 5]

    s = [f(x + 1, p + 1), f(x + 5, p + 1), f(x * 3, p + 1)]
    if p % 2 == 0:
        return any(s)
    return all(s)


for s in range(1, 41):
    if f(s, 1):
        print(s)
