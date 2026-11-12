"""Does every published face that prints a premium percentage name the session it belongs to?

WHY THIS EXISTS: r1605..r1610 fixed five faces in a row that each read "today" as the price
panel's last row (premium_leak, persistence, percentile, forward, subscription). Each was found
by a person reading a page and noticing a number that could not be dated. A sixth copy would
have to be found the same way -- by eye -- unless something mechanical reads the whole tree.

WHAT THIS LEG CAN AND CANNOT SAY: it answers "does the face carry a field that lets a reader
locate the session", not "is every premium priced on its own denominator". A face can name a
session and still mix one leg's NAV stamp with another's price bar (that is r1605's defect, and
it needs the per-leg date to be checked against the leg, not the document). The narrow claim is
deliberate: it is the cheap question whose answer is true for the whole tree today, so a red
here means a face was published with no date at all -- the shape a sixth copy would arrive in.

USAGE:
    python Tools/premium_session_guard.py            # report (exit 0 always, --check gates)
    python Tools/premium_session_guard.py --check    # rc1 when a face is undatable
    python Tools/premium_session_guard.py --selftest # offline invariants
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A key that answers "which session is this number from". `date`/`cutoff` are the loose ends a
# face uses when it has one reading; the named ones are what the premium family settled on.
SESSION_KEYS = (
    "nav_session", "priced_session", "ticket_session", "base_bar", "as_of",
    "nav_date", "evidence_cutoff", "session", "cutoff", "date",
)

# results/_* are scratch captures that quote raw payloads on purpose (the repo's own underscore
# convention, same scope the conflict-marker leg uses).
SCRATCH_PREFIX = "_"
MAX_BYTES = 8_000_000


def premium_sites(obj, trail=()):
    """Every dict that prints a premium percentage, with the trail that leads to it."""
    out = []
    if isinstance(obj, dict):
        if "premium_pct" in obj:
            out.append((trail, obj))
        for key, val in obj.items():
            out.extend(premium_sites(val, trail + (key,)))
    elif isinstance(obj, list):
        for idx, val in enumerate(obj):
            out.extend(premium_sites(val, trail + (idx,)))
    return out


def _chain(doc, trail):
    """Every ancestor of a site, root first (so a document-level date counts for a nested leg)."""
    chain = [doc]
    cur = doc
    for step in trail:
        cur = cur[step] if not isinstance(cur, list) else cur[step]
        chain.append(cur)
    return chain


def undatable(path):
    """(has_premium, [(trail, why)]) for one face; (False, None) when the JSON cannot be read.

    An unreadable file is json_face_guard's leg, not this one -- reporting it here would make two
    legs red for one defect and teach readers to ignore whichever one they meet first.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception:
        return None, None
    sites = premium_sites(doc)
    if not sites:
        return False, []
    bad = []
    for trail, _obj in sites:
        chain = _chain(doc, trail)
        if not any(isinstance(level, dict) and any(k in level for k in SESSION_KEYS)
                   for level in chain):
            bad.append((trail, "no session key on the site or any ancestor"))
    return True, bad


def faces():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "results", "**", "*.json"), recursive=True)):
        if os.path.basename(path).startswith(SCRATCH_PREFIX):
            continue
        try:
            if os.path.getsize(path) > MAX_BYTES:
                continue
        except OSError:
            continue
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        out.append((rel, path))
    return out


def audit():
    scanned, printed, red = 0, 0, []
    for rel, path in faces():
        scanned += 1
        has_premium, bad = undatable(path)
        if not has_premium:
            continue
        printed += 1
        for trail, why in bad:
            red.append({"path": rel, "trail": "/".join(str(s) for s in trail) or "<root>",
                        "why": why})
    return {"scanned": scanned, "faces_printing_premium": printed, "undatable": red}


def selftest():
    checks = []

    def chk(name, ok):
        checks.append((name, bool(ok)))

    # 1. a site with its own date passes
    doc = {"legs": [{"symbol": "A", "premium_pct": 1.0, "nav_session": "2026-01-02"}]}
    chk("a leg that names its own session is datable",
        not premium_sites(doc) or all(
            any(k in obj for k in SESSION_KEYS) for _t, obj in premium_sites(doc)))
    # 2. a document-level date reaches a nested leg (the qdii shape: date on the parent face)
    doc2 = {"nav_date": "2026-09-30", "top10_target": [{"premium_pct": 2.0}]}
    trail, obj = premium_sites(doc2)[0]
    chain = _chain(doc2, trail)
    chk("a document-level date covers a nested leg",
        any(isinstance(l, dict) and "nav_date" in l for l in chain))
    # 3. nothing anywhere -> red (the shape a sixth copy arrives in)
    doc3 = {"top10_target": [{"premium_pct": 2.0}]}
    trail, _ = premium_sites(doc3)[0]
    chk("no session anywhere is undatable",
        not any(isinstance(l, dict) and any(k in l for k in SESSION_KEYS)
                for l in _chain(doc3, trail)))
    # 4. a site inside a list inside a list still resolves
    doc4 = {"date": "2026-02-03", "grid": [[{"premium_pct": 3.0}]]}
    trail, _ = premium_sites(doc4)[0]
    chk("a doubly nested site resolves its ancestry", chain_has_date(doc4, trail))
    # 5. a face with no premium at all is out of scope
    chk("a face with no premium is not in scope", premium_sites({"rows": [{"nav": 1.0}]}) == [])
    # 6. scratch files are excluded by name, not by list
    chk("scratch prefix is the underscore convention", SCRATCH_PREFIX == "_")
    # 7. every session key is a string and none is empty
    chk("session keys are well formed", all(isinstance(k, str) and k for k in SESSION_KEYS))

    ok = sum(1 for _n, v in checks if v)
    for name, verdict in checks:
        print("%-55s %s" % (name, "PASS" if verdict else "FAIL"))
    print("selftest: %d/%d" % (ok, len(checks)))
    return 0 if ok == len(checks) else 1


def chain_has_date(doc, trail):
    return any(isinstance(l, dict) and any(k in l for k in SESSION_KEYS)
               for l in _chain(doc, trail))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    res = audit()
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print("premium session guard: %d file(s) scanned, %d print a premium, %d undatable site(s)"
              % (res["scanned"], res["faces_printing_premium"], len(res["undatable"])))
        for row in res["undatable"][:20]:
            print("  UNDATABLE %s [%s] -- %s" % (row["path"], row["trail"], row["why"]))
    if a.check and res["undatable"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
