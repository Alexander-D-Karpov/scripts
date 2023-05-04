for x in range(2):
    for y in range(2):
        for w in range(2):
            for z in range(2):
                r = ((x <= y) == (w <= x)) and (z <= w)
                if r:
                    print(x, w, z, y)
