def f(n, path):
    if n <= 0:
        return 0
    if n == 1 and 10 in path:
        return 1
    return f(n - 2, path + [n - 2]) + f(n // 2, path + [n // 2])


print(f(28, []))
