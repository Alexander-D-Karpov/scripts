with open("26.txt") as f:
    data = list(map(int, f.read().split()))

su = 0
m = 0
data = sorted(data[1:], reverse=True)

while data:
    mx = data[0]
    del data[0]
    i = 0
    c = 1
    left = []
    for el in data:
        if mx - el >= 5:
            c += 1
            mx = el
        else:
            left.append(el)
    su += mx
    if c > m:
        m = c
    data = left

print(su, m)
