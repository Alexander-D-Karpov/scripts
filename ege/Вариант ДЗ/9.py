with open("9.txt") as f:
    data = [list(map(int, x.split())) for x in f.read().splitlines()]
c = 0
for row in data:
    cr = sorted(row)
    n1 = cr[-1] ** 2 + cr[-2] ** 2
    n2 = cr[0] ** 2 + cr[1] ** 2
    if n1 % n2 == 0:
        if any([n1 % x == 0 or n2 % x == 0 for x in cr[2:-2]]):
            print(row)
            c += 1
print(c)
