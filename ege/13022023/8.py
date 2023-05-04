alf = "ЕКОФ"
sgl = "КФ"
r = []
n = 1
for a in alf:
    for b in alf:
        for c in alf:
            for d in alf:
                for e in alf:
                    w = a + b + c + d + e
                    if w.count("О") == 1:
                        i = w.index("О")
                        if i == 0:
                            f = w[i + 1] not in sgl
                        elif i == 4:
                            f = w[i - 1] not in sgl
                        else:
                            f = w[i + 1] not in sgl and w[i - 1] not in sgl
                        if f:
                            r.append(n)
                    n += 1


print(min(r) + max(r))
