for x in range(2):
    for y in range(2):
        for z in range(2):
            r = x <= y and z
            if not r:
                print(y, x, z)
