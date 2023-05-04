with open("17.txt") as f:
    data = list(map(int, f.read().split()))

res = []

for i in range(1, len(data)):
    n1 = data[i - 1]
    n2 = data[i]

    if (n1 * n2) % 15 == 0:
        if (n1 + n2) % 7 == 0:
            res.append(n1 + n2)

print(len(res), max(res))
