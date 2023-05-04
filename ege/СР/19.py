def f(x, y, p=1):
    if x + y >= 101 or p > 3:
        return p == 3

    return any(
        [f(x + 1, y, p + 1), f(x * 2, y, p + 1), f(x, y + 1, p + 1), f(x, y * 2, p + 1)]
    )


for s in range(1, 94):
    if f(s, 7):
        print(s)
