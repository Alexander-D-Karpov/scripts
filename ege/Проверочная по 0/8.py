alf = "алпця"
cnt = 1
for a in alf:
    for b in alf:
        for c in alf:
            for d in alf:
                for e in alf:
                    w = a + b + c + d + e
                    if w.count("а") <= 1 and w.count("ц") == 2 and w.count("л") == 0:
                        print(cnt)
                        raise
                    cnt += 1
