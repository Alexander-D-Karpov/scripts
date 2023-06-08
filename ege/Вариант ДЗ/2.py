for x in range(2):
    for y in range(2):
        for w in range(2):
            for z in range(2):
                r = (int(x or y) <= int(x != w)) != (int(x and z) <= int(y == w))
                if r:
                    print(w, x, y, z)
