for A in range(1000):
    f = True
    for x in range(1, 1000):
        for y in range(1, 1000):
            r = (x + y <= 32) or (y <= x + 4) or (y >= A)
            if not r:
                f = False
        if not f:
            break
    if f:
        print(A)
