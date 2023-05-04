def check_n(n):
    r = []
    for x in range(1, int(n**0.5) + 1):
        for y in range(x, int(n**0.5) + 1):
            if x**2 + y**2 == n:
                r.append((x, y))
            if len(r) > 1:
                return []

    return r


for x in range(164361, 164424):
    n = check_n(x)
    if n:
        print(n[0], x)
