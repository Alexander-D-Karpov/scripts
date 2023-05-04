gr = {
    "а": "бг",
    "б": "д",
    "в": "абгдж",
    "г": "ж",
    "д": "ие",
    "е": "влк",
    "ж": "е",
    "и": "ел",
    "к": "ж",
    "л": "к",
}


def f(p, path):
    if p == "е" and path:
        return 1
    s = []
    for n in gr[p]:
        if n not in path:
            s.append(f(n, path + [n]))
    return sum(s)


print(f("е", []))
