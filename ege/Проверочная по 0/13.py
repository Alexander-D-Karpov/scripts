g = {
    "а": "бг",
    "б": "д",
    "в": "абдгж",
    "г": "ж",
    "д": "еи",
    "е": "вл",
    "ж": "е",
    "и": "л",
    "к": "ж",
    "л": "кж",
}


def f(p, path):
    if p == "е" and path:
        return 1
    s = []
    for n in g[p]:
        if n not in path:
            s.append(f(n, path + n))
    return sum(s)


print(f("е", ""))
