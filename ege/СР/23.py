def f(n, path):
    if n >= 24:
        if n == 24:
            if 6 in path:
                return 1
        return 0

    return (
        f(n + 2, path + [n + 2]) + f(n * 2, path + [n * 2]) + f(n * 3, path + [n * 3])
    )


print(f(1, []))
