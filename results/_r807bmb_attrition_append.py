"""r807 bm-b: append trio gate-attrition rows (prereg §8 duty, schema v1 7-key shape)."""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "results", "gate_attrition.json")

ROWS = [
    {
        "batch": "FUND-DIVLOWVOL-P1",
        "kind": "fund-p1-finalize",
        "cells_ledger_delta": 2002,
        "ledger_total_after": 792907,
        "gates": {"verdict": "insufficient-sample", "g_seg_chop": 14,
                  "g1_line_ok": False, "g1_ci_lower_positive": True,
                  "x2_survival": True, "m1_t": 3.9894, "m1_pass": True,
                  "dsr": 0.6751, "pbo": 0.0,
                  "note_gates": "G-SEG precedence; skill_line not beaten "
                                "(null mu 0.7178); verdict single-read r638"},
        "note": "finalize 2026-10-08 23:30 bm-b network-blocked stale-tree "
                "prev=790905 (freeze-era head); r807 additive fork re-anchor "
                "FUND-TRIO-REANCHOR-R807 counted trio 6008 once onto live "
                "head 825328->831336; branch total 792907 superseded "
                "never re-add; attrition row retro-filled r807 absorb "
                "(r806 session beheaded pre-S7, r873 retro-fill precedent)",
    },
    {
        "batch": "FUND-QUALITY-P1",
        "kind": "fund-p1-finalize",
        "cells_ledger_delta": 2002,
        "ledger_total_after": 794909,
        "gates": {"verdict": "insufficient-sample", "g_seg_chop": 14,
                  "g1_line_ok": False, "g1_ci_lower_positive": False,
                  "x2_survival": True, "m1_t": -1.5600, "m1_pass": False,
                  "dsr": 0.0, "pbo": 1.0,
                  "note_gates": "headline x1 NAV negative-crossing pathology "
                                "disclosed (max_dd -1.1454; rolling 3/5/10y "
                                "figures are compounding artifacts, not "
                                "readable); family revisit requires pathology "
                                "fix first"},
        "note": "finalize 2026-10-08 23:33 same stale-tree fork chain; r807 "
                "re-anchor counted once (see FUND-DIVLOWVOL-P1 row); branch "
                "total 794909 superseded never re-add; retro-filled r807",
    },
    {
        "batch": "FUND-VALUE-P1",
        "kind": "fund-p1-finalize",
        "cells_ledger_delta": 2004,
        "ledger_total_after": 796913,
        "gates": {"verdict": "insufficient-sample", "g_seg_chop": 14,
                  "g1_line_ok": False, "g1_ci_lower_positive": True,
                  "x2_survival": True, "m1_t": 2.1288, "m1_pass": False,
                  "dsr": 0.0935, "pbo": 0.6143,
                  "note_gates": "in-band sharpe 0.3809 but M1/DSR/PBO all "
                                "red = would fail even with G-SEG coverage"},
        "note": "finalize 2026-10-08 23:35 same stale-tree fork chain tail; "
                "r807 re-anchor counted once; branch total 796913 superseded "
                "never re-add; retro-filled r807",
    },
]


def main():
    with open(PATH, encoding="utf-8") as fh:
        d = json.load(fh)
    entries = d["entries"]
    existing = {e.get("batch") for e in entries}
    ts = time.strftime("%Y-%m-%d %H:%M")
    added = 0
    for row in ROWS:
        if row["batch"] in existing:
            print("skip existing:", row["batch"])
            continue
        entries.append({"batch": row["batch"], "ts": ts, **row})
        del entries[-1]["batch"]
        entries[-1]["batch"] = row["batch"]
        added += 1
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, PATH)
    # append-only assertion: prefix intact, count grew
    with open(PATH, encoding="utf-8") as fh:
        d2 = json.load(fh)
    assert len(d2["entries"]) == len(entries)
    assert [e.get("batch") for e in d2["entries"][-added:]] == \
        [r["batch"] for r in ROWS[-added:]]
    assert all(k in d2["entries"][0] for k in ("batch", "ts"))
    print("ATTRITION_OK added=%d n_entries=%d" % (added, len(d2["entries"])))


if __name__ == "__main__":
    main()
