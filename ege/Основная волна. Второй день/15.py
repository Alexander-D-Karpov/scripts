for a in range(10000):
    s = True
    for x in range(1000):
        for y in range(1000):
            r = (x + y <= 22) or (y <= x - 6) or (y >= a)
            if not r:
                s = False
                break
        if not s:
            break
    if s:
        print(a)
