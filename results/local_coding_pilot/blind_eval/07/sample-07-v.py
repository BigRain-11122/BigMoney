#!/usr/bin/env python3
"""leg_freshness.py -- S6 maintenance-chain per-leg freshness matrix.

T-70 local-coding pilot task 07. For each frozen S6 leg (manifest below),
read its status artifact under a results directory, parse the leg's frozen
ts field, and render a last-run age table: integer-hour age (floor),
ok/missing/bad_ts classification, stale24h flag. Stdlib only, zero
network, zero file writes.
"""

import json
import os
import sys
from datetime import datetime

# Frozen manifest (prompt rule 1): (name, status file basename, ts field)
LEGS = [
    ("ah_panel", "ah_panel_status.json", "ts"),
    ("daily", "update_status.json", "updated"),
    ("fundamental", "fundamental_status.json", "updated"),
    ("lhb", "lhb_update_status.json", "updated"),
    ("moneyflow", "moneyflow_update_status.json", "ts"),
    ("regime", "regime_state.json", "updated"),
    ("token_meter", "token_usage.json", "generated"),
]

USAGE = ("usage: leg_freshness.py [selftest | [results_dir [now_str]]] "
         "(default results_dir=results, now=wall clock)")

STATUS_RANK = {"ok": 0, "bad_ts": 1, "missing": 2}


def parse_ts(value):
    """Prompt rule 3: 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DDTHH:MM:SS' only,
    fractional seconds tolerated (truncated), naive. Else None."""
    if not isinstance(value, str) or not value:
        return None
    head = value.split(".", 1)[0]
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(head, fmt)
        except ValueError:
            continue
    return None


