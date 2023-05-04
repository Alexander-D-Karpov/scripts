with open("26.txt") as f:
    data = f.read().splitlines()[1:]

nums = sorted([x.split() for x in data], key=lambda x: int(x[0]))
rec = 0
left = 0
cars = [0] * 80
bas = [0] * 20
proc = {}

for em, t, typ in nums:
    em = int(em)
    time = int(t)
    proc[em] = (time, typ)

mx = max([int(x[0]) for x in nums])
for i in range(1, mx + 2):
    crs = []
    for c in cars:
        if c <= 1:
            crs.append(0)
        else:
            crs.append(c - 1)
    cars = crs

    bs = []
    for b in bas:
        if b <= 1:
            bs.append(0)
        else:
            bs.append(b - 1)
    bas = bs

    if i in proc:
        time, typ = proc[i]

        if typ == "A":
            if 0 in cars:
                cars[cars.index(0)] = time
                rec += 1
            elif 0 in bas:
                bas[bas.index(0)] = time
                rec += 1
            else:
                left += 1
        else:
            if 0 in bas:
                bas[bas.index(0)] = time
            else:
                left += 1
    if i % 100 == 0:
        print("done", i, mx, len(proc))

print(rec, left)
