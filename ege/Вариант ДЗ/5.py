def fifth_n(n, k):
    s = ""
    while n:
        s += str(n % 5)
        n //= 5
    s = s[::-1]
    return s[k]


def f(n):
    bin_n = bin(n)[2:]
    if bin_n.count("0") % 2 == 0:
        n = fifth_n(n, 0) + str(n)
    else:
        n = str(n) + fifth_n(n, 0)
    return sum(list(map(int, bin(int(n))[2:])))


m = []
for i in range(100, 501):
    m.append(f(i))

print(max(m))
