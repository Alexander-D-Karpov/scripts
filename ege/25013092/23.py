def f(p, path):
    if p > 280:
        return 0
    if p == 280:
        if 30 in path and 60 not in path:
            return 1
        return 0

    return f(p + 5, path + [p + 5]) + f(p * 5, path + [p * 5])


print(f(5, []))
