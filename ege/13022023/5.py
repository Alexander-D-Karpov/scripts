def f(n, m):
    n = str(n)
    m = str(m)
    s = str(int(n[0]) + int(m[0]))
    s += str(int(n[1]) + int(m[1]))
    return int(s[-4:-1])


r = []
for x in range(100, 1000):
    for y in range(100, 1000):
        if f(x, y) == 2:
            r.append(x)

print(max(r))
