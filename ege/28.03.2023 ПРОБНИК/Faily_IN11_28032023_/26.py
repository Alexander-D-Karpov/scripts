with open("26.txt") as f:
    data = [list(map(int, x.split())) for x in f.read().splitlines()]

res = []
rows = {}
for el in data[1:]:
    if el[0] in rows:
        rows[el[0]] += [el[1]]
    else:
        rows[el[0]] = [el[1]]


for elll, row in rows.items():
    row = sorted(row)
    if len(row) > 1:
        c = 0
        for i in range(1, len(row)):
            i1 = row[i - 1]
            i2 = row[i]

            if i2 - i1 <= 9:
                c += i2 - i1
            else:
                if c:
                    res.append((elll, c))
                c = 0

        if c:
            res.append((elll, c))

print(sorted(res, key=lambda x: x[1], reverse=True)[:20])
