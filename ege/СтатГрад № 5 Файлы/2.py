for x in range(2):
    for y in range(2):
        for w in range(2):
            for z in range(2):
                f1 = (x or not (y)) <= (w == z)
                f2 = (x or not (y)) == (z <= w)
                if not (f1) and not (f2):
                    print(y, z, x, w, "|", int(f1), int(f2))
print("-" * 8)
for x in range(2):
    for y in range(2):
        for w in range(2):
            for z in range(2):
                f1 = (x or not (y)) <= (w == z)
                f2 = (x or not (y)) == (z <= w)
                if not (f1):
                    print(y, z, x, w, "|", int(f1), int(f2))

print("-" * 8)
for x in range(2):
    for y in range(2):
        for w in range(2):
            for z in range(2):
                f1 = (x or not (y)) <= (w == z)
                f2 = (x or not (y)) == (z <= w)
                if not (f2):
                    print(y, z, x, w, "|", int(f1), int(f2))
