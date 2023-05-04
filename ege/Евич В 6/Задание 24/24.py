with open("24.txt") as f:
    data = f.read().split(" ")

print(min([len(x) for x in data if x]))
