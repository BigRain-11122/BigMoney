# -*- coding: utf-8 -*-
"""R404 bm-c: third-machine origin-only forensics for the p1c_stock 688 content-drift case.

Request context (MSG-2026-10-03-0830-bmb-all, bm-c note): bm-b asked bm-c to run
a 688 magnitude spot-check on "our copy" of the p1c_stock cache. FACT: bm-c has
NO local p1c_stock cache (structural, r393/MSG-0230: five 02:06-02:10 burns all
died on load_universe FileNotFoundError; claims released; fleet informed). The
requested local spot-check is therefore NOT EXECUTABLE on bm-c.

What bm-c CAN do third-machine, origin-only, zero local cache: verify the drift
signature from the committed cell products themselves (n_base is a pure
panel-caliber fingerprint: value/quality family masks are cell-independent, so
same-caliber burns must produce identical n_base columns), and verify the
nulls-checkpoint contamination boundary claimed by bm-a r615 (VALUE 81 rows +
QUALITY 9 rows off-caliber under bm-b in-flight burns, done-key resume boundary
visible as an n_engine_syms step).

Read-only forensics: no engine touch, no pool touch, no shared-face writes.
Output: results/_r404bmc_688_crosscheck.json (evidence only).
"""
import json
import os
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000


def git(args):
    """Run git with zero desktop flash; return stdout bytes."""
    return subprocess.check_output(["git"] + args, cwd=ROOT,
                                   creationflags=CREATE_NO_WINDOW)


def provenance(path):
    """Creator commit (first in --follow history) one-line + sha for a path."""
    out = git(["log", "--follow", "--format=%H%x09%s", "--", path])
    lines = [l for l in out.decode("utf-8", "replace").splitlines() if l.strip()]
    if not lines:
        return {"commit": None, "subject": None}
    sha, subj = lines[-1].split("\t", 1)   # oldest = creator
    return {"commit": sha[:9], "subject": subj[:180]}


def load_jsonl(path):
    rows = []
    bad = 0
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                bad += 1
                continue
            if not isinstance(r, dict):     # r570 type-gate law
                bad += 1
                continue
            rows.append(r)
    return rows, bad


def index_by_start(rows):
    idx = {}
    for r in rows:
        s = r.get("start")
        if isinstance(s, str):
            idx[s] = r
    return idx


