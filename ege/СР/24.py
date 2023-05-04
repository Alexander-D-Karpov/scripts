with open("24.txt") as f:
    data = f.read()

mx = 0
for i in range(len(data)):
    for j in range(i + 1, len(data)):
        s = data[i:j]
        if s.count("Z") <= 2:
            if len(s) > mx:
                mx = len(s)
                print(mx)
        else:
            break
