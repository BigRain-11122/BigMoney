#!/usr/bin/env python3
"""opt_cells_recon.py -- options forward-collector checkpoint reconciler.

T-70 local-coding pilot task 08. Reconciles the per-contract checkpoint face
(options_update_cells.jsonl) against the panel face embedded in
options_update_status.json: line/code-set counts vs panel.attempted/universe,
pass-date agreement, appended-sum agreement, and status hygiene. Stdlib only,
zero network, zero file writes.
"""

import json
import os
import sys
from collections import Counter

CELLS_FILE = "options_update_cells.jsonl"
STATUS_FILE = "options_update_status.json"

USAGE = ("usage: opt_cells_recon.py [selftest | [results_dir]] "
         "(default results_dir=results)")


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _row_ok(obj):
    """Prompt rule 3 row contract: dict + code/pass/kind/status str
    (code non-empty) + appended-if-present int."""
    if not isinstance(obj, dict):
        return False
    code = obj.get("code")
    if not isinstance(code, str) or not code:
        return False
    if not isinstance(obj.get("pass"), str):
        return False
    if not isinstance(obj.get("kind"), str):
        return False
    if not isinstance(obj.get("status"), str):
        return False
    if "appended" in obj and not _is_int(obj["appended"]):
        return False
    return True


def recon(cells_lines, panel_text):
    """Core (prompt rule 7 selftest target). cells_lines = list of raw line
    strings; panel_text = full status-JSON text. Returns dict with all
    counts, derived stats, six check flags, verdict and fail count."""
    blank = malformed = 0
    valid_rows = []
    for line in cells_lines:
        if not isinstance(line, str):
            malformed += 1
            continue
        if not line.strip():
            blank += 1
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            malformed += 1
            continue
        if not _row_ok(obj):
            malformed += 1
            continue
        valid_rows.append(obj)

    codes = Counter(r["code"] for r in valid_rows)
    codes_unique = len(codes)
    dup_codes = sum(1 for c in codes.values() if c > 1)
    kind_live = sum(1 for r in valid_rows if r["kind"] == "live")
    kind_extra = sum(1 for r in valid_rows if r["kind"] == "extra")
    kind_other = len(valid_rows) - kind_live - kind_extra
    status_ok = sum(1 for r in valid_rows if r["status"] == "ok")
    status_fail = len(valid_rows) - status_ok
    appended_sum = sum(r.get("appended", 0) for r in valid_rows)
    pass_set = sorted({r["pass"] for r in valid_rows})
    if len(pass_set) == 1:
        pass_render = pass_set[0]
    elif len(pass_set) > 1:
        pass_render = "MULTI"
    else:
        pass_render = "-"

    status_obj = json.loads(panel_text)
    panel = status_obj.get("panel") if isinstance(status_obj, dict) else None
    if not isinstance(panel, dict):
        panel = {}

    def p_int(key):
        v = panel.get(key)
        return v if _is_int(v) else None

    attempted = p_int("attempted")
    universe = p_int("universe")
    appended_panel = p_int("appended")
    lpd = panel.get("last_pass_date")
    lpd_render = lpd if isinstance(lpd, str) else "-"

    def list_len(key):
        v = panel.get(key)
        return len(v) if isinstance(v, list) else -1

    fails_len = list_len("fails")
    mism_len = list_len("mismatches")

    checks = {
        "c0": malformed == 0,
        "c1": attempted is not None and len(valid_rows) == attempted,
        "c2": universe is not None and codes_unique == universe,
        "c3": (len(pass_set) == 1 and isinstance(lpd, str)
               and pass_render == lpd),
        "c4": (appended_panel is not None
               and appended_sum == appended_panel),
        "c5": (status_fail == 0 and fails_len == 0 and mism_len == 0),
    }
    fails_n = sum(1 for ok in checks.values() if not ok)

    return {
        "lines": blank + malformed + len(valid_rows),
        "blank": blank, "malformed": malformed, "valid": len(valid_rows),
        "codes_unique": codes_unique, "dup_codes": dup_codes,
        "kind_live": kind_live, "kind_extra": kind_extra,
        "kind_other": kind_other, "status_ok": status_ok,
        "status_fail": status_fail, "appended_sum": appended_sum,
        "pass_render": pass_render, "attempted": attempted,
        "universe": universe, "appended_panel": appended_panel,
        "lpd_render": lpd_render, "fails_len": fails_len,
        "mism_len": mism_len, "checks": checks, "fails_n": fails_n,
        "verdict": "MATCH" if fails_n == 0 else "MISMATCH",
    }


