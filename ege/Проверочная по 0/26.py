with open("26.txt") as f:
    data = [list(map(int, x.split())) for x in f.read().splitlines()[1:]]

rows = {}

for ind, num in data:
    if ind in rows:
        rows[ind].append(num)
    else:
        rows[ind] = [num]
print("data loaded")
res = []


for ind, row in rows.items():
    row.sort()
    for i in range(1, len(row)):
        n1 = row[i - 1]
        n2 = row[i]
        if n2 - n1 == 14:
            res.append((ind, n1 + 1))

print(len(res))
r = [x for x in res if x[0] == max([n[0] for n in res])]
print(r)
