for x in range(2):
    for y in range(2):
        for w in range(2):
            for z in range(2):
                r = (w == y) or ((not (x) <= z) and (not (z) <= y))
                if not r:
                    print(y, z, w, x)
