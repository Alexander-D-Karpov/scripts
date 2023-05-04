alf = "ярослав"
gl = "яоа"
sgl = "рслв"
cnt = 0
for a in alf:
    w = a
    for b in alf:
        if b not in w:
            w = a + b
            for c in alf:
                if c not in w:
                    w = a + b + c
                    for d in alf:
                        if d not in w:
                            w = a + b + c + d
                            for e in alf:
                                if e not in w:
                                    w = a + b + c + d + e
                                    sggl = len([x for x in w if x in sgl])
                                    if sggl >= 3:
                                        f = True
                                        for i in range(1, 5):
                                            a1 = w[i - 1]
                                            a2 = w[i]
                                            if a1 in gl and a2 in gl:
                                                f = False
                                        if f:
                                            cnt += 1
print(cnt)
