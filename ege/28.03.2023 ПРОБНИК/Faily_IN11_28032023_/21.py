def f(p, x, y):
    if x + y >= 47 or p > 5:
        return p in [3, 5]
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
    if p % 2 == 0:
        return any(s)
    return all(s)


for a in range(1, 25):
    if f(1, 22, a):
        print(a)


def f(p, x, y):
    if x + y >= 47 or p > 3:
        return p == 3
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
    if p % 2 == 0:
        return any(s)
    return all(s)


for a in range(1, 25):
    if f(1, 22, a):
        print(a)
