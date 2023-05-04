with open("26-84.txt") as f:
    data = f.read().splitlines()

n = int(data[0])
groups = list(map(int, data[1].split()))
rooms = list(map(int, data[2].split()))

min_r = min(rooms)
min_g = [x for x in groups if x <= min_r]
print(len(min_g))
