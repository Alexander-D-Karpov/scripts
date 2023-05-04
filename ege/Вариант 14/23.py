def f(n, y):
    if n < y:
        return 0
    if n == y:
        return 1
    return f(n / 2, y) + f(n - 1, y)


print(f(64, 14))
