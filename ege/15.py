def symb(x, y):
    return x + y > 0


res = []

for z in range(10000):
    f = True
    for x in range(1000):
        r = symb(x, z + 1) <= (int(not (symb(x, -7)) <= int(not (symb(x, 7)))))
        if not r:
            f = False
            break
    if f:
        res.append(z)

print(max(res))
