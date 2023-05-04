with open("24.txt") as f:
    data = f.read()

nx = [i for i in range(len(data)) if data[i] == "F"]
mx = 0

for bg in nx:
    for eg in nx:
        if eg > bg:
            d = data[bg : eg + 1]
            if d.count("A") <= 2:
                if len(d) > mx:
                    mx = len(d)
            else:
                if bg % 1000 < 5:
                    print(f"broken, {bg}/{len(data)}, mx: {mx}")
                break

print(mx)
