def f(n):
    bin_n = bin(n)[2:]
    if n % 5 == 0:
        bin_n += bin(5)[2:]
    else:
        bin_n += "1"
    if int(bin_n, 2) % 7 == 0:
        bin_n += bin(7)[2:]
    else:
        bin_n += "1"
    return int(bin_n, 2)


for i in range(1000, 1000000):
    if f(i) >= 1728404:
        print(i - 1)
        break
