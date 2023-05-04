with open("24.txt") as f:
    data = f.read()

mx = 0
data = data.split("%")

for seq in data:
    c = 0
    f = False
    if seq:
        for i in range(0, len(seq), 3):
            d = seq[i : i + 3]
            if d in ["?!?", "?!", "!"] and f:
                if f:
                    c += len(d)
                else:
                    c = len(d)
                    f = True
            elif d == "?!?":
                f = True
                c = 3
            else:
                if f:
                    f = False
                    if c > mx:
                        mx = c
                        print(seq, c)
                    c = 0

print(mx)
