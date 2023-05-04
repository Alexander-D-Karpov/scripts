with open("17.txt") as f:
    data = list(map(int, f.read().split()))

nl = [x for x in data if str(x)[-1] == "3"]
n = sum(nl) / len(nl)
m = max(data)
r = []

for i in range(1, len(data)):
    num1 = data[i - 1]
    num2 = data[i]

    if m % num1 == 0 or m % num2 == 0:
        if num1 + num2 > n:
            r.append(num1 + num2)


print(len(r), min(r))
