"""T-2026-09-26-72 s2 acceptance derive -- INDEPENDENT panel re-verification.

Prereg (FROZEN at collector-ticket claim 5a14ff38): research/shortline/
SINA_MF_PREREG.md section-4 machine-verifiable acceptance lines.

O-2115 post-review law: the worker does not certify its own work. This script
re-derives every criterion from the panel BYTES (independent csv parse + own
collapse math); collector runtime accounting (progress / status mirror) is
read only as cross-check disclosure, never as evidence of pass.

Two measurement faces of the self-collapse law (honest disclosure):
- SOURCE face (collector booking gate, frozen): |netamount - sum(r*_net)|
  <= 1e-3 absolute, checked on full-precision source floats BEFORE booking.
- WRITTEN face (this acceptance): files are %.10g projections -- at 1e10+
  magnitudes the write itself injects up to ~5 yuan of rounding drift, and
  tier cancellation can amplify the RELATIVE drift (empirical partial-panel
  worst: 0.08 abs on a -4.9e5 net from +-1.4e8 tiers = 5.8e-10 x scale).
  Bound: each of the 5 values drifts <= 0.5 ulp of its 10th significant
  digit <= 5e-10 x |v|, so total <= 2.5e-9 x scale with
  scale = max(|net|, |tiers|, 1). WRITTEN_LAW_TOL = 1e-8 (4x headroom);
  a real structural violation (order-1 relative) stays far above it.

Latent re-pull defect (disclosed, NOT patched mid-pull -- collector frozen
while first pull is in flight): overlap verify compares fresh source floats
against %.10g-written bytes with PRIMARY_TOL=1.0 yuan; for |netamount| >= 1e10
write rounding alone can exceed 1.0 -> false mismatch -> symbol frozen on the
first monthly re-pull (~20td staleness gate). Prereg amendment required BEFORE
s3 wiring / first re-pull. Evidence: worst_written_drift in this report.

Exit codes: 0 = derive complete + PASS; 1 = derive complete + FAIL (frozen
line not met -- honest report, no line-bending); 2 = machinery (pull in
flight / universe unavailable / unreadable artifacts).

Lane guard (R31 family): acceptance artifact owned by bm-a; other machines
stdout-only honest no-op, zero shared-file writes.
"""
from __future__ import annotations

import csv as _csv
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import update_sina_mf as mf          # frozen constants + pure spec-face helpers

ROOT = mf.ROOT
ACCEPT_OUT = os.path.join(ROOT, "results", "sina_mf_accept.json")

MIN_FRESH_COVERED = 5000     # prereg section-4.1 (frozen)
WRITTEN_LAW_TOL = 1e-8       # see module header: %.10g bound 2.5e-9 x scale
RUNAWAY_MULT = 2.0           # budget runaway = >= one extra full re-pull
NUM_PROBES_ACCOUNTED = 2     # R220 num-ceiling probes, disclosed separately
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EXPECTED_HEADER = mf.DATE_KEY + "," + ",".join(mf.FLOW_COLS)


class Machinery(Exception):
    """Derive cannot proceed honestly (exit 2 face)."""


# ------------------------------------------------------------- panel bytes


