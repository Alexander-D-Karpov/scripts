def d(n):
    r = []
    for i in range(15, n - 1, 15):
        if n % i == 0:
            r.append(i)
    return r


c = 0

for x in range(66730, 67001):
    if len(d(x)) == 3:
        print(x, d(x))

print(c)
