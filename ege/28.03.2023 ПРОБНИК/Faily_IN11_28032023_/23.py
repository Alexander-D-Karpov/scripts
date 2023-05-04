def f(n, prev):
    if n == 24:
        return 1
    if n > 24:
        return 0

    s = 0
    if prev not in "12":
        s += f(n + 1, "1")
    if prev not in "12":
        s += f(n + 2, "2")
    if prev not in "34":
        s += f(n * 2, "3")
    if prev not in "34":
        s += f(n * 3, "4")
    return s


print(f(1, "0"))
