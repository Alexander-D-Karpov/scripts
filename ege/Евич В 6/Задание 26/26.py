with open("26.txt") as f:
    data = f.read().split("\n")

d, n = map(int, data[0].split())
nums = list(map(int, data[1:]))
nums.sort(reverse=False)

em = 0
k = d
r = []
for el in nums:
    if k - el >= 0:
        em += 1
        k -= el
        r.append(el)
    else:
        break

nr = max(r)
en = 0
for el in nums:
    if el > nr:
        en += 1

print(em, en)
