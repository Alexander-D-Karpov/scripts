with open("17.txt") as f:
    data = list(map(int, f.read().split()))

res = []
n = len([x for x in data if x % 5 == 0])
for i in range(1, len(data)):
    n1 = data[i - 1]
    n2 = data[i]

    if [int(x < 0) for x in [n1, n2]].count(1) == 1:
        if n1 + n2 < n:
            res.append(n1 + n2)

print(len(res), max(res))
