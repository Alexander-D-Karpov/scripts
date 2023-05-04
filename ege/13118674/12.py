for x in range(70):
    for y in range(70):
        for z in range(70):
            ed = y + z
            dw = z
            tr = x + y + z

            if ed == 20 and dw == 10 and tr == 70:
                print(x, y, z)
