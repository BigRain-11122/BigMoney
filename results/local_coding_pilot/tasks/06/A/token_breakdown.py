"""token_breakdown.py — per-leg incremental breakdown of token_usage.json.

Task 06 of the T-70 local-coding pilot (frozen prompt
results/local_coding_pilot/tasks/06/prompt.md, commit 6958d24a).

Reads the token-meter snapshot face and derives a per-leg table: two fixed
context legs (mandate/CODELY read load) plus per-machine state/report legs
derived from the machines map — never from the declared top-level totals,
which are instead cross-checked against the derived sums (mismatch = exit 1
warning bit). A delta line reports snapshot-over-snapshot growth when the
meter recorded one.

Exit codes: 0 ok | 1 cross-check mismatch warning | 2 usage/schema/IO error.
"""

import io
import json
import os
import sys

REQUIRED_KEYS = (
    "generated",
    "per_round_context",
    "machines",
    "total_state_tokens_est",
    "total_report_tokens_est",
)


def _is_int(v):
    """True only for real ints (bool excluded, per frozen spec)."""
    return isinstance(v, int) and not isinstance(v, bool)


def _leg_val(d, key):
    """Leg value with tolerant consumption: missing/non-int -> 0."""
    v = d.get(key)
    return v if _is_int(v) else 0


def validate(usage):
    """Return error string for schema violations, or None when valid."""
    if not isinstance(usage, dict):
        return "usage face is not a JSON object"
    for k in REQUIRED_KEYS:
        if k not in usage:
            return f"missing required key: {k}"
    if not isinstance(usage["per_round_context"], dict):
        return "per_round_context is not an object"
    if not isinstance(usage["machines"], dict):
        return "machines is not an object"
    for k in ("total_state_tokens_est", "total_report_tokens_est"):
        if not _is_int(usage[k]):
            return f"{k} is not an int"
    return None


def derive(usage):
    """Derive legs/cross/delta faces from a validated usage dict."""
    ctx = usage["per_round_context"]
    legs = [
        ("mandate", _leg_val(ctx, "mandate_read_tokens_est")),
        ("codely", _leg_val(ctx, "codely_read_tokens_est")),
    ]
    malformed = 0
    for mid, m in sorted(usage["machines"].items()):
        if not isinstance(m, dict):
            malformed += 1
            continue
        legs.append((mid + "/state", _leg_val(m, "state_tokens_est")))
        legs.append((mid + "/report", _leg_val(m, "report_tokens_est")))

    grand = sum(n for _, n in legs)
    derived_state = sum(n for name, n in legs if name.endswith("/state"))
    derived_report = sum(n for name, n in legs if name.endswith("/report"))
    cross_state = derived_state == usage["total_state_tokens_est"]
    cross_report = derived_report == usage["total_report_tokens_est"]

    delta = usage.get("delta_vs_prev")
    if isinstance(delta, dict):
        g = lambda k: v if _is_int(v := delta.get(k)) else 0  # noqa: E731
        delta_line = "DELTA state={} report={} mandate={} vs={}".format(
            "{:+d}".format(g("state_tokens_growth")),
            "{:+d}".format(g("report_tokens_growth")),
            "{:+d}".format(g("mandate_growth")),
            delta.get("prev_generated", "unknown"),
        )
    else:
        delta_line = "DELTA absent"

    return {
        "legs": legs,
        "grand": grand,
        "malformed": malformed,
        "derived_state": derived_state,
        "derived_report": derived_report,
        "cross_state": cross_state,
        "cross_report": cross_report,
        "delta_line": delta_line,
    }


