def dev(n):
    for i in range(2, int(n**0.5) + 2):
        if n % i == 0:
            return i


for i in range(850_000, 5_000_000):
    n = dev(i)
    if n:
        r = i / n
        num = r - n
        if num and num % 13 == 0:
            print(i, num)
