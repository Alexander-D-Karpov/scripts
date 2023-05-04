with open("9.txt") as f:
    data = [list(map(int, x.split())) for x in f.read().splitlines()]


c = 0
for row in data:
    n = 1
    for el in row:
        for e in str(el):
            n *= int(e)
    if n > sum(row):
        c += 1
print(c)
