with open("17.txt") as f:
    data = list(map(int, f.read().splitlines()))

res = []
n = len([x for x in data if x % 3 == 0])
for i in range(1, len(data)):
    n1 = data[i - 1]
    n2 = data[i]
    if n1 < 0 or n2 < 0:
        if n1 + n2 < n:
            res.append(n1 + n2)

print(len(res), max(res))
