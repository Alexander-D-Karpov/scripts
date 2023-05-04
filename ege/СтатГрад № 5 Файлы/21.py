def f(x, y, p=1):
    if x >= 48 or y >= 48 or p > 3:
        return p == 3
    s = []
    if x > y:
        s.append(f(x, y * 2, p + 1))
        for i in range(1, 4):
            s.append(f(x + i, y, p + 1))
    elif y > x:
        s.append(f(x * 2, y, p + 1))
        for i in range(1, 4):
            s.append(f(x, y + i, p + 1))
    else:
        for i in range(1, 4):
            s.append(f(x + i, y, p + 1))

        for i in range(1, 4):
            s.append(f(x, y + i, p + 1))
    if p % 2 == 0:
        return any(s)
    return all(s)


for x in range(1, 48):
    if f(x, 39):
        print(x)

print("---")


def f(x, y, p=1):
    if x >= 48 or y >= 48 or p > 5:
        return p in [3, 5]
    s = []
    if x > y:
        s.append(f(x, y * 2, p + 1))
        for i in range(1, 4):
            s.append(f(x + i, y, p + 1))
    elif y > x:
        s.append(f(x * 2, y, p + 1))
        for i in range(1, 4):
            s.append(f(x, y + i, p + 1))
    else:
        for i in range(1, 4):
            s.append(f(x + i, y, p + 1))

        for i in range(1, 4):
            s.append(f(x, y + i, p + 1))
    if p % 2 == 0:
        return any(s)
    return all(s)


for x in range(1, 48):
    if f(x, 39):
        print(x)
