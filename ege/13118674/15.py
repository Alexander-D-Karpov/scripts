for A in range(1000):
    f = True
    for x in range(1000):
        for y in range(1000):
            r = (x + 2 * y < A) or (y > x) or (x > 20)
            if not r:
                f = False
                break
        if not f:
            break
    if f:
        print(A)
        break
