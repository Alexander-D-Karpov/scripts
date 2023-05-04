with open("24.txt") as f:
    data = f.read()

sgl = "CDF"
gl = "AO"
r = []
for s in sgl:
    for g in gl:
        r.append(s + g)
mx = 0

for e in range(2):
    c = 0
    rek = 0
    for i in range(e + 1, len(data), 2):
        n1 = data[i - 1]
        n2 = data[i]
        nk = n1 + n2
        if nk in r:
            rek += 1
            c += 2
        else:
            c += 2
        if c > mx:
            mx = c
        if rek > 5:
            rek = 0
            c = 0
print(mx)
