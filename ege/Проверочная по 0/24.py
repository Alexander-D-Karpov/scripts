with open("24.txt") as f:
    data = f.read()

c = 0
mx = 0

for ex in range(1, 3):
    for i in range(ex, len(data), 2):
        el1 = data[i - 1]
        el2 = data[i]

        if el1 + el2 in ["AB", "CB"]:
            c += 1
        else:
            if c > mx:
                mx = c
            c = 0

print(mx)
