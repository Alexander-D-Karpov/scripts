def to_3(n):
    s = ""
    while n:
        s += str(n % 3)
        n //= 3
    return s[::-1]


r = 2 * 729**1021 - 2 * 243**1022 + 81**1023 - 2 * 27**1024 - 1025
s = to_3(r)
print(s.count("0"))
