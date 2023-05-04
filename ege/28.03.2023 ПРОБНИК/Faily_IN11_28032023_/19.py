def f(p, x, y):
    if x + y >= 47 or p > 2:
        return p == 2
    s = []
    if x == y:
        for i in range(1, 4):
            s.append(f(p + 1, x + i, y))
        for i in range(1, 4):
            s.append(f(p + 1, x, y + i))
    elif x > y:
        for i in range(1, 4):
            s.append(f(p + 1, x + i, y))
        s.append(f(p + 1, x, y * 2))
    else:
        for i in range(1, 4):
            s.append(f(p + 1, x, y + i))
        s.append(f(p + 1, x * 2, y))
    if p % 2 == 1:
        return any(s)
    return all(s)


res = []

for a in range(47):
    for b in range(47):
        if f(1, a, b):
            res.append(a + b)
print(min(res))
