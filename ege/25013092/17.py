with open("17.txt") as f:
    data = list(map(int, f.read().split()))

res = []
n = min(data)

for i in range(1, len(data)):
    num1 = data[i - 1]
    num2 = data[i]

    if num1 % 117 == n or num2 % 117 == n:
        res.append(num1 + num2)


print(len(res), max(res))
