def f(x, y, p):
    if x + y == 0 or p > 5:
        return p in [3, 5]

    s = []
    if x >= 3 and y >= 3:
        s.append(f(x - 3, y - 3, p + 1))
    if x and x % 2 == 0:
        s.append(f(x // 2, x // 2, p + 1))
    if y and y % 2 == 0:
        s.append(f(y // 2, y // 2, p + 1))

    if not s:
        return p in [3, 5]

    if p % 2 == 0:
        return all(s)
    return any(s)


for k in range(1000):
    if f(20, k, 1):
        print(k)
