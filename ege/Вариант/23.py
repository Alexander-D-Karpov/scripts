def f(n, path):
    if len(path) == 12:
        return path

    return f(n + 1, path + [n + 1]) + f(n - 1, path + [n - 1])


r = f(1, [])
print(len(r))
print(len(list(set(r))))
