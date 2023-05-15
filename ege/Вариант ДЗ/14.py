def _(n, p, d=16):
    return n * d ** (p - 1)


r = []

for x in range(16):
    for y in range(16):
        for z in range(1000):
            n1 = _(5, 4) + _(x, 1) + 7
            n2 = _(3, 2) + _(y, 1) + 1
            n3 = _(1, 6, z) + _(2, 5, z) + _(6, 1, z) + 5

            if n1 + n2 == n3:
                print(x, y, z)
                r.append(x * y * z)

print(max(r))
