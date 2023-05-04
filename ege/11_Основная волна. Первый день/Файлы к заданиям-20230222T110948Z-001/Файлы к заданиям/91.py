with open("9.txt") as f:
    data = f.read().split("\n")

nums = [list(map(int, x.split())) for x in data]

n = 0

for row in nums:
    m = max(row)
    s = sum(row) - m
    if m < s:
        res = []
        for i in range(4):
            for j in range(4):
                if i != j:
                    s1 = row[i] + row[j]
                    res.append(sum(row) / 2 == s1)
        if any(res):
            n += 1

print(n)
