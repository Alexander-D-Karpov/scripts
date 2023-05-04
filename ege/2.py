with open("24.txt") as f:
    data = f.read()


data = data.split("F")

mx = 0
mf = ""
for i in range(len(data)):
    if data[i] and data[i].count("A") <= 2:
        p = []
        j = i + 1
        try:
            while data[j].count("A") <= 2:
                p.append(data[j])
                j += 1
            s = "F" + "F".join(p) + "F"
            if len(s) > mx:
                mx = len(s)
                mf = s
        except IndexError:
            break
print(mx, mf)
