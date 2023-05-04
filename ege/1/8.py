def to_6(n):
    s = ""
    while n:
        s += str(n % 6)
        n //= 6
    return s[::-1]


c = 0
ch = "02468"

for i in range(100000, 1000000):
    s = to_6(i)
    if s.count("2") == 1:
        ind = s.index("2")
        if ind == 0:
            if s[1] in ch:
                c += 1
        elif ind == len(s) - 1:
            if s[-2] in ch:
                c += 1
        else:
            if s[ind - 1] in ch and s[ind + 1] in ch:
                c += 1
print(c)