def render(result):
    """Prompt rule 6: header + check lines + verdict, fixed order."""
    c = result["checks"]
    ok = lambda b: 1 if b else 0
    out = ["RECON lines=%d blank=%d malformed=%d valid=%d codes_unique=%d "
           "dup_codes=%d kind_live=%d kind_extra=%d kind_other=%d "
           "status_ok=%d status_fail=%d appended_sum=%d pass=%s"
           % (result["lines"], result["blank"], result["malformed"],
              result["valid"], result["codes_unique"], result["dup_codes"],
              result["kind_live"], result["kind_extra"], result["kind_other"],
              result["status_ok"], result["status_fail"],
              result["appended_sum"], result["pass_render"])]
    out.append("CHECK c0_malformed malformed=%d ok=%d"
               % (result["malformed"], ok(c["c0"])))
    att = "-" if result["attempted"] is None else result["attempted"]
    out.append("CHECK c1_count valid=%d attempted=%s ok=%d"
               % (result["valid"], att, ok(c["c1"])))
    uni = "-" if result["universe"] is None else result["universe"]
    out.append("CHECK c2_universe codes_unique=%d universe=%s ok=%d"
               % (result["codes_unique"], uni, ok(c["c2"])))
    out.append("CHECK c3_pass cells_pass=%s panel_pass=%s ok=%d"
               % (result["pass_render"], result["lpd_render"], ok(c["c3"])))
    ap = "-" if result["appended_panel"] is None else result["appended_panel"]
    out.append("CHECK c4_appended cells=%d panel=%s ok=%d"
               % (result["appended_sum"], ap, ok(c["c4"])))
    out.append("CHECK c5_status cells_fail=%d panel_fails=%d "
               "panel_mismatches=%d ok=%d"
               % (result["status_fail"], result["fails_len"],
                  result["mism_len"], ok(c["c5"])))
    if result["verdict"] == "MATCH":
        out.append("VERDICT MATCH")
    else:
        out.append("VERDICT MISMATCH fails=%d" % result["fails_n"])
    return out


def live(results_dir):
    if not os.path.isdir(results_dir):
        print("results dir not found: %s" % results_dir, file=sys.stderr)
        return 2
    cells_path = os.path.join(results_dir, CELLS_FILE)
    status_path = os.path.join(results_dir, STATUS_FILE)
    try:
        with open(cells_path, encoding="utf-8-sig") as fh:
            cells_lines = fh.read().splitlines()
    except OSError as e:
        print("cells face unreadable: %s" % e, file=sys.stderr)
        return 2
    try:
        with open(status_path, encoding="utf-8-sig") as fh:
            panel_text = fh.read()
    except OSError as e:
        print("status face unreadable: %s" % e, file=sys.stderr)
        return 2
    try:
        status_obj = json.loads(panel_text)
    except ValueError as e:
        print("status face unparseable: %s" % e, file=sys.stderr)
        return 2
    if not isinstance(status_obj, dict):
        print("status face top level not a dict", file=sys.stderr)
        return 2
    result = recon(cells_lines, panel_text)
    for line in render(result):
        print(line)
    return 0 if result["verdict"] == "MATCH" else 1


def _panel(universe, attempted, appended, lpd, fails=None, mism=None):
    body = {"universe": universe, "attempted": attempted,
            "appended": appended, "last_pass_date": lpd,
            "fails": fails if fails is not None else [],
            "mismatches": mism if mism is not None else []}
    return json.dumps({"panel": body})


def _row(code, kind="live", status="ok", appended=0, p="2026-09-24"):
    return json.dumps({"pass": p, "code": code, "kind": kind,
                       "status": status, "appended": appended})


