with open("17.txt") as f:
    data = list(map(int, f.read().splitlines()))

n = min([x for x in data if str(x)[-2:] == "68"]) ** 2
res = []
for i in range(1, len(data)):
    num1 = data[i - 1]
    num2 = data[i]
    s = [str(num1)[-2:], str(num2)[-2:]]
    if s.count("68") == 1 and num1**2 + num2**2 >= n:
        res.append(num1**2 + num2**2)

print(len(res), max(res))
