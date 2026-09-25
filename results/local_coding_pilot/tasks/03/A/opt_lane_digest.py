"""opt_lane_digest.py -- one-line health digest for the options forward-collector gate.

Reads the status JSON written each gate tick by scripts/update_options.py
(default face: results/options_update_status.json) and prints a single
ASCII verdict line so a round report can cite lane health in one glance.

Verdict order (first hit wins, frozen in the task prompt):
  INCOMPLETE  panel.complete is not true, or universe != attempted
  DATA_ISSUE  panel.fails / panel.mismatches non-empty
  ENUM_FAIL   top-level enum_fails / mismatch non-empty
  OK          otherwise

Exit codes: 0 OK verdict | 1 any non-OK verdict | 2 usage / unreadable or
structurally invalid input. Digest mode never writes files, zero network.
"""

import io
import json
import sys

USAGE = "usage: python opt_lane_digest.py selftest | <status.json>"


def _ascii(text):
    """Guarantee the output discipline: ASCII printable only."""
    return str(text).encode("ascii", "replace").decode("ascii")


def _verdict(panel, enum_fails, mismatch):
    if panel.get("complete") is not True or panel.get("universe") != panel.get("attempted"):
        return "INCOMPLETE"
    if panel.get("fails") or panel.get("mismatches"):
        return "DATA_ISSUE"
    if enum_fails or mismatch:
        return "ENUM_FAIL"
    return "OK"


def summarize(data):
    """Map a parsed status object to (summary_line, verdict).

    Raises ValueError when the status face is structurally unusable
    (top level not an object, or panel missing / not an object).
    """
    if not isinstance(data, dict):
        raise ValueError("top-level object required")
    panel = data.get("panel")
    if not isinstance(panel, dict):
        raise ValueError("panel object required")
    enum_fails = data.get("enum_fails") or []
    mismatch = data.get("mismatch") or {}
    verdict = _verdict(panel, enum_fails, mismatch)
    # absent universe/attempted print as -1 (never collapse 0 to -1)
    u = panel.get("universe")
    a = panel.get("attempted")
    cutoff = panel.get("max_collected") or panel.get("last_pass_date") or "na"
    line = "OPT-LANE {} universe={} attempted={} cutoff={} enum_fails={} mismatch={}".format(
        verdict,
        -1 if u is None else u,
        -1 if a is None else a,
        cutoff,
        len(enum_fails),
        len(mismatch),
    )
    return line, verdict


def main(argv):
    if len(argv) < 2:
        print(USAGE)
        return 2
    if argv[1] == "selftest":
        return _selftest()
    path = argv[1]
    try:
        text = io.open(path, encoding="utf-8-sig").read()
    except OSError as exc:
        print(_ascii("cannot read {}: os error {}".format(path, exc.errno)), file=sys.stderr)
        return 2
    try:
        data = json.loads(text)
    except ValueError as exc:
        print(_ascii("json parse failed: {}".format(exc.__class__.__name__)), file=sys.stderr)
        return 2
    try:
        line, verdict = summarize(data)
    except ValueError as exc:
        print(_ascii("invalid status face: {}".format(exc)), file=sys.stderr)
        return 2
    print(_ascii(line))
    return 0 if verdict == "OK" else 1


def _selftest():
    """Offline assertions on synthetic samples; no repo files touched."""
    checks = []

    def check(name, cond):
        checks.append((name, cond))
        if not cond:
            print("FAIL: {}".format(name))
            for n, ok in checks:
                if not ok:
                    print("  failed: {}".format(n))
            return False
        return True

    # legal 1: full OK state, every in-scope key present, max_collected valued
    full_ok = {
        "mode": "no-op: cutoff covered",
        "enum_fails": [],
        "mismatch": {},
        "panel": {
            "complete": True, "universe": 200, "attempted": 200,
            "last_pass_date": "2026-09-24", "max_collected": "2026-09-24",
            "fails": [], "mismatches": [],
        },
    }
    line, verdict = summarize(full_ok)
    ok = check("legal-1 verdict OK", verdict == "OK")
    ok = check("legal-1 line format",
               line == "OPT-LANE OK universe=200 attempted=200 cutoff=2026-09-24 enum_fails=0 mismatch=0") and ok

    # legal 2: INCOMPLETE via universe != attempted
    line2, verdict2 = summarize({
        "panel": {"complete": True, "universe": 200, "attempted": 160},
    })
    ok = check("legal-2 verdict INCOMPLETE", verdict2 == "INCOMPLETE") and ok
    ok = check("legal-2 attempted segment", "attempted=160" in line2) and ok

    # boundary 1: enum_fails non-empty -> ENUM_FAIL
    _, v = summarize({
        "enum_fails": ["202610 board"], "mismatch": {},
        "panel": {"complete": True, "universe": 3, "attempted": 3},
    })
    ok = check("enum_fails triggers ENUM_FAIL", v == "ENUM_FAIL") and ok

    # boundary 2: mismatch non-empty, enum_fails empty -> still ENUM_FAIL
    _, v = summarize({
        "panel": {"complete": True, "universe": 1, "attempted": 1},
        "mismatch": {"10010971": "overlap mismatch"},
    })
    ok = check("mismatch triggers ENUM_FAIL", v == "ENUM_FAIL") and ok

    # boundary 3: panel missing -> structurally invalid
    try:
        summarize({"enum_fails": []})
        raised = False
    except ValueError:
        raised = True
    ok = check("panel missing raises", raised) and ok

    # boundary 4: max_collected null -> cutoff falls back to last_pass_date
    line4, v4 = summarize({
        "panel": {"complete": True, "universe": 2, "attempted": 2,
                  "last_pass_date": "2026-09-23", "max_collected": None},
    })
    ok = check("cutoff fallback to last_pass_date",
               v4 == "OK" and "cutoff=2026-09-23" in line4) and ok

    # short-circuit: fails non-empty + enum_fails non-empty -> DATA_ISSUE, not ENUM_FAIL
    _, v = summarize({
        "enum_fails": ["x"],
        "panel": {"complete": True, "universe": 1, "attempted": 1, "fails": ["f1"]},
    })
    ok = check("order short-circuit fails>enum_fails", v == "DATA_ISSUE") and ok

    # top-level non-object rejected
    try:
        summarize([1, 2, 3])
        raised = False
    except ValueError:
        raised = True
    ok = check("top-level non-object raises", raised) and ok

    if not ok:
        return 1
    print("selftest: {} assertions ALL PASS".format(len(checks)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
