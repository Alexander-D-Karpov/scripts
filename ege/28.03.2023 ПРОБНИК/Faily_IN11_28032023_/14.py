for p in range(5, 1000):
    for x in range(p):
        for y in range(p):
            for z in range(p):
                if y < p and x < p and z < p:
                    n1 = y * p**2 + 4 * p + y
                    n2 = y * p**2 + 6 * p + 5
                    n3 = x * p**3 + z * p**2 + 3 * p + 3
                    if n1 + n2 == n3:
                        print(x * p**2 + y * p * z)
