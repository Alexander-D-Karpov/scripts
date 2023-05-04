with open("24.txt") as f:
    data = f.read()

k = 0
m = 0
f = False
for j in range(3):
    for i in range(j, len(data), 3):
        w = data[i - 3 : i]
        if w in ["CFE", "FCE"]:
            if f:
                k += 1
            else:
                f = True
                k = 1
        else:
            f = False
            if k > m:
                m = k
            k = 0
print(m)