def _read_panel(per_dir, expected):
    """Independent parse of every per-symbol csv. Never imports the
    collector's row path (O-2115): own csv loop, own law math."""
    files = sorted(
        os.path.basename(p)[:-4] for p in
        [os.path.join(per_dir, f) for f in os.listdir(per_dir)]
        if os.path.basename(p).endswith(".csv")) if os.path.isdir(per_dir) else []
    agg = {
        "n_files": len(files),
        "rows_total": 0,
        "law_violations": 0,
        "unverifiable_rows": 0,
        "dup_date_files": 0,
        "non_monotonic_files": 0,
        "schema_violation_files": 0,
        "worst_written_drift": 0.0,
        "violations_head": [],
        "defect_files_head": [],
    }
    max_date_by_code, empty_files = {}, []
    for code in files:
        path = os.path.join(per_dir, code + ".csv")
        with io.open(path, "r", encoding="utf-8", newline="") as f:
            first = f.readline()
            if first.rstrip("\r\n") != EXPECTED_HEADER:
                agg["schema_violation_files"] += 1
                agg["defect_files_head"].append(f"{code}:header_drift")
                continue                      # untrusted shape, skip rows
            # header already consumed + proven byte-exact: fieldnames MUST be
            # explicit (DictReader would otherwise eat the first data row as
            # the header -- 0-row false read, caught by selftest mini-repro)
            rd = _csv.DictReader(f, fieldnames=[mf.DATE_KEY] + mf.FLOW_COLS)
            prev, n_rows, dmax, bad = None, 0, None, False
            for row in rd:
                d = str(row.get(mf.DATE_KEY, ""))
                if not DATE_RE.match(d):
                    bad = True
                    agg["defect_files_head"].append(f"{code}:bad_date:{d[:10]}")
                    continue
                if prev is not None:
                    if d == prev:
                        bad = True
                        agg["defect_files_head"].append(f"{code}:dup_date:{d}")
                    elif d < prev:
                        bad = True
                        agg["defect_files_head"].append(f"{code}:non_monotonic:{d}")
                prev = d
                n_rows += 1
                dmax = d if dmax is None or d > dmax else dmax
                vals = {}
                for col in mf.FLOW_COLS:
                    v = (row.get(col) or "").strip()
                    try:
                        vals[col] = float(v) if v != "" else None
                    except ValueError:
                        vals[col] = None
                net = vals.get(mf.PRIMARY)
                tiers = [vals.get(k) for k in mf.TIER_NETS]
                if net is None or any(t is None for t in tiers):
                    agg["unverifiable_rows"] += 1
                    continue
                diff = abs(net - sum(tiers))
                scale = max(abs(net), max(abs(t) for t in tiers), 1.0)
                drift = diff / scale
                if drift > agg["worst_written_drift"]:
                    agg["worst_written_drift"] = drift
                if drift > WRITTEN_LAW_TOL:
                    agg["law_violations"] += 1
                    if len(agg["violations_head"]) < 5:
                        agg["violations_head"].append(
                            f"{code}@{d}:diff={net - sum(tiers):.6g}:scale={scale:.6g}")
            agg["rows_total"] += n_rows
            if bad:
                pass                       # row defects already tagged above
            max_date_by_code[code] = dmax
            if n_rows == 0:
                empty_files.append(code)
    # file-level defect counts (one file counts once per defect kind)
    kinds = {}
    for tag in agg["defect_files_head"]:
        kind = tag.split(":", 1)[-1].split(":", 1)[0]
        code = tag.split(":", 1)[0]
        kinds.setdefault(code, set()).add(kind)
    for code, ks in kinds.items():
        if "dup_date" in ks:
            agg["dup_date_files"] += 1
        if "non_monotonic" in ks:
            agg["non_monotonic_files"] += 1
    agg["defect_files_head"] = agg["defect_files_head"][:10]
    return agg, max_date_by_code, empty_files, files


# ----------------------------------------------------------------- derive