def compare_n_base(name, rows_a, rows_b, note):
    ia, ib = index_by_start(rows_a), index_by_start(rows_b)
    common = sorted(set(ia) & set(ib))
    div = []
    n_active_diff = 0
    for s in common:
        na, nb = ia[s].get("n_base"), ib[s].get("n_base")
        if na is None or nb is None:
            continue
        if na != nb:
            div.append((s, nb - na))
        if ia[s].get("n_active_universe") != ib[s].get("n_active_universe"):
            n_active_diff += 1
    deltas = [d for _, d in div]
    by_year = Counter(s[:4] for s, _ in div)
    # per-year delta median/max: cohort growth shape (STAR listing growth)
    year_med_max = {}
    for y in sorted(set(s[:4] for s, _ in div)):
        ds = [d for s, d in div if s[:4] == y]
        ds_sorted = sorted(ds)
        year_med_max[y] = {"n": len(ds), "median": ds_sorted[len(ds) // 2],
                           "max": max(ds)}
    return {
        "pair": name,
        "note": note,
        "n_starts_compared": len(common),
        "n_divergent_n_base": len(div),
        "delta_min": min(deltas) if deltas else 0,
        "delta_max": max(deltas) if deltas else 0,
        "delta_hist": dict(Counter(deltas)),
        "first_divergent_start": div[0][0] if div else None,
        "last_divergent_start": div[-1][0] if div else None,
        "divergent_by_year": dict(sorted(by_year.items())),
        "delta_median_max_by_year": year_med_max,
        "n_active_universe_diffs": n_active_diff,
    }


def nulls_boundary(name, path, claim_lo_n, claim_note):
    """Contamination-count verification vs bm-a r615 ledger confession
    (VALUE 81 rows / QUALITY 9 rows off-caliber, k-sequential done-key burns).
    bm-a burned k=0..N-1 off-caliber before kill; bm-b resumed past done keys.
    Per-row content discrimination from committed faces alone is NOT possible
    (per-draw n_engine_syms noise ~+-50 swamps the +1..+140 mask inflation
    effect on selection unions), so this leg verifies row COUNTS + k-continuity
    and reports claimed-boundary segment medians honestly (not a hard gate)."""
    rows, bad = load_jsonl(path)
    ks = {}
    for r in rows:
        k = r.get("k")
        if isinstance(k, int):
            ks[k] = r
    if not ks:
        return {"face": name, "error": "no k rows"}
    kk = sorted(ks)
    kmin, kmax = kk[0], kk[-1]
    missing = [k for k in range(kmin, kmax + 1) if k not in ks]
    series = [ks[k].get("n_engine_syms") for k in kk]

    def _med(v):
        v = sorted(x for x in v if isinstance(x, int))
        return v[len(v) // 2] if v else None

    # claimed boundary: bm-a rows = k=0..claim_lo_n-1, bm-b rows = k=claim_lo_n..
    seg_a = [ks[k].get("n_engine_syms") for k in kk if k < claim_lo_n]
    seg_b = [ks[k].get("n_engine_syms") for k in kk if k >= claim_lo_n]
    # best median separation over all candidate boundaries (data-driven check)
    best_split, best_gap = None, None
    if len(kk) > 2:
        for cut in range(1, len(kk)):
            left = [ks[k].get("n_engine_syms") for k in kk[:cut]]
            right = [ks[k].get("n_engine_syms") for k in kk[cut:]]
            ml, mr = _med(left), _med(right)
            if ml is not None and mr is not None:
                gap = abs(ml - mr)
                if best_gap is None or gap > best_gap:
                    best_gap, best_split = gap, {"k_cut": kk[cut - 1],
                                                 "median_left": ml,
                                                 "median_right": mr}
    return {
        "face": name,
        "claim_note": claim_note,
        "n_rows": len(rows), "bad_rows": bad,
        "k_min": kmin, "k_max": kmax,
        "k_missing_in_range": missing[:10],
        "k_contiguous": not missing,
        "n_engine_syms_series_k_sorted": series,
        "claimed_boundary": {"bm_a_rows_expected": claim_lo_n,
                             "bm_b_rows_on_origin": len(kk) - claim_lo_n,
                             "median_k_below": _med(seg_a),
                             "median_k_ge_claim": _med(seg_b),
                             "discriminable": False,
                             "why_not": "per-draw nes noise >> inflation effect"},
        "best_median_split_any_boundary": best_split,
    }


def main():
    fv = os.path.join(ROOT, "results", "fund_value_p1")
    fq = os.path.join(ROOT, "results", "fund_quality_p1")
    cells = {
        "VALUE-PE_x1": os.path.join(fv, "cells_VALUE-PE_x1.jsonl"),
        "VALUE-PE_x2": os.path.join(fv, "cells_VALUE-PE_x2.jsonl"),
        "VALUE-PB_x1": os.path.join(fv, "cells_VALUE-PB_x1.jsonl"),
        "VALUE-PB_x2": os.path.join(fv, "cells_VALUE-PB_x2.jsonl"),
        "QUALITY-ROE_x1": os.path.join(fq, "cells_QUALITY-ROE_x1.jsonl"),
        "QUALITY-ROE_x2": os.path.join(fq, "cells_QUALITY-ROE_x2.jsonl"),
    }
    missing = [k for k, p in cells.items() if not os.path.exists(p)]
    if missing:
        print("MISSING_FACES: %s" % missing)
        return 2

    data, bad = {}, {}
    for k, p in cells.items():
        data[k], bad[k] = load_jsonl(p)

    # historical off-caliber blob: bm-a r612-613 reland QUALITY-ROE_x2 (superseded
    # by bm-b r609b restore to 93fb399ed caliber)
    hist_blob = git(["show",
                     "78fcec946:results/fund_quality_p1/cells_QUALITY-ROE_x2.jsonl"])
    hist_rows = []
    hbad = 0
    for line in hist_blob.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            hbad += 1
            continue
        if isinstance(r, dict):
            hist_rows.append(r)
        else:
            hbad += 1

    prov = {k: provenance(p[len(ROOT) + 1:].replace("\\", "/"))
            for k, p in cells.items()}

    checks = [
        compare_n_base(
            "VALUE-PE_x1[bm-b] vs VALUE-PE_x2[bm-a]",
            data["VALUE-PE_x1"], data["VALUE-PE_x2"],
            "cross-machine VALUE drift expectation: bm-a copy 100x -> +n_base"),
        compare_n_base(
            "VALUE-PE_x1[bm-b] vs VALUE-PB_x1[bm-a]",
            data["VALUE-PE_x1"], data["VALUE-PB_x1"],
            "cross-machine VALUE drift expectation (second bm-a face)"),
        compare_n_base(
            "VALUE-PE_x1[bm-b] vs VALUE-PB_x2[bm-b]",
            data["VALUE-PE_x1"], data["VALUE-PB_x2"],
            "same-machine sanity anchor: expect 0 divergent (both bm-b panel)"),
        compare_n_base(
            "QUALITY-ROE_x1[bm-b] vs QUALITY-ROE_x2[bm-b]",
            data["QUALITY-ROE_x1"], data["QUALITY-ROE_x2"],
            "same-machine sanity anchor: expect 0 divergent (both bm-b panel)"),
        compare_n_base(
            "QUALITY-ROE_x2[origin=bm-b-restore] vs QUALITY-ROE_x2[bm-a@78fcec946]",
            data["QUALITY-ROE_x2"], hist_rows,
            "bm-b r609b finding reproduction: 59/401 +1..+42 expected"),
    ]

    nulls = [
        nulls_boundary("VALUE-nulls", os.path.join(fv, "nulls.jsonl"), 81,
                        "bm-a r615 ledger: 81 off-caliber rows (k=0..80), "
                        "bm-b in-flight resume from k=81"),
        nulls_boundary("QUALITY-nulls", os.path.join(fq, "nulls.jsonl"), 9,
                       "bm-a r615 ledger: 9 off-caliber rows (k=0..8), "
                       "bm-b in-flight resume from k=9"),
    ]

    out = {
        "batch": "R404-BMC-688-CROSSCHECK",
        "machine": "bm-c",
        "evidence_source": "origin-only committed products (worktree==origin "
                           "after r404 S0 ff to 432ca2001) + git historical blob",
        "local_cache_fact": "bm-c has NO local p1c_stock cache (r393 structural, "
                            "MSG-2026-10-03-0230): requested spot-check on 'my "
                            "copy' not executable - no copy exists",
        "provenance": prov,
        "n_base_comparisons": checks,
        "nulls_contamination_boundary": nulls,
        "bad_parse_rows": bad,
        "history_blob_bad_rows": hbad,
    }
    op = os.path.join(ROOT, "results", "_r404bmc_688_crosscheck.json")
    with open(op, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=True)
    print("WROTE %s" % op)
    for c in checks:
        ym = c.get("delta_median_max_by_year", {})
        ym_s = " ".join("%s:med%s/max%s" % (y, v["median"], v["max"])
                        for y, v in ym.items()) if ym else ""
        print("%s: div=%s delta=[%s..%s] first=%s n_active_diff=%s" % (
            c["pair"], c["n_divergent_n_base"], c["delta_min"],
            c["delta_max"], c["first_divergent_start"],
            c["n_active_universe_diffs"]))
        if ym_s:
            print("   by-year %s" % ym_s)
    for n in nulls:
        cb = n.get("claimed_boundary")
        print("%s: rows=%s k=[%s..%s] contiguous=%s claimed(bm_a=%s bm_b=%s) "
              "med_below=%s med_ge=%s" % (
                  n.get("face"), n.get("n_rows"), n.get("k_min"),
                  n.get("k_max"), n.get("k_contiguous"),
                  cb.get("bm_a_rows_expected"), cb.get("bm_b_rows_on_origin"),
                  cb.get("median_k_below"), cb.get("median_k_ge_claim")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
