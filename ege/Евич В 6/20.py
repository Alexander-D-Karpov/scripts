def f(x, y, p=1):
    if x + y >= 84 or p > 4:
        return p == 4
    res = [
        f(x + 1, y, p + 1),
        f(x, y + 1, p + 1),
        f(x + y * 2, y, p + 1),
        f(x, y + x * 2, p + 1),
    ]
    if p % 2 == 0:
        return all(res)
    return any(res)


for s in range(1, 76):
    if f(8, s):
        print(s)