def _read_json(path):
    if not os.path.exists(path):
        return None
    with io.open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def derive(per_dir, progress_path, status_path, expected=None, universe=None,
           now=None):
    """All counts + line evaluations. `expected`/`universe` injectable for
    hermetic fixtures; production path derives both from frozen faces."""
    if expected is None:
        expected = mf.expected_latest_bar_date(now or dt.datetime.now())
    if universe is None:
        codes, skipped, buckets = mf.universe_codes()
    else:
        codes, skipped, buckets = universe
    if not codes:
        raise Machinery(f"universe unavailable ({len(codes)} codes)")
    panel, max_date_by_code, empty_files, files = _read_panel(per_dir, expected)
    prog = _read_json(progress_path) or {}
    done = set(prog.get("done", []))
    attempts = {k: int(v) for k, v in (prog.get("attempts") or {}).items()}
    status = _read_json(status_path) or {}
    last_refresh = (status.get("last_refresh") or {})

    universe_set = set(codes)
    files_set = set(files)
    fresh_covered = sum(1 for c in files_set
                        if max_date_by_code.get(c) == expected)
    stale_files = sorted(c for c in files_set
                         if max_date_by_code.get(c) is not None
                         and max_date_by_code[c] < expected)
    quarantined = sorted(c for c, n in attempts.items()
                         if n >= mf.QUARANTINE_AT)
    requests_lb = len(done) + sum(attempts.values())
    panel_cutoff = max((d for d in max_date_by_code.values()
                        if d is not None), default=None)
    mismatches = int(last_refresh.get("n_mismatches") or 0)

    counts = {
        "universe_n": len(codes),
        "universe_skipped": len(skipped),
        "universe_skipped_buckets": dict(buckets),
        "files_n": panel["n_files"],
        "rows_total": panel["rows_total"],
        "fresh_covered": fresh_covered,
        "stale_covered_suspended_face": len(stale_files),
        "stale_files_head": stale_files[:10],
        "empty_history_files": len(empty_files),
        "empty_files_head": empty_files[:10],
        "done_n": len(done),
        "quarantined_n": len(quarantined),
        "quarantined_head": quarantined[:10],
        "attempts_open": {k: v for k, v in sorted(attempts.items())[:10]},
        "files_not_in_universe": sorted(files_set - universe_set)[:10],
        "file_without_done": sorted(files_set - done)[:10],
        "done_without_file": sorted(done - files_set)[:10],
        "panel_cutoff": panel_cutoff,
        "expected_bar_date": str(expected),
    }
    law = {
        "law_violations_written_face": panel["law_violations"],
        "unverifiable_rows": panel["unverifiable_rows"],
        "worst_written_drift": panel["worst_written_drift"],
        "written_law_tol": WRITTEN_LAW_TOL,
        "violations_head": panel["violations_head"],
    }
    defects = {
        "dup_date_files": panel["dup_date_files"],
        "non_monotonic_files": panel["non_monotonic_files"],
        "schema_violation_files": panel["schema_violation_files"],
        "defect_files_head": panel["defect_files_head"],
    }
    request_account = {
        "pull_requests_lb": requests_lb,
        "num_probes_accounted_separately": NUM_PROBES_ACCOUNTED,
        "last_run_failures": int(last_refresh.get("failures") or 0),
        "last_run_appended": int(last_refresh.get("appended") or 0),
        "last_run_law_rejected_source_face":
            int(last_refresh.get("law_rejected_rows") or 0),
        "universe_n": len(codes),
        "runaway_line": RUNAWAY_MULT * len(codes),
    }
    lines = {
        "coverage(fresh>=5000)": fresh_covered >= MIN_FRESH_COVERED,
        "law(written_face_zero_violations)":
            panel["law_violations"] == 0 and panel["unverifiable_rows"] == 0,
        "integrity(no_dup/no_mono/no_schema/files==done/no_mismatch/"
        "cutoff_covers_expected)":
            (panel["dup_date_files"] == 0
             and panel["non_monotonic_files"] == 0
             and panel["schema_violation_files"] == 0
             and not (files_set - done) and not (done - files_set)
             and mismatches == 0
             and panel_cutoff is not None and str(panel_cutoff) >= str(expected)),
        "budget(no_runaway)": requests_lb <= RUNAWAY_MULT * len(codes),
    }
    return {
        "expected_bar_date": str(expected),
        "counts": counts,
        "law": law,
        "defects": defects,
        "request_account": request_account,
        "lines": lines,
    }


# ------------------------------------------------------------------- run


def _lane_ok():
    return mf._lane_owner_id() == mf.LANE_OWNER


def _in_flight_guard():
    if mf._lock_alive():
        raise Machinery("pull in progress (lock alive) -- accept deferred")


def _collector_selftest_ok():
    r = subprocess.run(
        [sys.executable, os.path.abspath(mf.__file__), "selftest"],
        capture_output=True, timeout=600)
    return r.returncode == 0


def run():
    if not _lane_ok():
        print(f"no-op: sina_mf lane owned by {mf.LANE_OWNER}; acceptance "
              f"artifact is lane property (R31 family), not this machine")
        return 0
    try:
        _in_flight_guard()
        res = derive(mf.PER_DIR, mf.PROGRESS, mf.STATUS)
    except Machinery as e:
        print(f"machinery: {e}")
        return 2
    ok4 = _collector_selftest_ok()          # prereg section-4.4, offline
    res["lines"]["selftest(collector_offline_green)"] = bool(ok4)
    verdict = all(res["lines"].values())
    res.update({
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "machine": mf._lane_owner_id(),
        "claim": "T-2026-09-26-72-bm-a-sina-mf-collector",
        "prereg_ref": "research/shortline/SINA_MF_PREREG.md section-4",
        "evidence_cutoff": res["counts"]["panel_cutoff"],
        "verdict": "PASS" if verdict else "FAIL",
        "latent_repull_defect_note": (
            "%.10g write rounding can exceed PRIMARY_TOL=1.0 on |netamount|"
            ">=1e10 rows at overlap re-verify -> prereg amendment required "
            "before s3 wiring / first monthly re-pull (see module header)"),
    })
    with io.open(ACCEPT_OUT, "w", encoding="utf-8", newline="") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    c = res["counts"]
    print(f"accept: files={c['files_n']} rows={c['rows_total']} "
          f"fresh={c['fresh_covered']}/{c['universe_n']} "
          f"(min {MIN_FRESH_COVERED}) quarantined={c['quarantined_n']} "
          f"law_viol={res['law']['law_violations_written_face']} "
          f"worst_drift={res['law']['worst_written_drift']:.3e} "
          f"cutoff={c['panel_cutoff']} verdict={res['verdict']}")
    for k, v in res["lines"].items():
        print(f"  line {k}: {'ok' if v else 'FAIL'}")
    return 0 if verdict else 1


