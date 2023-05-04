alf = "АКЛМРС"
num = 1
r = []

for a in alf:
    for b in alf:
        for c in alf:
            for d in alf:
                for e in alf:
                    for g in alf:
                        w = a + b + c + d + e + g
                        n = [w.count(x) for x in w]
                        if n.count(3) == 3 and n.count(1) == 3:
                            f = True
                            for i in range(1, 6):
                                n1 = w[i - 1]
                                n2 = w[i]
                                if n1 == "К" and n2 == "С":
                                    f = False
                            if f:
                                r.append(num)
                        num += 1


print(r[-1])
