def f(n):
    bin_n = bin(n)[2:]
    for _ in range(3):
        nch = 0
        ch = 0
        for e in str(n):
            if e in "02468":
                ch += 1
            else:
                nch += 1
        if ch == nch:
            if n % 2 == 1:
                bin_n += "1"
            else:
                bin_n += "0"
        else:
            if ch > nch:
                bin_n += "1"
            else:
                bin_n += "0"
        n = int(bin_n, 2)
    return n


print(f(14))

c = 0
for i in range(100000, 1000000010):
    r = f(i)
    if 1_234_567_899 >= r >= 876_544:
        c += 1
        if c % 100000 == 0:
            print(i, r, c)
    if r > 1_334_567_899:
        break
print(c)
