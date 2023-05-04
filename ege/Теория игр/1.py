def f(x, p):
    if x <= 10 or p > 3:
        return p == 3

    s = [f(x // 3, p + 1), f(x - 10, p + 1)]
    # if p % 2 == 1:
    #    return all(s)
    return any(s)


rs = []
for s in range(11, 1000):
    if f(s, 1):
        rs.append(s)
print(1, max(rs))


def f2(x, p):
    if x <= 10 or p > 4:
        return p == 4

    s = [f2(x // 3, p + 1), f2(x - 10, p + 1)]
    if p % 2 == 0:
        return all(s)
    return any(s)


rs2 = []
for s in range(11, 1000):
    if f2(s, 1):
        rs2.append(s)
print(2, min(rs2), max(rs2))


def f3(x, p):
    if x <= 10 or p > 5:
        return p in [3, 5]

    s = [f3(x // 3, p + 1), f3(x - 10, p + 1)]
    if p % 2 == 1:
        return all(s)
    return any(s)


def f32(x, p):
    if x <= 10 or p > 3:
        return p == 3

    s = [f32(x // 3, p + 1), f32(x - 10, p + 1)]
    if p % 2 == 1:
        return all(s)
    return any(s)


rs3 = []
res32 = []


for s in range(11, 1000):
    if f32(s, 1):
        res32.append(s)

for s in range(11, 1000):
    if f3(s, 1):
        rs3.append(s)
print(3, len(rs3) - len(res32))