def share_x10(n, grand):
    """Half-up percent*10 via integer math (float round is banker's)."""
    if grand == 0:
        return 0
    return (n * 1000 + grand // 2) // grand


def render(d):
    """Fixed line order: summary, legs desc, cross, delta."""
    lines = [
        "TOKENS grand={} legs={} malformed={} state_derived={} "
        "report_derived={}".format(
            d["grand"], len(d["legs"]), d["malformed"],
            d["derived_state"], d["derived_report"])
    ]
    for name, n in sorted(d["legs"], key=lambda t: (-t[1], t[0])):
        lines.append("LEG {} tokens={} share_pct={:.1f}".format(
            name, n, share_x10(n, d["grand"]) / 10))
    lines.append("CROSS state={} report={}".format(
        str(d["cross_state"]).lower(), str(d["cross_report"]).lower()))
    lines.append(d["delta_line"])
    return lines


def _selftest():
    """Offline assertions on pure functions (no repo files, no writes)."""
    ok = 0
    base = {
        "generated": "2026-09-26 00:00:00",
        "per_round_context": {"mandate_read_tokens_est": 6600,
                              "codely_read_tokens_est": 13060},
        "machines": {"bm-a": {"state_tokens_est": 1041,
                               "report_tokens_est": 143989},
                     "-bm-c": {"state_tokens_est": 700,
                               "report_tokens_est": 37894}},
        "total_state_tokens_est": 1741,
        "total_report_tokens_est": 181883,
        "delta_vs_prev": {"prev_generated": "2026-09-25 23:50:00",
                          "state_tokens_growth": 10,
                          "report_tokens_growth": 1871,
                          "mandate_growth": 0},
    }
    # legal 1: full face, delta present, cross true
    assert validate(base) is None
    d = derive(base)
    assert d["grand"] == 6600 + 13060 + 1041 + 143989 + 700 + 37894
    assert len(d["legs"]) == 6 and d["malformed"] == 0
    assert d["cross_state"] is True and d["cross_report"] is True
    assert d["derived_state"] == 1741 and d["derived_report"] == 181883
    lines = render(d)
    assert lines[0] == "TOKENS grand=203284 legs=6 malformed=0 " \
                       "state_derived=1741 report_derived=181883", lines[0]
    # desc order: biggest leg first
    assert lines[1].startswith("LEG bm-a/report tokens=143989 "), lines[1]
    assert lines[-2] == "CROSS state=true report=true", lines[-2]
    assert lines[-1] == "DELTA state=+10 report=+1871 mandate=+0 " \
                        "vs=2026-09-25 23:50:00", lines[-1]
    ok += 1
    # legal 2: cross mismatch -> both false flags
    bad = dict(base, total_state_tokens_est=999, total_report_tokens_est=999)
    d2 = derive(bad)
    assert d2["cross_state"] is False and d2["cross_report"] is False
    assert render(d2)[-2] == "CROSS state=false report=false"
    ok += 1
    # violation 1: non-dict machine member -> malformed=1, no legs for it
    m1 = dict(base, machines={"bm-a": {"state_tokens_est": 5,
                                       "report_tokens_est": 7},
                             "broken": "not-a-dict"})
    d3 = derive(m1)
    assert d3["malformed"] == 1 and len(d3["legs"]) == 4
    assert all(not name.startswith("broken") for name, _ in d3["legs"])
    ok += 1
    # violation 2: missing required key -> error classification
    m2 = {k: v for k, v in base.items() if k != "machines"}
    assert validate(m2) == "missing required key: machines"
    ok += 1
    # violation 3: context keys absent -> both context legs 0
    m3 = dict(base, per_round_context={},
              total_state_tokens_est=1741, total_report_tokens_est=181883)
    d4 = derive(m3)
    ctx_legs = [n for name, n in d4["legs"] if name in ("mandate", "codely")]
    assert ctx_legs == [0, 0]
    ok += 1
    # violation 4: grand=0 -> all shares 0.0, summary grand=0
    m4 = dict(base, machines={}, per_round_context={},
              total_state_tokens_est=0, total_report_tokens_est=0)
    d5 = derive(m4)
    assert d5["grand"] == 0 and len(d5["legs"]) == 2
    assert share_x10(0, 0) == 0
    assert render(d5)[0].startswith("TOKENS grand=0 legs=2 ")
    assert all(l.startswith("LEG mandate tokens=0 share_pct=0.0")
               or l.startswith("LEG codely tokens=0 share_pct=0.0")
               or not l.startswith("LEG") for l in render(d5))
    ok += 1
    # violation 5: delta absent -> DELTA absent line
    m5 = {k: v for k, v in base.items() if k != "delta_vs_prev"}
    assert derive(m5)["delta_line"] == "DELTA absent"
    assert "delta_vs_prev" not in m5
    ok += 1
    # violation 6: half-up pinning (float round would give 31.2)
    assert share_x10(5, 16) == 313 and "{:.1f}".format(313 / 10) == "31.3"
    ok += 1
    # negative delta sign rendering
    neg = dict(base, delta_vs_prev={"state_tokens_growth": -3})
    assert derive(neg)["delta_line"] == \
        "DELTA state=-3 report=+0 mandate=+0 vs=unknown"
    ok += 1
    # type guards: bool/float legs count as 0; bool totals = schema error
    m6 = dict(base, machines={"bm-a": {"state_tokens_est": True,
                                       "report_tokens_est": 1.5}})
    d6 = derive(m6)
    assert all(n == 0 for name, n in d6["legs"] if "bm-a" in name)
    assert validate(dict(base, total_state_tokens_est=True)) is not None
    ok += 1
    print(f"selftest: {ok} assertions ALL PASS")
    return 0


def main(argv):
    if len(argv) == 1:
        print("usage: token_breakdown.py selftest | [usage_json_path]")
        return 2
    if argv[1] == "selftest":
        return _selftest()
    path = argv[1] if len(argv) > 1 else "results/token_usage.json"
    if not os.path.isfile(path):
        print(f"file not found: {path}", file=sys.stderr)
        return 2
    try:
        usage = json.loads(io.open(path, encoding="utf-8").read())
    except (ValueError, OSError) as e:
        print(f"cannot parse {path}: {e}", file=sys.stderr)
        return 2
    err = validate(usage)
    if err:
        print(err, file=sys.stderr)
        return 2
    d = derive(usage)
    for line in render(d):
        print(line)
    return 0 if (d["cross_state"] and d["cross_report"]) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
