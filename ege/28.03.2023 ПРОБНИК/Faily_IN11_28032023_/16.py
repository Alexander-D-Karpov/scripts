c = 0
for n in range(123_456_789, 1_234_567_886):
    if n % 15 != 0:
        if n % 3 != 0:
            if n % 5 != 0:
                c += 1

print(c)
