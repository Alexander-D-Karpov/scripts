with open("24.txt") as f:
    data = f.read()

sgl = "CDF"
gl = "AO"

mx = 0
n = 0

for xr in range(3):
    for i in range(xr, len(data) - 2, 3):
        i1 = data[i]
        i3 = data[i + 2]
        if i1 in sgl and i3 in gl:
            n += 1
        else:
            if n > mx:
                mx = n
            n = 0
print(mx)
