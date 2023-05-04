res = []

for x in range(0, 1001):
    for y in range(10):
        if x == 1000:
            rx = ""
        else:
            rx = x

        r = int(f"123{rx}4{y}5")
        if r % 3013 == 0:
            res.append(r)

print(sorted(res))
