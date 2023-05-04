def f(n):
    if n == 0:
        return 0
    if n % 2 == 0:
        return f(n / 2) - 1
    return f(n - 1) + 2


c = 0

for i in range(1000):
    if f(i) == 3:
        c += 1


print(c)
