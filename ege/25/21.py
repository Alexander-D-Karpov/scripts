for i in range(10):
    for j in range(10):
        s = int(f"12345{i}6{j}8")
        if s % 17 == 0:
            print(s, s // 17)
