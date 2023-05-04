def f(n):
    if n <= 3:
        return 1
    return f(n - 3) + f(n - 2)


print(f(10))
