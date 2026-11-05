"""E455: a census over a growing tree re-reds one round after its republish, because the leg demands
exact equality between the stored summary and a fresh reading while the corpus gains rows every
round.  r1473 measured the delta as pure growth (227->232 readers, 265->266 sites, 230->233 faces,
verdicts unchanged) but the leg cannot tell that apart from a corruption.

This module is the smallest tolerance rule that still catches a changed row, a changed verdict and a
shrink.  It is deliberately structural, not per-leg: the leg hands over the published payload, the
fresh payload, the list key that carries the rows, the row's identity field and (optionally) the
fields that hold the row's CLASS.  It gets back a verdict plus a priced account of what moved.

Why row payloads are not compared: these rows carry live measurements -- a reader site carries its
`smoke_test.py` line number, an unfloored face carries its age in days -- so payload equality can
never hold while the tree grows, and a leg that demands it re-reds for a reason that is not a defect.
The stable identity of a row is its name, and the stable claim it makes is its class.  So the rule
compares names (a name that vanished is a changed population) and declared class fields (a class
that flipped is a changed claim), and leaves the measurements to the summary, where a count may only
move up.

Frozen vocabulary:

    identical              stored and fresh agree on names, classes, summary and verdict
    pure_growth            nothing was lost, the verdict is unchanged, every integer count did not
                           decrease, every non-numeric leaf that existed still has its value, and
                           something moved upward -- i.e. everything that moved is explained by rows
                           that appeared or measurements that only grew
    lost_row               a stored row is absent from the fresh reading
    class_moved            a declared class field changed on a row that is still present
    shrank                 a stored integer count came back smaller
    verdict_moved          the stored verdict is not the one the fresh reading produces
    moved_without_growth   the payload differs while nothing grew (a corruption, not growth)
    changed_value          a non-numeric leaf changed value or disappeared

Why floats are allowed to fall: a share of sites that can go red moves with its denominator, so a
legitimate growth can pull a derived ratio down.  Integers are counts, so their only legal direction
is up.

Usage:
    python scripts/growth_tolerance.py selftest
"""
from __future__ import annotations

import json
import sys

IDENTICAL = "identical"
PURE_GROWTH = "pure_growth"
LOST_ROW = "lost_row"
CLASS_MOVED = "class_moved"
SHRANK = "shrank"
VERDICT_MOVED = "verdict_moved"
MOVED_WITHOUT_GROWTH = "moved_without_growth"
CHANGED_VALUE = "changed_value"

DERIVED_HINTS = ("share", "ratio", "mean", "median", "pct", "percent", "rate")


def _is_derived(path):
    low = "/".join(str(p) for p in path).lower()
    return any(h in low for h in DERIVED_HINTS)


def _walk(pub, fresh, path=(), out=None):
    """Every leaf that differs, as (path, published, fresh); added/removed keys included."""
    if out is None:
        out = []
    if isinstance(pub, dict) and isinstance(fresh, dict):
        for k in pub:
            if k not in fresh:
                out.append((path + (k,), pub[k], None))
            else:
                _walk(pub[k], fresh[k], path + (k,), out)
        for k in fresh:
            if k not in pub:
                out.append((path + (k,), None, fresh[k]))
        return out
    if pub != fresh:
        out.append((path, pub, fresh))
    return out


def _index(payload, list_key, row_id):
    rows = payload.get(list_key) or []
    if not row_id:
        return {}
    return {r.get(row_id): r for r in rows if isinstance(r, dict)}


