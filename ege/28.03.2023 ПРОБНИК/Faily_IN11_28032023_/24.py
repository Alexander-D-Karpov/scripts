with open("24.txt") as f:
    data = f.read().splitlines()

l = []
for r in data:
    res = {}
    for i in range(1, len(r)):
        r1 = r[i - 1]
        r2 = r[i]
        if r1 == "T":
            if r2 in res:
                res[r2] += 1
            else:
                res[r2] = 1
    mx = max(res.values())
    l += [x for x in res if res[x] == mx]

print(max([l.count(el) for el in list(set(l))]))
