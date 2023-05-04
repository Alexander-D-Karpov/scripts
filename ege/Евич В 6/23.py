def f(n, path):
    if n == 26:
        if 12 in path:
            return 1
        return 0
    if n > 26:
        return 0
    return f(n + 1, path + [n + 1]) + f(n + 7, path + [n + 7])


print(f(5, []))
