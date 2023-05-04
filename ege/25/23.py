for i in range(1, 100000):
    n = str(i)
    s = i
    if s % 103 == 0:
        if all([int(n[x]) > int(n[x - 1]) for x in range(1, len(n))]):
            print(i, i // 103)
