with open("27-B.txt") as f:
    data = list(map(int, f.read().splitlines()))[1:]


c = 0

for x in range(len(data)):
    for y in range(len(data)):
        if x != y:
            if x * y % 1_000_000 == 0:
                c += 1

print(c)
