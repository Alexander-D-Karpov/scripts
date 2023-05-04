with open("9.txt") as f:
    data = [list(map(int, x.split())) for x in f.read().splitlines()]

n = 0
for row in data:
    mx = max(row)
    if row.count(mx) == 1:
        if [row.count(x) for x in row].count(1) != 6:
            c = [x for x in row if x != mx]
            if mx > sum(c) / len(c) * 3:
                n += 1

print(n)
