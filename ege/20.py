def f(x, y, p):
    if x + y == 0 or p > 4:
        return p == 4

    s = []
    if x >= 3 and y >= 3:
        s.append(f(x - 3, y - 3, p + 1))
    if x and x % 2 == 0:
        s.append(f(x // 2, x // 2, p + 1))
    if y and y % 2 == 0:
        s.append(f(y // 2, y // 2, p + 1))

    if not s:
        return p == 4

    if p % 2 == 1:
        return all(s)
    return any(s)


for k in range(100):
    if f(32, k, 1):
        print(k)
