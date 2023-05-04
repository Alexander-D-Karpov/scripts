def f(n):
    bin_n = bin(n)[2:]
    if n % 2 == 0:
        bin_n = "1" + bin_n + "0"
    else:
        bin_n = "11" + bin_n + "11"
    return int(bin_n, 2)


for n in range(1000):
    if f(n) > 225:
        print(f(n))
        break
