for x in range(2):
    for y in range(2):
        for z in range(2):
            for w in range(2):
                r = not (y <= w) or (x <= z) or not (x)
                if not r:
                    print(x, w, y, z)
