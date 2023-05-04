def f(x, y, p):
    if x == 0 or y == 0 or (x == 1 and y % 2 != 0) or (y == 1 and x % 2 != 0) or p > 3:
        return p == 3
    if y <= x:
        if y % 2 == 0:
            return f(y // 2, y // 2, p + 1) or f(x - 3, y - 3, p + 1)
        if x % 2 == 0:
            return f(x // 2, x // 2, p + 1) or f(x - 3, y - 3, p + 1)
        if y % 2 != 0 and y % 2 != 0:
            return f(x - 3, y - 3, p + 1)
    if x < y:
        if x % 2 == 0:
            return f(x // 2, x // 2, p + 1) or f(x - 3, y - 3, p + 1)
        if y % 2 == 0:
            return f(y // 2, y // 2, p + 1) or f(x - 3, y - 3, p + 1)
        if y % 2 != 0 and y % 2 != 0:
            return f(x - 3, y - 3, p + 1)


for s in range(1, 50):
    if f(32, s, 1):
        print(s)
