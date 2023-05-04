for x in range(101):
    if x == 100:
        x = ""
    for y in range(10):
        s = int(f"123{x}4{y}5")
        if s % 161 == 0:
            print(s, s // 161)
