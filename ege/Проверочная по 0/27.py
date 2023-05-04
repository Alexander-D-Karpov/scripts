with open("27_B.txt") as f:
    data = f.read().splitlines()


n, m = map(int, data[0].split())
data = [list(map(int, x.split())) for x in data[1:]]
res = [0] * (max([x[0] for x in data]) + m + 1)
max_n = len(data)
nk = 0

for n, em in data:
    if em % 30 == 0:
        boxes = em // 30
    else:
        boxes = em // 30 + 1
    if n > m:
        for i in range(n - m, n + m + 1):
            res[i] += boxes
    else:
        for i in range(n + m + 1):
            res[i] += boxes
    if nk % 500 == 0:
        print(nk, max_n)
    nk += 1


print("max", max(res), "index", res.index(max(res)))
