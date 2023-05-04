with open("17.txt") as f:
    data = list(map(int, f.read().split()))

n = [x for x in data if "4" in str(x)]

print(len(n), max(n))
