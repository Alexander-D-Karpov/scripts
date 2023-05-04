def is_prime(n):
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


for r in range(200, 10000):
    s = "0" + "2" * r + "1" * r + "210"
    while "00" not in s:
        s = s.replace("02", "101", 1)
        s = s.replace("11", "2", 1)
        s = s.replace("12", "21", 1)
        s = s.replace("010", "00", 1)

    n = sum([int(x) for x in s])
    if is_prime(n):
        print(s, n, r)
        break

    s = "0" + "2" * r + "1" * r + "0"
    while "00" not in s:
        s = s.replace("02", "101", 1)
        s = s.replace("11", "2", 1)
        s = s.replace("12", "21", 1)
        s = s.replace("010", "00", 1)

    n = sum([int(x) for x in s])
    if is_prime(n):
        print(s, n, r)
        break
