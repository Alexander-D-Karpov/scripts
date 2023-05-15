g = {
    "a": "cd",
    "b": "ac",
    "c": "gd",
    "d": "he",
    "e": "ab",
    "f": "gbn",
    "g": "ho",
    "h": "jli",
    "i": "fl",
    "j": "kg",
    "k": "h",
    "l": "k",
    "m": "fi",
    "n": "mo",
    "o": "f",
}


def f(p, path):
    if p == "a" and path:
        return 1
    s = []
    for n in g[p]:
        if n not in path:
            s.append(f(n, path + n))
    return sum(s)


print(f("a", ""))
