with open("17.txt") as f:
    data = list(map(int, f.read().split()))

n = min([x for x in data if x > 0 and x % 19 == 0])
r = []
for i in range(1, len(data)):
    n1 = data[i - 1]
    n2 = data[i]
    if n1 + n2 < n:
        r.append(abs(n1 + n2))

print(len(r), max(r))
