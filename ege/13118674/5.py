def f(n):
    sn = str(n)
    r = sorted(
        [int(sn[0]) + int(sn[1]), int(sn[1]) + int(sn[2]), int(sn[2]) + int(sn[3])]
    )
    return "".join([str(x) for x in r[-2:]])


for i in range(1000, 10000):
    if f(i) == "1418":
        print(i)
        break
