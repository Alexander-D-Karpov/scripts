with open("9.txt") as f:
    data = f.read().splitlines()

nums = [list(map(int, x.split())) for x in data]
cnt = 0

for en, row in enumerate(nums):
    s = [i for i in range(len(row)) if row.count(i) == 1]
    if s:
        f = False
        for i in s:
            c = 0
            for j in range(len(nums)):
                if j != en:
                    c += nums[j].count(row[i])
            if c == 50:
                f = True
        if f:
            cnt += 1

print(cnt)
