"""Does every printed premium sit on a NAV from its own session -- and if not, is that said out loud?

WHY THIS EXISTS: Tools/premium_session_guard.py answers the document-level question ("does this face
carry a field that lets a reader locate the session") and says so in its own docstring. The
question the five rounds r1605..r1609 were actually about is one level down: a row can be dated
and still be priced against ANOTHER session's net asset value. That is what cost the 2026-11-12
ticket CNY 8,974 of imaginary premium (159655: price of 11-12 against a NAV dated 11-13, printed as
"you paid 1.75% over" when the same ticket was in fact 0.49% under). r1605 fixed the consumer by
hand. Nothing stopped the producer from doing it again.

WHAT THIS LEG SAYS, per premium site (any dict carrying `premium_pct`):
  SAME_SESSION          the leg's own denominator date equals the session its face prices
  FOREIGN_NAV_NO_MONEY  the leg is priced against another session's NAV but carries no CNY figure
                        (this is the shape a lagging cross-border fund always has -- allowed, but it
                        has to be named in the face's disclosure lists to count as DISCLOSED)
  FOREIGN_NAV_UNDISCLOSED  foreign NAV, no money, and the face never names it -> RED
  MONEY_ON_FOREIGN_NAV  foreign NAV and a CNY premium figure -> RED (the r1605 defect)
  UNDATED_LEG           the leg carries no denominator date of its own -> counted, not red. Two
                        populations land here and the report names both: boards published before
                        the per-row stamp existed (they cannot be re-dated after the fact without
                        re-pricing them on today's panel, which would be worse than saying so), and
                        faces whose denominator is the session board's own IOPV rather than a
                        published NAV (there is no per-leg NAV date to carry; the face-level
                        session is the date)
  NO_FACE_SESSION       the document prices no session at all -> counted, not red (the guard's leg)

The two reds are defects this leg can PROVE from the face alone. The two counted buckets are
disclosed as counts with the faces named, because a permanently red gate teaches readers to skip
it (E318) and a silent one hides the population it never examined.

USAGE:
    python Tools/premium_leg_session_audit.py             # report
    python Tools/premium_leg_session_audit.py --check     # rc1 on a provable red
    python Tools/premium_leg_session_audit.py --json      # machine face
    python Tools/premium_leg_session_audit.py --probe     # re-create the r1605 defect in memory
    python Tools/premium_leg_session_audit.py --selftest  # offline invariants
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import premium_session_guard as _guard  # noqa: E402  (single walker, single definition of a site)

ROOT = _guard.ROOT

# The date of the leg's own denominator. Ordered: the first key present on the site wins.
LEG_DATE_KEYS = ("nav_session", "nav_date", "target_nav_date", "baseline_nav_date")

# Which session the face claims to price. evidence_cutoff is deliberately absent: it is the max of
# the legs' tails, so a face that only carries it cannot say what its rows are priced on.
FACE_SESSION_KEYS = ("session", "ticket_session", "iopv_session", "base_bar", "as_of")

# A CNY figure that a reader will act on. `amount_cny` is NOT here: that is the position size, not
# a statement about the premium.
MONEY_KEYS = ("premium_paid_cny", "over_nav_cny", "basket_gain_cny", "premium_cny")

# Keys under which a face names the legs it is NOT counting. Presence of the symbol as a string
# anywhere below one of these is what turns FOREIGN_NAV_NO_MONEY into DISCLOSED.
DISCLOSURE_KEY_HINTS = ("unverified", "lagging", "cross_session", "off_session", "excluded",
                        "unpriced", "not_counted")

SAME, FOREIGN_OK, FOREIGN_UNDISCLOSED, MONEY_ON_FOREIGN, UNDATED, NO_FACE_SESSION = (
    "SAME_SESSION", "FOREIGN_NAV_DISCLOSED", "FOREIGN_NAV_UNDISCLOSED", "MONEY_ON_FOREIGN_NAV",
    "UNDATED_LEG", "NO_FACE_SESSION")

RED_STATES = (FOREIGN_UNDISCLOSED, MONEY_ON_FOREIGN)


def _str(value):
    return value if isinstance(value, str) and value.strip() else None


def leg_date(site):
    for key in LEG_DATE_KEYS:
        got = _str(site.get(key))
        if got:
            return got, key
    return None, None


def face_session(doc, trail):
    """The nearest ancestor that says which session this face prices, and the key that said it."""
    for level in reversed(_guard._chain(doc, trail)):
        if not isinstance(level, dict):
            continue
        for key in FACE_SESSION_KEYS:
            got = _str(level.get(key))
            if got:
                return got, key
    return None, None


def _collect_names(node, out):
    """Every string a disclosure block points at: bare symbols, or rows that carry a symbol."""
    if isinstance(node, str):
        out.add(node)
    elif isinstance(node, dict):
        for key in ("symbol", "code", "name"):
            got = _str(node.get(key))
            if got:
                out.add(got)
        for key, val in node.items():
            if key not in ("symbol", "code", "name"):
                _collect_names(val, out)
    elif isinstance(node, list):
        for item in node:
            _collect_names(item, out)


def disclosed_names(doc):
    """Symbols the face itself lists as not counted (anywhere under a disclosure-ish key)."""
    out = set()

    def walk(node):
        if isinstance(node, dict):
            for key, val in node.items():
                flat = str(key).lower()
                if any(hint in flat for hint in DISCLOSURE_KEY_HINTS):
                    _collect_names(val, out)
                walk(val)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(doc)
    return out


def money_on(site):
    """The first CNY premium figure the site carries, with its key. None when the site is priced."""
    for key in MONEY_KEYS:
        val = site.get(key)
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return float(val), key
    return None, None


def symbol_of(site):
    for key in ("symbol", "code", "name"):
        got = _str(site.get(key))
        if got:
            return got
    return None


def classify(doc, trail, site, named=None):
    """One verdict for one premium site. `named` lets a caller pass a pre-computed name set."""
    sess, sess_key = face_session(doc, trail)
    ld, ld_key = leg_date(site)
    if ld is None:
        return {"state": UNDATED, "leg_date": None, "leg_date_key": None,
                "face_session": sess, "face_session_key": sess_key, "money_key": None,
                "money_cny": None,
                "why": "the row carries no date for its own denominator"}
    if sess is None:
        return {"state": NO_FACE_SESSION, "leg_date": ld, "leg_date_key": ld_key,
                "face_session": None, "face_session_key": None, "money_key": None,
                "money_cny": None,
                "why": "no ancestor says which session this face prices"}
    amount, money_key = money_on(site)
    if ld == sess:
        return {"state": SAME, "leg_date": ld, "leg_date_key": ld_key,
                "face_session": sess, "face_session_key": sess_key,
                "money_key": money_key, "money_cny": amount,
                "why": "the denominator belongs to the session the face prices"}
    if amount is not None:
        return {"state": MONEY_ON_FOREIGN, "leg_date": ld, "leg_date_key": ld_key,
                "face_session": sess, "face_session_key": sess_key,
                "money_key": money_key, "money_cny": amount,
                "why": "a CNY premium is struck against a NAV from %s, not this face's %s"
                       % (ld, sess)}
    names = disclosed_names(doc) if named is None else named
    sym = symbol_of(site)
    if sym in names:
        return {"state": FOREIGN_OK, "leg_date": ld, "leg_date_key": ld_key,
                "face_session": sess, "face_session_key": sess_key,
                "money_key": None, "money_cny": None,
                "why": "priced against %s; the face names it as not counted" % ld}
    return {"state": FOREIGN_UNDISCLOSED, "leg_date": ld, "leg_date_key": ld_key,
            "face_session": sess, "face_session_key": sess_key,
            "money_key": None, "money_cny": None,
            "why": "priced against %s and nothing in the face says this leg was set aside" % ld}


OWN_FACE = "results/premium_leg_session_audit.json"


def audit():
    faces, sites, states = [], 0, {}
    for rel, path in _guard.faces():
        if rel == OWN_FACE:
            # The naming rule above (quoted_*, never a bare premium_pct) is what keeps this face out
            # of both readers' scope. Skipping it by name is the belt: if a later field ever prints
            # a bare premium again, the audit must not count its own quotation on the next run.
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except Exception:
            continue  # unreadable JSON is json_face_guard's leg, not this one
        found = _guard.premium_sites(doc)
        if not found:
            continue
        named = disclosed_names(doc)
        rows = []
        for trail, site in found:
            sites += 1
            verdict = classify(doc, trail, site, named)
            verdict["path"] = rel
            verdict["trail"] = "/".join(str(s) for s in trail) or "<root>"
            verdict["symbol"] = symbol_of(site)
            # Quoted, not printed: a face that republishes another face's `premium_pct` becomes a
            # premium face itself, and on the second run the audit would audit its own quotation
            # (44 legs -> 88, every quoted row undated). The value is kept under a name that says
            # it is a quotation, which is also what keeps it out of both readers' scope.
            verdict["quoted_premium_pct"] = site.get("premium_pct")
            rows.append(verdict)
            states[verdict["state"]] = states.get(verdict["state"], 0) + 1
        faces.append({
            "path": rel,
            "sites": len(rows),
            "face_session": rows[0]["face_session"],
            "states": _count(rows),
            "legs": rows,
        })
    red = [r for f in faces for r in f["legs"] if r["state"] in RED_STATES]
    return {
        "artifact": "results/premium_leg_session_audit.json",
        "faces_with_premium": len(faces),
        "sites": sites,
        "states": states,
        "red": len(red),
        "red_legs": [{"path": r["path"], "trail": r["trail"], "symbol": r["symbol"],
                      "state": r["state"], "why": r["why"]} for r in red],
        "faces": faces,
    }


def _count(rows):
    out = {}
    for row in rows:
        out[row["state"]] = out.get(row["state"], 0) + 1
    return out


def probe():
    """Re-create the r1605 defect on a real published board, in memory, and show the leg bites."""
    import glob
    boards = sorted(glob.glob(os.path.join(ROOT, "results", "etf_premium", "PREMIUM-20*.json")))
    for path in reversed(boards):
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        sess, _k = face_session(doc, ("legs", 0)) if _guard.premium_sites(doc) else (None, None)
        foreign = []
        for trail, site in _guard.premium_sites(doc):
            got, _key = leg_date(site)
            if got and sess and got != sess:
                foreign.append((trail, site))
        if not foreign:
            continue
        trail, site = foreign[0]
        before = classify(doc, trail, site)
        sym = symbol_of(site)
        # The exact shape of the defect: put the money column back on the foreign leg and leave
        # every disclosure list untouched -- r1605's board, before the fix.
        dirty = json.loads(json.dumps(doc))
        target = dirty
        for step in trail:
            target = target[step]
        target["over_nav_cny"] = -6833.21
        after = classify(dirty, trail, target)
        print("probe: %s [%s] %s" % (os.path.basename(path), "/".join(str(s) for s in trail), sym))
        print("  as published : %s -- %s" % (before["state"], before["why"]))
        print("  with the money column put back : %s -- %s" % (after["state"], after["why"]))
        ok = before["state"] not in RED_STATES and after["state"] in RED_STATES
        print("  PROBE-OK=%s (a published foreign leg is quiet, the same leg with a CNY figure "
              "is red)" % ok)
        return 0 if ok else 1
    print("probe: no published board carries a foreign-NAV leg -- nothing to re-create")
    return 0


def selftest():
    checks = []

    def chk(name, ok):
        checks.append((name, bool(ok)))

    same = {"session": "2026-01-02", "legs": [
        {"symbol": "A", "premium_pct": 1.0, "nav_session": "2026-01-02", "over_nav_cny": -12.0}]}
    v = classify(same, ("legs", 0), same["legs"][0])
    chk("a leg on its own session is SAME even with money on it", v["state"] == SAME)

    foreign_money = {"session": "2026-01-02", "legs": [
        {"symbol": "B", "premium_pct": 7.8, "nav_session": "2026-01-03", "over_nav_cny": -6833.2}]}
    v = classify(foreign_money, ("legs", 0), foreign_money["legs"][0])
    chk("money on a foreign NAV is red", v["state"] == MONEY_ON_FOREIGN)
    chk("the red names both dates", "2026-01-03" in v["why"] and "2026-01-02" in v["why"])

    foreign_silent = {"session": "2026-01-02", "legs": [
        {"symbol": "B", "premium_pct": 7.8, "nav_session": "2026-01-03", "over_nav_cny": None}]}
    v = classify(foreign_silent, ("legs", 0), foreign_silent["legs"][0])
    chk("a foreign NAV with no money and no naming is red", v["state"] == FOREIGN_UNDISCLOSED)

    disclosed = json.loads(json.dumps(foreign_silent))
    disclosed["denominator"] = {"legs_lagging": ["B"]}
    v = classify(disclosed, ("legs", 0), disclosed["legs"][0])
    chk("a face that names the lagging leg is quiet", v["state"] == FOREIGN_OK)

    disclosed_rows = json.loads(json.dumps(foreign_silent))
    disclosed_rows["unverified_legs"] = [{"symbol": "B", "why": "cross-border"}]
    v = classify(disclosed_rows, ("legs", 0), disclosed_rows["legs"][0])
    chk("a disclosure row (not a bare string) also counts", v["state"] == FOREIGN_OK)

    undated = {"session": "2026-01-02", "legs": [{"symbol": "C", "premium_pct": 1.0,
                                                  "over_nav_cny": 5.0}]}
    v = classify(undated, ("legs", 0), undated["legs"][0])
    chk("a leg with no denominator date is undated, not red", v["state"] == UNDATED)

    nosess = {"legs": [{"symbol": "D", "premium_pct": 1.0, "nav_date": "2026-01-02"}]}
    v = classify(nosess, ("legs", 0), nosess["legs"][0])
    chk("no face session is its own bucket, not a red", v["state"] == NO_FACE_SESSION)

    qdii = {"top10_target": [{"code": "513100", "premium_pct": 2.0, "nav_date": "2026-01-02"}]}
    v = classify(qdii, ("top10_target", 0), qdii["top10_target"][0])
    chk("a document with no session at all does not silently pass as same", v["state"] == NO_FACE_SESSION)

    # the first key wins, so a row that carries several dates is read the way its producer meant
    multi = {"session": "2026-01-02", "legs": [
        {"symbol": "E", "premium_pct": 1.0, "nav_session": "2026-01-02", "nav_date": "2025-12-31"}]}
    got, key = leg_date(multi["legs"][0])
    chk("nav_session outranks nav_date", (got, key) == ("2026-01-02", "nav_session"))

    no_premium = {"rows": [{"nav": 1.0}]}
    chk("a face with no premium is out of scope", _guard.premium_sites(no_premium) == [])

    # 2026-11-13, first run of this tool: it republished each leg's premium_pct inside its own
    # artifact, so the second run audited its own quotation -- 44 legs became 88 and every quoted
    # row counted as undated. A face that quotes another face's number is a reader, not a printer.
    chk("a quoted premium is not a printed premium",
        _guard.premium_sites({"legs": [{"quoted_premium_pct": 1.0}]}) == [])
    chk("the audit's own face is skipped by name as well as by naming",
        OWN_FACE == "results/premium_leg_session_audit.json")

    chk("a money key list never contains the position size",
        "amount_cny" not in MONEY_KEYS)
    chk("evidence_cutoff is not accepted as a face session",
        "evidence_cutoff" not in FACE_SESSION_KEYS)

    ok = sum(1 for _n, v in checks if v)
    for name, verdict in checks:
        print("%-63s %s" % (name, "PASS" if verdict else "FAIL"))
    print("selftest: %d/%d" % (ok, len(checks)))
    return 0 if ok == len(checks) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.probe:
        return probe()
    res = audit()
    out = a.out or os.path.join(ROOT, "results", "premium_leg_session_audit.json")
    try:
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=1)
    except OSError as exc:
        print("could not write %s: %r" % (out, exc))
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print("premium leg session audit: %d face(s), %d premium leg(s)" %
              (res["faces_with_premium"], res["sites"]))
        for state in (SAME, FOREIGN_OK, FOREIGN_UNDISCLOSED, MONEY_ON_FOREIGN, UNDATED,
                      NO_FACE_SESSION):
            n = res["states"].get(state, 0)
            if n:
                print("  %-24s %d" % (state, n))
        for row in res["red_legs"][:20]:
            print("  RED %s [%s] %s %s -- %s"
                  % (row["path"], row["trail"], row["symbol"], row["state"], row["why"]))
        undated_faces = [f for f in res["faces"] if f["states"].get(UNDATED)]
        if undated_faces:
            print("  legs with no per-row denominator date live in: %s"
                  % ", ".join("%s (%d, session %s)" % (f["path"], f["states"][UNDATED],
                                                       f["face_session"] or "unstated")
                              for f in undated_faces))
    return 1 if (a.check and res["red"]) else 0


if __name__ == "__main__":
    sys.exit(main())
