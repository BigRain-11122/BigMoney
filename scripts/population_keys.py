"""Population counts are not readings.

A face that counts the python corpus moves whenever the tree moves: a round-scoped scratch file
appears, a stale one is deleted.  A leg that demands a byte-identical summary therefore goes red
for the wrong reason once per few rounds (E420/E421 law, 5th recurrence at r1441: E403 went red on
`corpus_py_files 3488 -> 3487` while every number a reader acts on was identical).

The fix is a declaration, not a looser assertion: a producer names the summary keys that count its
own population, publishes that list inside the face, and the leg compares every OTHER key for
equality.  A key is excluded only if the producer declared it -- the leg cannot widen the gate,
and the face cannot exclude a key it does not publish.
"""

#: Keys a summary may use to report the size of the corpus it scanned.
DECLARED_ATTR = "population_keys"


def keys_of(face, module=None):
    """(declared keys, problems) for a published face and its producer module.

    Both sides must agree: the face says which keys it counts, and the module says the same, so a
    leg reading `module.population_keys` can never silently exclude more than the face admits.
    """
    problems = []
    published = face.get(DECLARED_ATTR)
    if published is None:
        return (), ["the face does not declare %s, so every summary key is treated as a reading"
                    % DECLARED_ATTR]
    if not isinstance(published, list) or not all(isinstance(k, str) for k in published):
        return (), ["%s must be a list of key names" % DECLARED_ATTR]
    if module is not None:
        mine = list(getattr(module, "POPULATION_KEYS", ()))
        if sorted(mine) != sorted(published):
            problems.append("the face declares %r but the producer declares %r"
                            % (sorted(published), sorted(mine)))
    return tuple(published), problems


def compare(published, fresh, keys, where=""):
    """Problems with `fresh` against the published summary, treating `keys` as population counts.

    Readings must be identical.  Population counts must be present on both sides and be plain
    integers (a float or a bool in a count column is a different defect), but they are allowed to
    move -- and the movement is returned by `drift()` so a caller can publish it.
    """
    problems = []
    tag = where or "summary"
    keys = tuple(keys or ())
    for k in keys:
        if k not in published:
            problems.append("%s: declared population key %r is not published" % (tag, k))
            continue
        if k not in fresh:
            problems.append("%s: declared population key %r is not produced any more" % (tag, k))
            continue
        for side, value in (("published", published[k]), ("fresh", fresh[k])):
            if isinstance(value, bool) or not isinstance(value, int):
                problems.append("%s: population key %r is %s on the %s side"
                                % (tag, k, type(value).__name__, side))
    for k in sorted(set(published) | set(fresh)):
        if k in keys:
            continue
        if published.get(k) != fresh.get(k):
            problems.append("%s.%s moved: %r vs %r"
                            % (tag, k, published.get(k), fresh.get(k)))
    return problems


def drift(published, fresh, keys):
    """{key: (published, fresh)} for the population counts that moved -- published, not hidden."""
    out = {}
    for k in tuple(keys or ()):
        a, b = published.get(k), fresh.get(k)
        if a != b:
            out[k] = (a, b)
    return out


def selftest():
    """Legs that prove the gate still discriminates, not just that it passes."""
    results = []

    def check(name, ok):
        results.append((name, bool(ok)))

    pub = {"readers": 4, "corpus_py_files": 10}
    fresh_same = {"readers": 4, "corpus_py_files": 10}
    fresh_grown = {"readers": 4, "corpus_py_files": 11}
    fresh_reading = {"readers": 5, "corpus_py_files": 10}
    check("an unchanged face passes", compare(pub, fresh_same, ("corpus_py_files",)) == [])
    check("a moved population count passes but is disclosed",
          compare(pub, fresh_grown, ("corpus_py_files",)) == []
          and drift(pub, fresh_grown, ("corpus_py_files",)) == {"corpus_py_files": (10, 11)})
    check("a moved reading still goes red",
          any("readers moved" in p for p in compare(pub, fresh_reading, ("corpus_py_files",))))
    check("an undeclared key cannot be excluded by the leg",
          any("corpus_py_files moved" in p for p in compare(pub, fresh_grown, ())))
    check("a declared key absent from the face is refused",
          any("is not published" in p
              for p in compare({"readers": 4}, {"readers": 4}, ("corpus_py_files",))))
    check("a float in a count column is refused",
          any("is float on the published side" in p
              for p in compare({"n": 1.0}, {"n": 1}, ("n",))))
    check("a bool in a count column is refused",
          any("is bool" in p for p in compare({"n": True}, {"n": 1}, ("n",))))

    class _M:
        POPULATION_KEYS = ("corpus_py_files",)

    face = {"population_keys": ["corpus_py_files"]}
    check("a matching declaration is clean", keys_of(face, _M)[1] == [])
    check("a face that widens the list is caught",
          keys_of({"population_keys": ["corpus_py_files", "readers"]}, _M)[1] != [])
    check("a face that declares nothing is caught",
          keys_of({}, _M)[1] != [])
    return results


if __name__ == "__main__":
    import sys

    legs = selftest()
    for name, ok in legs:
        print(("PASS " if ok else "FAIL ") + name)
    print("legs %d/%d" % (sum(1 for _, ok in legs if ok), len(legs)))
    sys.exit(0 if all(ok for _, ok in legs) else 1)