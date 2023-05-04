def f(n):
    bin_n = bin(n)[2:]
    if len(bin_n) % 2 == 0:
        nk = len(bin_n) // 2
        bin_n = bin_n[:nk] + "000" + bin_n[nk:]
    else:
        bin_n = "1" + bin_n + "01"
    return int(bin_n, 2)


for n in range(100):
    if f(n) > 100:
        print(n)
        break
