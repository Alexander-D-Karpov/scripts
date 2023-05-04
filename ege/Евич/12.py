with open("24.txt") as f:
    data = f.read()


mx = 0
c = 0
cur = ""
f = False

for i in range(1, len(data) - 1):
    s1 = data[i - 1]
    s2 = data[i]
    s3 = data[i + 1]
    if f:
        if s1 == s2 == s3:
            c += 1
        else:
            if c > mx and data[i + 1] == cur:
                print(data[i - c : i + 2])
                mx = c
            f = False
    else:
        if s1 == s2 == s3:
            cur = data[i - 2]
            c = 3
            f = True
print(mx)
