gr = {
    "а": "б",
    "б": "ве",
    "в": "гиж",
    "г": "и",
    "д": "аб",
    "е": "вдл",
    "ж": "ем",
    "и": "н",
    "к": "д",
    "л": "дк",
    "м": "ели",
    "н": "м",
}


def f(p, path):
    if p == "н" and path:
        print(path)
        return 1
    res = []
    for g in gr[p]:
        if path.count(g) <= 0:
            res.append(f(g, path + [g]))

    return sum(res)


print(f("а", ["а"]))
