def f(n):
    bin_n = bin(n)[2:]
    if bin_n.count("1") % 2:
        bin_n = "11" + bin_n[2:] + "1"
    else:
        bin_n = "10" + bin_n[2:] + "0"
    return int(bin_n, 2)


for i in range(200):
    if f(i) >= 16:
        print(i)
        break
