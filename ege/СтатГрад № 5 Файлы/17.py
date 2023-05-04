with open("17.txt") as f:
    data = list(map(int, f.read().split()))

n = min([x for x in data if len(str(x)) == 3 if str(x)[-1] == "5"])
res = []
for i in range(1, len(data)):
    n1 = data[i - 1]
    n2 = data[i]
    if [len(str(x)) for x in [n1, n2]].count(4) == 1:
        if (n1**2 + n2**2) % n == 0:
            res.append(n1**2 + n2**2)


print(len(res), max(res))
