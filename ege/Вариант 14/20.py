def f(x, y, p):
    if x + y >= 59 or p > 5:
        return p in [3, 5]
    if p % 2 == 1:
        return (
            f(x + 2, y, p + 1)
            or f(x * 3, y, p + 1)
            or f(x, y + 2, p + 1)
            or f(x, y * 3, p + 1)
        )
    return (
        f(x + 2, y, p + 1)
        and f(x * 3, y, p + 1)
        and f(x, y + 2, p + 1)
        and f(x, y * 3, p + 1)
    )


for s in range(1, 54):
    if f(5, s, 1):
        print(s)
