g = {
    "а": "бг",
    "б": "д",
    "в": "абгд",
    "г": "еж",
    "д": "иле",
    "е": "вл",
    "ж": "е",
    "и": "л",
    "к": "ж",
    "л": "жк",
}


def run(p, path):
    if p == "е" and path:
        return 1

    ns = g[p]
    r = 0
    for n in ns:
        if n not in path:
            r += run(n, path + [n])
    return r


print(run("е", []))
