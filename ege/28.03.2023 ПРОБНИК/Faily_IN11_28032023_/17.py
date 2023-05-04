with open("17.txt") as f:
    data = list(map(int, f.read().splitlines()))

n = min([x for x in data if str(x)[-1] == str(x)[-2]]) ** 2
res = []

for i in range(1, len(data)):
    el1 = data[i - 1]
    el2 = data[i]

    s1 = str(el1)
    s2 = str(el2)

    if s1[-1] == s2[-2] or s2[-1] == s1[-2]:
        if el1 % 13 == 0 and el2 % 13 != 0 or el1 % 13 != 0 and el2 % 13 == 0:
            if el1**2 + el2**2 <= n:
                res.append(el1**2 + el2**2)

print(len(res), max(res))
