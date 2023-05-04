with open("26.txt") as f:
    data = list(map(int, f.read().split()))[1:]

s1 = 0
s2 = 0

for i in range(len(data)):
    n = i + 1
    if n % 4 == 0:
        s1 += data[i] % 2
    else:
        s1 += data[i]

l = 1
sdata = sorted(data)

for i in range(len(data)):
    n = i + 1
    if len(data) - i == l:
        break

    if n % 4 == 0:
        s2 += sdata[-l] % 2
        l += 1
    else:
        s2 += sdata[i]


print(s1, s2)
