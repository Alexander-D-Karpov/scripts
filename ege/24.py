with open("24-215.txt") as f:
    data = f.read()

b = "ABC"
c = "123"

cnt = 0
mx = 0

for ex in range(3):
    for i in range(ex + 2, len(data), 3):
        n1 = data[i - 2]
        n2 = data[i - 1]
        n3 = data[i]
        if n1 in b and n2 in c and n3 in c:
            cnt += 1
            if cnt > mx:
                mx = cnt
        else:
            cnt = 0


print(mx)
