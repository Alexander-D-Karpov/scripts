s = "7" * 512
c = 0
while "7777" in s or "1111" in s:
    c += 1
    if "7777" in s:
        s = s.replace("7777", "1", 1)
    else:
        s = s.replace("1111", "7", 1)

print(c)