def _selftest():
    """Offline assertions on recon/render (prompt rule 7): no repo file
    reads, no file writes."""
    ok = 0

    # sample 1: aligned face -- 5 ok rows (2 live + 3 extra), pass single,
    # appended sum 3, panel fully agreeing
    s1_lines = [
        _row("10011421", "live", "ok", 0),
        _row("10011422", "live", "ok", 0),
        _row("10011423", "extra", "ok", 1),
        _row("10011424", "extra", "ok", 2),
        _row("10011425", "extra", "ok", 0),
    ]
    r1 = recon(s1_lines, _panel(5, 5, 3, "2026-09-24"))
    assert (r1["lines"] == 5 and r1["blank"] == 0 and r1["malformed"] == 0
            and r1["valid"] == 5), r1
    assert r1["codes_unique"] == 5 and r1["dup_codes"] == 0, r1
    assert (r1["kind_live"] == 2 and r1["kind_extra"] == 3
            and r1["kind_other"] == 0), r1
    assert r1["status_ok"] == 5 and r1["status_fail"] == 0, r1
    assert r1["appended_sum"] == 3 and r1["pass_render"] == "2026-09-24", r1
    ok += 5
    assert all(r1["checks"].values()), r1["checks"]
    assert r1["verdict"] == "MATCH" and r1["fails_n"] == 0, r1
    ok += 2
    lines1 = render(r1)
    assert lines1[0] == (
        "RECON lines=5 blank=0 malformed=0 valid=5 codes_unique=5 "
        "dup_codes=0 kind_live=2 kind_extra=3 kind_other=0 status_ok=5 "
        "status_fail=0 appended_sum=3 pass=2026-09-24"), lines1[0]
    assert lines1[1] == "CHECK c0_malformed malformed=0 ok=1", lines1[1]
    assert lines1[2] == "CHECK c1_count valid=5 attempted=5 ok=1", lines1[2]
    assert lines1[3] == "CHECK c2_universe codes_unique=5 universe=5 ok=1", lines1[3]
    assert lines1[4] == "CHECK c3_pass cells_pass=2026-09-24 panel_pass=2026-09-24 ok=1", lines1[4]
    assert lines1[5] == "CHECK c4_appended cells=3 panel=3 ok=1", lines1[5]
    assert lines1[6] == "CHECK c5_status cells_fail=0 panel_fails=0 panel_mismatches=0 ok=1", lines1[6]
    assert lines1[7] == "VERDICT MATCH", lines1[7]
    ok += 8

    # sample 2: count gap -- 4 valid vs attempted=5, universe=4
    s2_lines = [_row("a"), _row("b"), _row("c"), _row("d")]
    r2 = recon(s2_lines, _panel(4, 5, 0, "2026-09-24"))
    assert r2["checks"]["c1"] is False and r2["checks"]["c2"] is True, r2
    assert r2["verdict"] == "MISMATCH" and r2["fails_n"] == 1, r2
    ok += 3

    # sample 3: duplicate code -- a,b,c,a (4 valid, unique=3, dup=1)
    s3_lines = [_row("a"), _row("b"), _row("c"), _row("a")]
    r3 = recon(s3_lines, _panel(4, 4, 0, "2026-09-24"))
    assert r3["codes_unique"] == 3 and r3["dup_codes"] == 1, r3
    assert r3["checks"]["c1"] is True and r3["checks"]["c2"] is False, r3
    assert r3["verdict"] == "MISMATCH" and r3["fails_n"] == 1, r3
    ok += 4

    # sample 4: pass dual values -> MULTI render, c3 fails alone
    s4_lines = [_row("a", p="2026-09-23"), _row("b", p="2026-09-24")]
    r4 = recon(s4_lines, _panel(2, 2, 0, "2026-09-23"))
    assert r4["pass_render"] == "MULTI", r4
    assert r4["checks"]["c3"] is False and r4["fails_n"] == 1, r4
    assert r4["verdict"] == "MISMATCH", r4
    ok += 3

    # sample 5a: appended gap -- cells sum 3 vs panel 2 -> c4 alone
    s5a_lines = [_row("a", appended=1), _row("b", appended=2)]
    r5a = recon(s5a_lines, _panel(2, 2, 2, "2026-09-24"))
    assert r5a["checks"]["c4"] is False and r5a["fails_n"] == 1, r5a
    ok += 2
    # sample 5b: one non-ok valid row -> status_fail=1 -> c5 alone
    s5b_lines = [_row("a", status="fail"), _row("b")]
    r5b = recon(s5b_lines, _panel(2, 2, 0, "2026-09-24"))
    assert r5b["status_fail"] == 1, r5b
    assert r5b["checks"]["c5"] is False and r5b["fails_n"] == 1, r5b
    ok += 3
    # sample 5c: panel.fails non-empty -> c5 alone (same check counted once)
    r5c = recon([_row("a")], _panel(1, 1, 0, "2026-09-24",
                                    fails=["10011425"]))
    assert r5c["checks"]["c5"] is False and r5c["fails_n"] == 1, r5c
    assert r5c["fails_len"] == 1, r5c
    ok += 3

    # boundary/violation family
    # (1) blank lines ("  " and "") -> blank counter, not malformed
    rb = recon(["", "  ", _row("a")], _panel(1, 1, 0, "2026-09-24"))
    assert rb["blank"] == 2 and rb["malformed"] == 0 and rb["valid"] == 1, rb
    assert rb["lines"] == rb["blank"] + rb["malformed"] + rb["valid"], rb
    ok += 2
    # (2) unparseable json -> malformed
    r = recon(["{not json"], _panel(0, 0, 0, "2026-09-24"))
    assert r["malformed"] == 1 and r["valid"] == 0, r
    ok += 1
    # (3) non-dict json -> malformed
    r = recon(["[1,2]"], _panel(0, 0, 0, "2026-09-24"))
    assert r["malformed"] == 1, r
    ok += 1
    # (4) dict missing code key -> malformed
    r = recon([json.dumps({"pass": "2026-09-24", "kind": "live",
                           "status": "ok"})], _panel(0, 0, 0, "2026-09-24"))
    assert r["malformed"] == 1, r
    ok += 1
    # (5) non-str code (int 5) -> malformed
    bad5 = json.dumps({"pass": "2026-09-24", "code": 5, "kind": "live",
                       "status": "ok"})
    r = recon([bad5], _panel(0, 0, 0, "2026-09-24"))
    assert r["malformed"] == 1, r
    ok += 1
    # (6) appended as str -> malformed
    bad6 = json.dumps({"pass": "2026-09-24", "code": "x", "kind": "live",
                       "status": "ok", "appended": "1"})
    r = recon([bad6], _panel(0, 0, 0, "2026-09-24"))
    assert r["malformed"] == 1, r
    ok += 1
    # (7) panel.universe absent -> c2 ok=0, render universe=-
    p7 = json.dumps({"panel": {"attempted": 1, "appended": 0,
                               "last_pass_date": "2026-09-24",
                               "fails": [], "mismatches": []}})
    r = recon([_row("a")], p7)
    assert r["checks"]["c2"] is False and r["universe"] is None, r
    lines7 = render(r)
    assert lines7[3] == "CHECK c2_universe codes_unique=1 universe=- ok=0", lines7[3]
    assert r["fails_n"] == 1, r
    ok += 4
    # (8) panel.last_pass_date absent -> c3 ok=0, render panel_pass=-
    p8 = json.dumps({"panel": {"universe": 1, "attempted": 1, "appended": 0,
                                "fails": [], "mismatches": []}})
    r = recon([_row("a")], p8)
    assert r["checks"]["c3"] is False, r
    lines8 = render(r)
    assert lines8[4] == "CHECK c3_pass cells_pass=2026-09-24 panel_pass=- ok=0", lines8[4]
    assert r["fails_n"] == 1, r
    ok += 3
    # (9) all lines malformed (0 valid) -> pass "-", c3 fail, c1 fail
    r = recon(["{bad1", "{bad2"], _panel(2, 2, 0, "2026-09-24"))
    assert r["pass_render"] == "-" and r["valid"] == 0, r
    assert r["checks"]["c3"] is False and r["checks"]["c1"] is False, r
    lines9 = render(r)
    assert lines9[4] == "CHECK c3_pass cells_pass=- panel_pass=2026-09-24 ok=0", lines9[4]
    ok += 4
    # (10) panel.fails absent -> panel_fails=-1, c5 fail
    p10 = json.dumps({"panel": {"universe": 1, "attempted": 1, "appended": 0,
                                "last_pass_date": "2026-09-24",
                                "mismatches": []}})
    r = recon([_row("a")], p10)
    assert r["fails_len"] == -1 and r["checks"]["c5"] is False, r
    lines10 = render(r)
    assert lines10[6] == "CHECK c5_status cells_fail=0 panel_fails=-1 panel_mismatches=0 ok=0", lines10[6]
    ok += 3

    print("selftest: %d assertions ALL PASS" % ok)
    return 0


def main(argv):
    if len(argv) == 1:
        print(USAGE)
        return 2
    if argv[1] == "selftest":
        return _selftest()
    return live(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
