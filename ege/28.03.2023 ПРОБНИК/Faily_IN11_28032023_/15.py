for a in range(10000):
    f = True
    for x in range(10000):
        r = int(x & 116 != 0 or x & 92 != 0) <= int(int(x & 69 == 0) <= int(x & a != 0))
        if not r:
            f = False
            break
    if f:
        print(a)
        break