def digest(observations, now):
    """Core (prompt rule 7 selftest target): observations = list of
    (name, src_basename, raw_text_or_None, ts_field); now = naive datetime.
    Returns {"rows": [...], "ok": n, "missing": n, "bad": n, "stale": n}."""
    rows = []
    n_ok = n_missing = n_bad = n_stale = 0
    for name, src, raw, ts_field in observations:
        status = ts_render = None
        age_h = None
        if raw is None:
            status = "missing"
        else:
            try:
                obj = json.loads(raw)
            except (ValueError, TypeError):
                obj = None
            if not isinstance(obj, dict):
                status = "missing"
            elif ts_field not in obj:
                status = "bad_ts"
            elif not isinstance(obj[ts_field], str):
                status = "bad_ts"
                ts_render = "nonstr"
            else:
                val = obj[ts_field]
                dt = parse_ts(val)
                if dt is None:
                    status = "bad_ts"
                    ts_render = val[:60] if len(val) > 60 else val
                else:
                    status = "ok"
                    age_h = int((now - dt).total_seconds() // 3600)
                    ts_render = val
        if status == "missing":
            ts_render = "absent"
        elif status == "bad_ts" and ts_render is None:
            ts_render = "absent"
        stale = 1 if (status == "ok" and age_h >= 24) else 0
        if status == "ok":
            n_ok += 1
        elif status == "bad_ts":
            n_bad += 1
        else:
            n_missing += 1
        n_stale += stale
        rows.append({
            "name": name, "src": src, "status": status,
            "age_h": age_h, "ts": ts_render, "stale": stale,
        })
    # prompt rule 6b sort: status rank asc -> age_h desc -> name ASCII asc
    rows.sort(key=lambda r: (STATUS_RANK[r["status"]],
                             -(r["age_h"] or 0), r["name"]))
    return {"rows": rows, "ok": n_ok, "missing": n_missing,
            "bad": n_bad, "stale": n_stale}


def render(result, now):
    """Prompt rule 6: header + per-leg rows, fixed order."""
    out = ["FRESHNESS legs=%d ok=%d missing=%d bad=%d stale=%d now=%s"
           % (len(result["rows"]), result["ok"], result["missing"],
              result["bad"], result["stale"], now.strftime("%Y-%m-%d %H:%M:%S"))]
    for r in result["rows"]:
        age = "-" if r["age_h"] is None else r["age_h"]
        out.append("LEG %s age_h=%s ts=%s status=%s stale=%d src=%s"
                   % (r["name"], age, r["ts"], r["status"],
                      r["stale"], r["src"]))
    return out


def live(results_dir, now_str):
    if now_str is not None:
        try:
            now = datetime.strptime(now_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("unparseable now_str: %r" % now_str, file=sys.stderr)
            return 2
    else:
        now = datetime.now()
    if not os.path.isdir(results_dir):
        print("results dir not found: %s" % results_dir, file=sys.stderr)
        return 2
    observations = []
    for name, fname, ts_field in LEGS:
        raw = None
        path = os.path.join(results_dir, fname)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8-sig") as fh:
                    raw = fh.read()
            except OSError:
                raw = None
        observations.append((name, fname, raw, ts_field))
    result = digest(observations, now)
    for line in render(result, now):
        print(line)
    return 0 if (result["missing"] == 0 and result["bad"] == 0) else 1


def _row(result, name):
    for r in result["rows"]:
        if r["name"] == name:
            return r
    raise AssertionError("row not found: %s" % name)


def _selftest():
    """Offline assertions on digest/render (prompt rule 7): no repo file
    reads, no file writes."""
    ok = 0
    now = datetime(2026, 9, 26, 1, 0, 0)

    def obs(name, ts, field="updated", src=None):
        return (name, src or (name + ".json"),
                json.dumps({field: ts}), field)

    # sample 1: five ok legs, ages 49h/25h/1h/0h/0h
    sample1 = [
        ("zeta", "zeta.json", json.dumps({"updated": "2026-09-24 00:00:00"}), "updated"),      # -49h
        ("yankee", "yankee.json", json.dumps({"updated": "2026-09-25 00:00:00"}), "updated"),   # -25h
        ("xray", "xray.json", json.dumps({"updated": "2026-09-25 23:30:00"}), "updated"),        # -90min
        ("wiskey", "wiskey.json", json.dumps({"updated": "2026-09-26 00:01:00"}), "updated"),   # -59min
        ("alpha", "alpha.json", json.dumps({"updated": "2026-09-26 00:30:00"}), "updated"),     # -30min
    ]
    r1 = digest(sample1, now)
    assert r1["ok"] == 5 and r1["missing"] == 0 and r1["bad"] == 0, r1
    assert r1["stale"] == 2, r1["stale"]
    ok += 2
    order1 = [r["name"] for r in r1["rows"]]
    assert order1 == ["zeta", "yankee", "xray", "alpha", "wiskey"], order1
    ok += 1
    assert _row(r1, "wiskey")["age_h"] == 0, _row(r1, "wiskey")  # 59min floor
    assert _row(r1, "xray")["age_h"] == 1, _row(r1, "xray")      # 90min -> 1
    assert _row(r1, "zeta")["stale"] == 1 and _row(r1, "yankee")["stale"] == 1
    assert _row(r1, "alpha")["stale"] == 0 and _row(r1, "wiskey")["stale"] == 0
    ok += 4
    # render contract for the header of sample 1
    lines1 = render(r1, now)
    assert lines1[0] == "FRESHNESS legs=5 ok=5 missing=0 bad=0 stale=2 now=2026-09-26 01:00:00", lines1[0]
    ok += 1

    # sample 2: mixed 3 legs (ok + bad_ts-field-absent + missing)
    sample2 = [
        ("m_ok", "m_ok.json", json.dumps({"updated": "2026-09-26 00:00:00"}), "updated"),
        ("m_bad", "m_bad.json", json.dumps({"other": 1}), "updated"),
        ("m_miss", "m_miss.json", None, "updated"),
    ]
    r2 = digest(sample2, now)
    assert r2["ok"] == 1 and r2["bad"] == 1 and r2["missing"] == 1, r2
    ok += 1
    order2 = [r["name"] for r in r2["rows"]]
    assert order2 == ["m_ok", "m_bad", "m_miss"], order2
    ok += 1
    assert _row(r2, "m_bad")["ts"] == "absent", _row(r2, "m_bad")
    assert _row(r2, "m_miss")["ts"] == "absent", _row(r2, "m_miss")
    assert _row(r2, "m_miss")["stale"] == 0 and _row(r2, "m_bad")["stale"] == 0
    ok += 3

    # boundary/violation family
    # (1) raw None -> missing
    r = digest([("b1", "b1.json", None, "updated")], now)
    assert _row(r, "b1")["status"] == "missing"
    ok += 1
    # (2) top-level non-dict JSON -> missing
    r = digest([("b2", "b2.json", "[1, 2]", "updated")], now)
    assert _row(r, "b2")["status"] == "missing"
    ok += 1
    # (3) JSON parse failure -> missing
    r = digest([("b3", "b3.json", "{not json", "updated")], now)
    assert _row(r, "b3")["status"] == "missing"
    ok += 1
    # (4) ts field absent -> bad_ts, render absent
    r = digest([("b4", "b4.json", json.dumps({"x": 1}), "updated")], now)
    assert _row(r, "b4")["status"] == "bad_ts" and _row(r, "b4")["ts"] == "absent"
    ok += 1
    # (5) ts non-str (int) -> bad_ts, render nonstr
    r = digest([("b5", "b5.json", json.dumps({"updated": 5}), "updated")], now)
    assert _row(r, "b5")["status"] == "bad_ts" and _row(r, "b5")["ts"] == "nonstr"
    ok += 1
    # (6) date-only string -> bad_ts
    r = digest([("b6", "b6.json", json.dumps({"updated": "2026-09-26"}), "updated")], now)
    assert _row(r, "b6")["status"] == "bad_ts"
    ok += 1
    # (7) space vs T separator -> identical age_h
    r = digest([("b7a", "a.json", json.dumps({"updated": "2026-09-25 10:00:00"}), "updated"),
                ("b7t", "t.json", json.dumps({"updated": "2026-09-25T10:00:00"}), "updated")], now)
    assert _row(r, "b7a")["age_h"] == _row(r, "b7t")["age_h"]
    ok += 1
    # (8) fractional seconds truncated -> identical age_h
    r = digest([("b8f", "f.json", json.dumps({"updated": "2026-09-25 10:00:00.500"}), "updated"),
                ("b8p", "p.json", json.dumps({"updated": "2026-09-25 10:00:00"}), "updated")], now)
    assert _row(r, "b8f")["age_h"] == _row(r, "b8p")["age_h"]
    ok += 1
    # (9) future ts (now+2h) -> age_h=-2, stale=0, status ok
    r = digest([("b9", "b9.json", json.dumps({"updated": "2026-09-26 03:00:00"}), "updated")], now)
    row = _row(r, "b9")
    assert row["status"] == "ok" and row["age_h"] == -2 and row["stale"] == 0, row
    ok += 1
    # (10) over-60-char bad_ts string -> truncated to 60
    r = digest([("b10", "b10.json", json.dumps({"updated": "x" * 70}), "updated")], now)
    assert _row(r, "b10")["ts"] == "x" * 60, len(_row(r, "b10")["ts"])
    ok += 1

    print("selftest: %d assertions ALL PASS" % ok)
    return 0


def main(argv):
    if len(argv) == 1:
        print(USAGE)
        return 2
    if argv[1] == "selftest":
        return _selftest()
    results_dir = argv[1] if len(argv) >= 2 else "results"
    now_str = argv[2] if len(argv) >= 3 else None
    return live(results_dir, now_str)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
