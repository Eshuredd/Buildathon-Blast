"""Deterministic integer-millisecond scheduling."""
def schedule(tests):
    if not tests:
        return []
    ordered = sorted(tests, key=lambda t: (-round(t["seconds"] * 1000), t["number"]))
    best = None
    for count in range(1, min(8, len(ordered)) + 1):
        workers = [[] for _ in range(count)]
        loads = [0] * count
        for test in ordered:
            index = min(range(count), key=lambda i: (loads[i], i))
            workers[index].append(test["number"])
            loads[index] += round(test["seconds"] * 1000)
        occupied = [w for w in workers if w]
        cost = max(loads) + 2000 * len(occupied)
        key = (cost, len(occupied))
        if best is None or key < best[0]:
            best = key, occupied
    return best[1]
