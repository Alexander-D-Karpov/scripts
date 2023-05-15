with open("26.txt") as f:
    data = f.read().splitlines()

n = int(data[0])

re = []

for l in data[1:]:
    h, w, d, a = l.split()

    re.append((int(h) * int(w) * int(d) / 8 / 1024 / 1024, a == "C" and 2 ** int(d) > 256))

re.sort()

ss = 0
c = 0

for e, a in re:
    if n > e:
        c += 1
        if a:
            ss += 1
        n -= e
print(c, ss)
    
