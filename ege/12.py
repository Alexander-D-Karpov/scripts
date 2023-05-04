r = "01111111222122212220"


while "00" not in r:
    if "011" in r:
        r = r.replace("011", "101", 1)
    else:
        r = r.replace("01", "40", 1)
        r = r.replace("02", "20", 1)
        r = r.replace("0222", "1401", 1)
print(r.count("4"))