# --------------------------------------------------------------- selftest


def _write_panel_rows(path, rows):
    """Fixture writer = producer path (r157 mirror-real-form law: %.10g
    rounding face included)."""
    text = mf.rows_to_csv_text(rows)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def _raw_row(date, net, t0, t1, t2, t3, trade="10.0"):
    """Law-exact by construction at source precision."""
    return {mf.DATE_KEY: date, "trade": trade, "changeratio": "0.01",
            "turnover": "100.5", "netamount": net, "ratioamount": "0.1",
            "r0": t0, "r1": t1, "r2": t2, "r3": t3,
            "r0_net": t0, "r1_net": t1, "r2_net": t2, "r3_net": t3}


def _selftest():
    exp = "2026-09-24"
    # boundary law of the frozen line itself (not a scaled fixture)
    assert (5000 >= MIN_FRESH_COVERED) and not (4999 >= MIN_FRESH_COVERED)
    with tempfile.TemporaryDirectory() as td:
        per = os.path.join(td, "per")
        prog_p = os.path.join(td, "_progress.json")
        st_p = os.path.join(td, "status.json")
        uni = (["000001", "300001", "600001", "600002", "600003"],
               ["830001"], {"83": 1})

        # F1 clean mini-panel: 2 fresh + 1 stale(suspended face) + 1 empty
        _write_panel_rows(os.path.join(per, "600001.csv"),
                          [_raw_row("2026-09-23", 100.0, 60.0, 20.0, 15.0, 5.0),
                           _raw_row(exp, -50.0, -30.0, -10.0, -5.0, -5.0)])
        _write_panel_rows(os.path.join(per, "000001.csv"),
                          [_raw_row(exp, 1000500.5, 600000.0, 300000.0,
                                    100000.0, 500.5)])
        _write_panel_rows(os.path.join(per, "300001.csv"),
                          [_raw_row("2026-09-18", 7.0, 3.0, 2.0, 1.0, 1.0)])
        _write_panel_rows(os.path.join(per, "600002.csv"), [])
        with io.open(prog_p, "w", encoding="utf-8") as f:
            json.dump({"done": ["000001", "300001", "600001", "600002"],
                       "attempts": {"600003": 3, "600004": 2, "600005": 2}}, f)
        with io.open(st_p, "w", encoding="utf-8") as f:
            json.dump({"last_refresh": {"failures": 1, "appended": 9,
                                        "n_mismatches": 0,
                                        "law_rejected_rows": 0}}, f)
        res = derive(per, prog_p, st_p, expected=exp, universe=uni)
        c = res["counts"]
        assert c["files_n"] == 4 and c["fresh_covered"] == 2, c
        assert c["stale_covered_suspended_face"] == 1, c
        assert c["empty_history_files"] == 1, c
        assert c["quarantined_n"] == 1 and c["done_n"] == 4, c
        assert res["request_account"]["pull_requests_lb"] == 4 + 7   # 11 > 2x5
        assert res["law"]["law_violations_written_face"] == 0
        assert res["defects"]["dup_date_files"] == 0
        assert res["lines"]["law(written_face_zero_violations)"]
        assert res["lines"]["integrity(no_dup/no_mono/no_schema/files==done/no_mismatch/cutoff_covers_expected)"]
        assert res["lines"]["coverage(fresh>=5000)"] is False   # 2 < 5000 (scaled fixture)
        assert res["lines"]["budget(no_runaway)"] is False      # 11 > 10 runaway fires

        # F2 big-magnitude %.10g rounding face must NOT be flagged (tol design)
        big = os.path.join(per, "600100.csv")
        _write_panel_rows(big, [_raw_row(
            exp, 12345678901.23, 10000000000.0, 2000000000.0,
            345678901.23, 0.0)])
        with io.open(prog_p, "w", encoding="utf-8") as f:
            json.dump({"done": ["000001", "300001", "600001", "600002",
                                "600100"],
                       "attempts": {"600003": 3, "600004": 2,
                                    "600005": 2}}, f)
        res2 = derive(per, prog_p, st_p, expected=exp, universe=uni)
        assert res2["law"]["law_violations_written_face"] == 0, res2["law"]
        assert res2["law"]["worst_written_drift"] > 0            # drift is real
        # the written bytes really are a lossy projection (%.10g may render
        # 1e10-scale values in scientific form -- form-agnostic proof below)
        with io.open(big, encoding="utf-8") as f:
            line = f.read().splitlines()[1]
        net_cell = line.split(",")[4]
        assert float(net_cell) != 12345678901.23   # source value NOT preserved

        # F3 structural law violation (direct bytes, gate-bypass hypothesis)
        viol = os.path.join(per, "600101.csv")
        with io.open(viol, "w", encoding="utf-8", newline="") as f:
            f.write(EXPECTED_HEADER + "\n")
            f.write(f"{exp},10,0.01,100,999.0,0.1,1,1,1,1,"
                    f"1.0,1.0,1.0,1.0\n")
        res3 = derive(per, prog_p, st_p, expected=exp, universe=uni)
        assert res3["law"]["law_violations_written_face"] == 1, res3["law"]
        assert not res3["lines"]["law(written_face_zero_violations)"]

        # F4 duplicate dates (double-append hypothesis) caught at file level
        dup = os.path.join(per, "600102.csv")
        with io.open(dup, "w", encoding="utf-8", newline="") as f:
            f.write(EXPECTED_HEADER + "\n")
            f.write(f"{exp},10,0.01,100,1.0,0.1,1,1,1,1,0.25,0.25,0.25,0.25\n")
            f.write(f"{exp},10,0.01,100,1.0,0.1,1,1,1,1,0.25,0.25,0.25,0.25\n")
        res4 = derive(per, prog_p, st_p, expected=exp, universe=uni)
        assert res4["defects"]["dup_date_files"] >= 1, res4["defects"]

        # F5 non-monotonic dates caught
        mono = os.path.join(per, "600103.csv")
        with io.open(mono, "w", encoding="utf-8", newline="") as f:
            f.write(EXPECTED_HEADER + "\n")
            f.write(f"{exp},10,0.01,100,1.0,0.1,1,1,1,1,0.25,0.25,0.25,0.25\n")
            f.write("2026-09-23,10,0.01,100,1.0,0.1,1,1,1,1,"
                    "0.25,0.25,0.25,0.25\n")
        res5 = derive(per, prog_p, st_p, expected=exp, universe=uni)
        assert res5["defects"]["non_monotonic_files"] >= 1, res5["defects"]

        # F6 schema-drift header caught, file skipped
        drift = os.path.join(per, "600104.csv")
        with io.open(drift, "w", encoding="utf-8", newline="") as f:
            f.write(EXPECTED_HEADER + ",extra_col\n")
        res6 = derive(per, prog_p, st_p, expected=exp, universe=uni)
        assert res6["defects"]["schema_violation_files"] == 1, res6["defects"]
        assert res6["counts"]["files_n"] == 9                # all fixture files seen

        # F7 unverifiable row (tier empty) caught
        unv = os.path.join(per, "600105.csv")
        with io.open(unv, "w", encoding="utf-8", newline="") as f:
            f.write(EXPECTED_HEADER + "\n")
            f.write(f"{exp},10,0.01,100,10.0,0.1,1,1,1,1,1.0,2.0,3.0,\n")
        res7 = derive(per, prog_p, st_p, expected=exp, universe=uni)
        assert res7["law"]["unverifiable_rows"] == 1, res7["law"]

        # F8 machinery: universe unavailable
        try:
            derive(per, prog_p, st_p, expected=exp, universe=([], [], {}))
            raise AssertionError("universe guard did not fire")
        except Machinery:
            pass

        # F9 in-flight lock guard (live pid = this process). NEVER touch the
        # real lock path: the first pull may be running (overwriting its lock
        # would let the gate misjudge staleness and double-spawn a refresh).
        real_lock = mf.LOCK
        tmp_lock = os.path.join(td, "_refresh.lock")
        mf.LOCK = tmp_lock
        try:
            with io.open(tmp_lock, "w", encoding="utf-8") as f:
                json.dump({"pid": os.getpid(),
                           "ts": dt.datetime.now().isoformat(
                               timespec="seconds")}, f)
            try:
                _in_flight_guard()
                raise AssertionError("lock guard did not fire")
            except Machinery:
                pass
            mf._clear_lock()
            _in_flight_guard()                       # cleared -> guard passes
        finally:
            mf.LOCK = real_lock

        # F10 stale-gate freshness face used by the cutoff line
        need, why = mf.stale_gate(exp, dt.datetime(2026, 9, 26, 6, 0))
        assert not need, why                     # fresh panel -> rerun merges zero

    # F11 collector selftest subprocess (prereg section-4.4, offline)
    assert _collector_selftest_ok()
    print("sina_mf_accept selftest: all green")


def main(argv):
    if len(argv) < 2 or argv[1] not in ("run", "selftest"):
        print("usage: sina_mf_accept.py run|selftest")
        return 2
    if argv[1] == "selftest":
        _selftest()
        return 0
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
