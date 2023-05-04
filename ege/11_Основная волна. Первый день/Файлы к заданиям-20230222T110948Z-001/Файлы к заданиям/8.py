alf = "01234567"
nc = ["1", "3", "5", "7"]
cnt = 0

for a in alf[1:]:
    for b in alf:
        for c in alf:
            for d in alf:
                for e in alf:
                    w = a + b + c + d + e
                    if w.count("6") == 1:
                        if a == "6":
                            if b not in nc:
                                cnt += 1
                        elif e == "6":
                            if d not in nc:
                                cnt += 1
                        else:
                            mnc = w[w.index("6") - 1]
                            mxc = w[w.index("6") + 1]
                            if mnc not in nc and mxc not in nc:
                                cnt += 1
print(cnt)
