import re


def subpaths(path):
    results = []
    indexes = [m.start() for m in re.finditer(r"\.", path)]
    for index in indexes + [len(path)]:
        results.append(path[0:index])
    return results
