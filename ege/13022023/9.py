with open("9.txt") as f:
    data = f.read().splitlines()
nums = [list(map(int, x.split())) for x in data]
n = 0

for row in nums:
    indx = [row.count(x) for x in row]
    if indx.count(2) == 2 and indx.count(1) == 4:
        f = False
        for i1 in range(6):
            for i2 in range(6):
                if i2 != i1:
                    for i3 in range(6):
                        if i3 not in [i1, i2]:
                            for j1 in range(6):
                                if j1 not in [i1, i2, i3]:
                                    for j2 in range(6):
                                        if j2 in [i1, i2, i3, j1]:
                                            for j3 in range(6):
                                                if j3 in [i1, i2, i3, j1, j2]:
                                                    s1 = row[i1] + row[i2] + row[i3]
                                                    s2 = row[j1] + row[j2] + row[j3]
                                                    if s1 == s2:
                                                        f = True
        if f:
            n += 1

print(n)
