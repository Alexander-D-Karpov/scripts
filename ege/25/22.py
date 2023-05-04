for i in range(0, 1000001):
    if i == 1000000:
        i = ""
    for j in range(0, 1000001):
        if j == 1000000:
            j = ""
        s = int(f"1{i}5{j}9")
        n = f"1{i}5{j}9"
        if s <= 10**9:
            if s % 21 == 0:
                if all([int(n[x]) > int(n[x - 1]) for x in range(1, len(n))]):
                    print(s, s // 21)
