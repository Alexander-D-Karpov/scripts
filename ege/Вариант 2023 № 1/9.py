with open("9.txt") as f:
    data = f.read().splitlines()

nums = [list(map(int, x.split())) for x in data]

count = 0

for row in nums:
    n = [row.count(x) for x in row]
    if n.count(3) == 3 and n.count(1) == 3:
        ns = [(x, row.count(x)) for x in row]
        nr = 0
        mr = 0
        for n, c in ns:
            if c == 3:
                nr += n
            else:
                mr += n
        if mr / 3 < nr:
            count += 1
            print(row)

print(count)
