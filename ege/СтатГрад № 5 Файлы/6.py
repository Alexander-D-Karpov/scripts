from itertools import permutations

j = 1

for i in permutations("ВИКОРТ", r=6):
    s = "".join(i) + " " + str(j)
    j += 1
    print(s)
