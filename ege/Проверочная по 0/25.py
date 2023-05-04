for i in range(10):
    for j in range(10):
        n = f"12345{i}7{j}8"
        n = int(n)
        if n % 23 == 0:
            print(n)