def classify(published, fresh, list_key="faces", row_id="face", class_fields=()):
    """Price the distance between a stored census face and a fresh reading of the same study."""
    pub_rows = _index(published, list_key, row_id)
    fresh_rows = _index(fresh, list_key, row_id)
    lost = sorted(set(pub_rows) - set(fresh_rows))
    added = sorted(set(fresh_rows) - set(pub_rows))
    class_moved = sorted(
        name for name in (set(pub_rows) & set(fresh_rows))
        for field in class_fields
        if pub_rows[name].get(field) != fresh_rows[name].get(field)
    )
    deltas = _walk(published.get("summary") or {}, fresh.get("summary") or {})

    pub_verdict = published.get("verdict")
    fresh_verdict = fresh.get("verdict")

    tolerated = []
    violations = []
    grew = bool(added)
    for path, pub_v, fresh_v in deltas:
        name = "/".join(str(p) for p in path)
        if pub_v is None:
            # A section or count that appeared is a census after growth; a string or list that
            # appeared is a new claim the stored face never made.
            if isinstance(fresh_v, (dict, list)) or (
                    isinstance(fresh_v, (int, float)) and not isinstance(fresh_v, bool)):
                tolerated.append({"path": name, "why": "key_added", "fresh": fresh_v})
                grew = True
            else:
                violations.append({"path": name, "why": "key_added_non_numeric",
                                   "fresh": fresh_v})
            continue
        if fresh_v is None:
            violations.append({"path": name, "why": "key_removed", "published": pub_v})
            continue
        if isinstance(pub_v, list) and isinstance(fresh_v, list):
            gone = [x for x in pub_v if x not in fresh_v]
            if gone:
                violations.append({"path": name, "why": "list_member_removed",
                                   "removed": gone[:5], "removed_count": len(gone)})
            else:
                tolerated.append({"path": name, "why": "list_grew",
                                  "published": len(pub_v), "fresh": len(fresh_v)})
                grew = grew or len(fresh_v) > len(pub_v)
            continue
        numeric = (isinstance(pub_v, (int, float)) and isinstance(fresh_v, (int, float))
                   and not isinstance(pub_v, bool) and not isinstance(fresh_v, bool))
        if not numeric:
            violations.append({"path": name, "why": "value_changed",
                               "published": pub_v, "fresh": fresh_v})
            continue
        if isinstance(pub_v, int) and isinstance(fresh_v, int):
            if fresh_v < pub_v:
                violations.append({"path": name, "why": "count_decreased",
                                   "published": pub_v, "fresh": fresh_v})
            else:
                tolerated.append({"path": name, "why": "count_grew",
                                  "published": pub_v, "fresh": fresh_v})
                grew = grew or fresh_v > pub_v
            continue
        # A float is a derived quantity: it moves with its denominator, either direction.
        tolerated.append({"path": name, "why": "derived_moved",
                          "published": pub_v, "fresh": fresh_v, "derived": _is_derived(path)})
        grew = True

    if lost:
        verdict = LOST_ROW
    elif pub_verdict != fresh_verdict:
        verdict = VERDICT_MOVED
    elif class_moved and not grew:
        verdict = CLASS_MOVED
    elif any(v["why"] == "count_decreased" for v in violations):
        verdict = SHRANK
    elif violations:
        verdict = CHANGED_VALUE
    elif not deltas and not added and not class_moved:
        verdict = IDENTICAL
    elif grew:
        verdict = PURE_GROWTH
    else:
        verdict = MOVED_WITHOUT_GROWTH

    return {
        "verdict": verdict,
        "rows_published": len(pub_rows),
        "rows_fresh": len(fresh_rows),
        "rows_added": added,
        "rows_lost": lost,
        "classes_moved": class_moved,
        "summary_deltas": [
            {"path": "/".join(str(p) for p in path), "published": pub_v, "fresh": fresh_v}
            for path, pub_v, fresh_v in deltas
        ],
        "tolerated": [
            {"path": a["path"], "why": a["why"],
             "published": a.get("published"), "fresh": a.get("fresh")}
            for a in tolerated
        ],
        "violations": violations,
        "published_verdict": pub_verdict,
        "fresh_verdict": fresh_verdict,
    }


def tolerates(result):
    """The one question a smoke leg asks: may this difference stand as growth?"""
    return result.get("verdict") == PURE_GROWTH


def describe(result):
    """One line a leg or a round report can print without re-reading the payload."""
    if result["verdict"] == IDENTICAL:
        return "identical"
    if result["verdict"] == PURE_GROWTH:
        return ("pure growth: rows %d->%d (+%d, -%d), %d row class(es) moved, %d header value(s) "
                "moved upward" % (
                    result["rows_published"], result["rows_fresh"],
                    len(result["rows_added"]), len(result["rows_lost"]),
                    len(result["classes_moved"]), len(result["tolerated"])))
    return "%s: %s" % (result["verdict"], json.dumps(result["violations"], ensure_ascii=False))


# --------------------------------------------------------------------------- selftest

def _mk_row(name, klass="blind", line=1):
    return {"face": name, "no_reader_that_can_go_red": klass == "blind", "line": line}


def _face(rows, summary, verdict="v1", key="faces"):
    return {key: rows, "summary": summary, "verdict": verdict}


