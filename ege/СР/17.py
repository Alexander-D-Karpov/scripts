data = []

with open("17.txt") as f:
    for fl in f:
        try:
            data.append(int(fl))
        except Exception:
            continue
print(len(data))
res = []

for i in range(1, len(data)):
    num1 = data[i - 1]
    num2 = data[i]
    if num1 + num2 >= 100:
        if num1 < 0 or num2 < 0:
            res.append(num1 * num2)


print(len(res), max(res))
