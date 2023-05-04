with open("9.txt") as f:
    data = f.read().splitlines()[1:]
nums = []
for x in data:
    nums += list(map(float, x.split()[1:]))

n = min(nums)
print(len([x for x in nums if x > n * 2]))
