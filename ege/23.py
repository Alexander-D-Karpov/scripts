def f(n, path):
    if n >= 214:
        if n == 214:
            if [x % 2 for x in path].count(1) <= 7:
                return 1
        return 0

    return (
        f(n + 2, path + [n + 2]) + f(n * 2, path + [n * 2]) + f(n * 3, path + [n * 3])
    )


print(f(1, [1]))
