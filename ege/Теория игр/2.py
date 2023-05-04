def f(x, p, pre):
    if x >= 62 or p > 3:
        return p == 3
    s = []
    if pre != 1:
        s.append(f(x + 1, p + 1, 1))
    if pre != 2:
        s.append(f(x + 2, p + 1, 2))
    if pre != 3:
        s.append(f(x * 3, p + 1, 3))
    if p % 2 == 1:
        return all(s)
    return any(s)


rss = 0
for s in range(1, 62):
    if f(s, 1, 0):
        rss = s
        print(s)


def f2(x, p, pre):
    if x >= 62 or p > 4:
        return p == 4
    s = []
    if pre != 1:
        s.append(f2(x + 1, p + 1, 1))
    if pre != 2:
        s.append(f2(x + 2, p + 1, 2))
    if pre != 3:
        s.append(f2(x * 3, p + 1, 3))
    if p % 2 == 0:
        return all(s)
    return any(s)


rs2 = []
for s in range(1, 62):
    if f2(s, 1, 0):
        rs2.append(s)

print(min(rs2), max(rs2))


def f3(x, p, pre):
    if x >= 62 or p > 5:
        return p in [3, 5]
    s = []
    if pre != 1:
        s.append(f3(x + 1, p + 1, 1))
    if pre != 2:
        s.append(f3(x + 2, p + 1, 2))
    if pre != 3:
        s.append(f3(x * 3, p + 1, 3))
    if p % 2 == 1:
        return all(s)
    return any(s)


for s in range(1, 62):
    if f3(s, 1, 0):
        if s != rss:
            print(s)
