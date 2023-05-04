g = {
    "а": "б",
    "б": "ве",
    "в": "ги",
    "г": "и",
    "д": "абе",
    "е": "вжл",
    "ж": "вл",
    "и": "нм",
    "к": "д",
    "л": "дк",
    "м": "жл",
    "н": "м",
}


def f(n, path):
    if n == "е":
        return 1
    s = []
    for nd in g[n]:
        if path.count(nd) != 1:
            s.append(f(nd, path + [nd]))
    return sum(s)


print(f("ж", []))
