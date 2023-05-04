with open("9.txt") as f:
    rows = [list(map(int, x.split())) for x in f.read().splitlines()]
cnt = 0

for row in rows:
    mx = max(row)
    row_c = row.copy()
    del row_c[row.index(mx)]
    if mx < sum(row_c):
        f = True
        for i in range(4):
            n = [i]
            for j in range(4):
                if j not in n:
                    n = [i, j]
                    for c in range(4):
                        if c not in n:
                            n = [i, j, c]
                            for d in range(4):
                                if d not in n:
                                    num1 = row[i]
                                    num2 = row[j]
                                    num3 = row[c]
                                    num4 = row[d]
                                    if num1 + num2 == num3 + num4:
                                        f = False
        if f:
            cnt += 1

print(cnt)
