for l in range(2):
    for x in range(2):
        for y in range(2):
            for w in range(2):
                for z in range(2):
                    f1 = (x or not (y)) == (z <= w)
                    f2 = (not (x) == y) and (z <= w)
                    if f1 == l and y == 1 and f2 == 0 and [x, y, w, z].count(1) >= 2:
                        print(z, x, y, w, "|", int(f1), int(f2))
