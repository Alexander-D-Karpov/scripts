data = [[0] * 100_000] * 100_000

with open("26.txt") as f:
    for el in f.read().split("\n")[1:]:
        try:
            x, y = map(int, el.split())
        except Exception:
            continue
        data[y - 1][x - 1] = 1
print("done")
res = []

for i, row in enumerate(data):
    indexes = []
    for index in range(len(row)):
        if row[index]:
            indexes.append(index)
    f = False
    n = 0
    c = 0
    for el in indexes:
        if el:
            if f:
                n += 1
                if n == 3:
                    c += 1
            else:
                n = 1
        else:
            f = False
            n = 0
    res.append((i, c))
    if i % 1000 == 0:
        print(i)

print(res[:4])
res = sorted(res, key=lambda x: x[1])
print(res[-1])
