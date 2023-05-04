with open("24.txt") as f:
    data = list(f.read())

mx = 0

for x in range(3):
    c = False
    s = 0
    for i in range(x + 1, len(data) - 1, 3):
        s1 = data[i - 1]
        s2 = data[i]
        s3 = data[i + 1]
        w = s1 + s2 + s3
        if w == "NPO" or w == "PNO":
            if c:
                s += 1
                if s > mx:
                    mx = s
            else:
                c = True
                s = 1
        else:
            c = False


print(mx)