def selftest():
    ok = 0
    total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % name)

    base_rows = [_mk_row("a"), _mk_row("b")]
    base_sum = {"faces": 2, "reader_sites": 2, "share_of_sites_that_can_go_red": 0.5,
                "by_reader_tier": {"no_freshness_test": 2}}
    base = _face(base_rows, base_sum)
    cls = ("no_reader_that_can_go_red",)

    leg("identical", classify(base, base, class_fields=cls)["verdict"] == IDENTICAL)

    grown = _face(base_rows + [_mk_row("c")],
                  {"faces": 3, "reader_sites": 3,
                   "share_of_sites_that_can_go_red": 0.3333333333,
                   "by_reader_tier": {"no_freshness_test": 3}})
    r = classify(base, grown, class_fields=cls)
    leg("pure_growth verdict", r["verdict"] == PURE_GROWTH)
    leg("pure_growth rows", r["rows_added"] == ["c"] and not r["rows_lost"])
    leg("pure_growth tolerates", tolerates(r))
    leg("derived float may fall", any(t["why"] == "derived_moved" for t in r["tolerated"]))
    leg("describe names the growth", describe(r).startswith("pure growth: rows 2->3"))

    # payload churn alone (a line number moved) is not a defect
    churned = _face([_mk_row("a", line=99), _mk_row("b", line=88)], base_sum)
    leg("payload churn is identical", classify(base, churned, class_fields=cls)["verdict"]
        == IDENTICAL)

    # a stored row disappeared
    leg("lost_row", classify(base, _face([_mk_row("a")],
                                        {"faces": 1, "reader_sites": 1}, key="faces"),
                             class_fields=cls)["verdict"] == LOST_ROW)

    # an integer count shrank
    shrunk = _face(base_rows + [_mk_row("c")],
                   {"faces": 3, "reader_sites": 1, "share_of_sites_that_can_go_red": 0.5,
                    "by_reader_tier": {"no_freshness_test": 3}})
    leg("shrank", classify(base, shrunk, class_fields=cls)["verdict"] == SHRANK)

    # the verdict moved
    moved = _face(base_rows + [_mk_row("c")],
                  {"faces": 3, "reader_sites": 3,
                   "share_of_sites_that_can_go_red": 0.3333333333,
                   "by_reader_tier": {"no_freshness_test": 3}}, verdict="v2")
    leg("verdict_moved", classify(base, moved, class_fields=cls)["verdict"] == VERDICT_MOVED)

    # a class flipped with no growth anywhere: refused
    flipped = _face([_mk_row("a"), _mk_row("b", klass="red")], base_sum)
    leg("class_moved", classify(base, flipped, class_fields=cls)["verdict"] == CLASS_MOVED)

    # a class flipped while the population grew: tolerated, but disclosed
    grown_flipped = _face([_mk_row("a"), _mk_row("b", klass="red"), _mk_row("c")],
                          {"faces": 3, "reader_sites": 3,
                           "share_of_sites_that_can_go_red": 0.3333333333,
                           "by_reader_tier": {"no_freshness_test": 3}})
    r = classify(base, grown_flipped, class_fields=cls)
    leg("class move is disclosed under growth", r["verdict"] == PURE_GROWTH
        and r["classes_moved"] == ["b"])

    # a list that only gained members is growth; a list that lost one is not
    grew_list = _face(base_rows, dict(base_sum, files_with_a_read_site=["a.py", "b.py"]))
    leg("list grew", classify(base, grew_list, class_fields=cls)["verdict"] == PURE_GROWTH)
    lost_list = _face(base_rows, dict(base_sum, files_with_a_read_site=["a.py"]))
    base_list = _face(base_rows, dict(base_sum, files_with_a_read_site=["a.py", "b.py"]))
    leg("list member removed",
        classify(base_list, lost_list, class_fields=cls)["verdict"] == CHANGED_VALUE)

    # a string key that appeared while nothing grew: growth cannot explain it
    leg("added key without growth",
        classify(base, _face(base_rows, dict(base_sum, tag="x")), class_fields=cls)["verdict"]
        == CHANGED_VALUE)

    # a non-numeric value replaced a count
    leg("changed value",
        classify(base, _face(base_rows, dict(base_sum, faces="two")), class_fields=cls)["verdict"]
        == CHANGED_VALUE)

    # a removed summary key is never tolerated
    leg("key removed",
        classify(base, _face(base_rows + [_mk_row("c")], {"faces": 3}), class_fields=cls)["verdict"]
        == CHANGED_VALUE)

    print("%d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "selftest").lower()
    if cmd == "selftest":
        return selftest()
    print("usage: python scripts/growth_tolerance.py selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))