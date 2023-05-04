rrs = [x for x in range(70, 81)]

for A in range(1, 1000):
    f = True
    for x in range(1, 1000):
        r = x % A == 0 or (int(x in rrs) <= int(x % 18 != 0))
        if not r:
            f = False
            break
    if f:
        print(A)
