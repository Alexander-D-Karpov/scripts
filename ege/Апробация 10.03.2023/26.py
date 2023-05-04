with open("26.txt") as f:
    data = list(map(int, f.read().splitlines()[1:]))

nums = sorted(data)
s = 0
il = 0

for i, el in enumerate(nums):
    n = i + 1
    if len(nums) - il == i:
        break
    if n % 3 == 0:
        il += 1
    else:
        s += el

print(s)

nums = sorted(data, reverse=True)
s = 0
il = 0

for i, el in enumerate(nums):
    n = i + 1
    if len(nums) - il == i:
        break
    if n % 3 == 0:
        il += 1
    else:
        s += el

print(s)
