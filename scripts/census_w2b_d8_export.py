# -*- coding: utf-8 -*-
"""W2-B D8 face export -- T-86 s2 wave-2 W2-B bm-a-side small-artifact build.

Roster (FROZEN R344 commit f084c8e2 precedes this build, R99):
results/census_fusion_s2/w2b_roster.json sec.9.4 D8-only faces. EXPLORATION
FACE: zero judgment claims / zero paper eligibility; sole consumer = the
W2-B cross-wave fusion census runner (scripts/census_fusion_s2_w2b.py,
lane=bm-b) -- the D-family standalone REJECT is disclosed with the batch.

Lane: bm-a ONLY (sina MF panel data/sina_mf/per is bm-a-local gitignored;
T-72 collector lineage). Panel absent -> honest exit 2 (one-shot build
artifact, not an S6 chain link).

Faces (roster w2b.faces, RAW values; z-scoring happens IN-RUNNER via the
wave-1 W1._zscore convention -- same as every A-face in the census, so the
combo score machinery is structurally identical):
  4 net faces  = panel raw columns r0_net/r1_net/r2_net/r3_net verbatim
  4 ratio faces= rX_net/turnover (SINA_CONSTRUCT_P1 sec.3 TIER_rX literal
                 formula; turnover = same-panel column, no external source,
                 no unit conversion; turnover>0 guard mirrored from the
                 judged construct: non-finite or <=0 -> NaN face value).

Laws (frozen; mirrored from the judged construct batch sina_construct_ic
load_sina_panel, byte-honest lineage SINA_CONSTRUCT_P1 sec.2):
  - dtype=str read + to_numeric coerce (judged-artifact read convention).
  - per-row self-collapse law |netamount - sum(r0_net..r3_net)| > 1e-3 ->
    rejected + counted (COLLAPSE_TOL family; the %.10g write-rounding latent
    defect makes this ~9-10% of rows at |netamount|>=1e9 -- KNOWN, disclosed
    with every artifact, non-blocking for the exploration census).
  - netamount finite + any tier missing -> conservative unverifiable
    rejection, counted separately (collector booking law mirrored).
  - duplicate opendate rows: keep-last dedup, counted (overlap insurance).
  - evidence_cutoff 2026-09-24 lockbox: rows past cutoff dropped with a
    disclosure count, never reflowed.
  - NO calendar/eligibility/mask filter at export (export = full-panel
    verbatim; the runner reindexes to the astock panel calendar, so
    non-panel dates drop there; short-history symbols disclosed here, not
    filtered).

Output:
  data/census_w2b/w2b_d8_faces.npz  (savez_compressed; gitignored data lane,
       travels via TRANSFER plan-A transfer branch, fleet/TRANSFER.md sec.2)
  results/census_fusion_s2/w2b_d8_manifest.json (small, git-tracked; the
       runner's fail-closed sha256 gate reads THIS file and recomputes the
       npz hash on receipt; container zip timestamps are not byte-stable
       across reruns -- regenerate manifest with every export, disclosed).

Usage: python scripts/census_w2b_d8_export.py export | selftest
"""
import argparse
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PER_DIR = os.path.join(ROOT, "data", "sina_mf", "per")
STATUS_JSON = os.path.join(ROOT, "results", "sina_mf_update_status.json")
OUT_DIR = os.path.join(ROOT, "data", "census_w2b")
OUT_NPZ = os.path.join(OUT_DIR, "w2b_d8_faces.npz")
MANIFEST = os.path.join(ROOT, "results", "census_fusion_s2",
                        "w2b_d8_manifest.json")

BATCH = "CENSUS_FUS_S2_W2B-D8-EXPORT"
TICKET = "T-2026-09-26-86-P1 s2 wave-2 W2-B (CEO O-20260926-2320)"
ROSTER_REF = "results/census_fusion_s2/w2b_roster.json sec.9.4 (FROZEN R344)"
CUTOFF = "2026-09-24"          # evidence_cutoff (roster gates.sina_mf_panel)
COLLAPSE_TOL = 1e-3            # |netamount - sum(rX_net)| absolute gate

TIER_NETS = ["r0_net", "r1_net", "r2_net", "r3_net"]
# roster w2b.faces ctor mapping (zero invention: name -> (col, kind))
FACE_SPECS = [
    ("sina_mf_eltra_large_net", "r0_net", "net"),
    ("sina_mf_eltra_large_ratio", "r0_net", "ratio"),
    ("sina_mf_large_net", "r1_net", "net"),
    ("sina_mf_large_net_ratio", "r1_net", "ratio"),
    ("sina_mf_mid_net", "r2_net", "net"),
    ("sina_mf_mid_net_ratio", "r2_net", "ratio"),
    ("sina_mf_small_net", "r3_net", "net"),
    ("sina_mf_small_net_ratio", "r3_net", "ratio"),
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_panel_rows(per_dir=PER_DIR, cutoff=CUTOFF):
    """Per-symbol numeric frame dict + law bookkeeping, mirroring the judged
    construct loader (sina_construct_ic.load_sina_panel). Fail-closed:
    panel dir absent or empty -> (None, report), caller exits 2."""
    if not os.path.isdir(per_dir):
        return None, {"ok": False, "fail": "sina MF panel dir absent "
                     "(data/sina_mf/per; lane=bm-a only)"}
    files = sorted(glob.glob(os.path.join(per_dir, "*.csv")))
    if not files:
        return None, {"ok": False, "fail": "panel dir empty"}
    cutoff_ts = pd.Timestamp(cutoff)
    cols = ["netamount", "turnover"] + TIER_NETS
    univ = {}
    n_trunc = n_bad = n_unver = n_dup = n_schema = 0
    row_counts = []
    for p in files:
        code = os.path.basename(p)[:-4]
        try:
            df = pd.read_csv(p, dtype=str)
        except Exception:
            continue
        if "opendate" not in df.columns:
            n_schema += 1
            continue
        if any(c not in df.columns for c in cols):
            n_schema += 1
            continue
        df["__d"] = pd.to_datetime(df["opendate"], errors="coerce")
        df = df.dropna(subset=["__d"])
        n_dup += len(df) - len(df.drop_duplicates("__d", keep="last"))
        df = df.drop_duplicates("__d", keep="last")
        before = len(df)
        df = df[df["__d"] <= cutoff_ts]          # cutoff lockbox
        n_trunc += before - len(df)
        if df.empty:
            # empty-body CSVs (IPO no-data): store a coerced empty float64
            # frame with the full 6-col schema -- raw str frame would poison
            # the pivot dtype (r345 real-panel crash)
            univ[code] = pd.DataFrame(
                {c: pd.Series(dtype="float64") for c in cols},
                index=pd.DatetimeIndex([])).sort_index()
            row_counts.append(0)
            continue
        # empty-body CSVs (IPO no-data) keep str dtype through to_numeric
        # and integer-only files coerce to int64 -- force uniform float64
        # (same end state as the judged construct's float64 grids)
        num = df[cols].apply(pd.to_numeric, errors="coerce").astype("float64")
        net = num["netamount"].values
        tiers = num[TIER_NETS].values
        ok_net = np.isfinite(net)
        tier_missing = (~np.isfinite(tiers)).any(axis=1)
        bad = ok_net & (np.abs(net - np.nansum(tiers, axis=1)) > COLLAPSE_TOL)
        unver = ok_net & tier_missing
        keep_row = ~(bad | unver)
        n_bad += int(bad.sum())
        n_unver += int(unver.sum())
        kept = num[keep_row]
        univ[code] = kept.set_index(df["__d"][keep_row]).sort_index()
        row_counts.append(len(kept))
    rep = {
        "ok": True, "panel_files": len(files), "n_symbols": len(univ),
        "rows_dropped_post_cutoff": int(n_trunc),
        "collapse_rejected": int(n_bad),
        "unverifiable_rows": int(n_unver),
        "duplicate_date_rows_dropped": int(n_dup),
        "schema_foreign_files": int(n_schema),
        "collapse_tol": COLLAPSE_TOL,
        "min_rows": int(min(row_counts)) if row_counts else 0,
        "median_rows": int(np.median(row_counts)) if row_counts else 0,
        "symbols_below_50_rows": int(sum(1 for n in row_counts if n < 50)),
        "cutoff": CUTOFF,
    }
    return univ, rep


def build_face_matrices(univ):
    """Pivot to (T_d x N_d) float64 matrices; absent (date,symbol) = NaN.
    Ratio faces carry the judged turnover>0 guard (non-finite or <=0 ->
    NaN), mirrored from sina_construct_ic.build_constructs."""
    idx = sorted(set().union(*[set(df.index) for df in univ.values()]))
    idx = pd.DatetimeIndex(idx)
    syms = sorted(univ.keys())
    tvr = pd.DataFrame({s: univ[s]["turnover"] for s in syms}) \
        .reindex(index=idx).sort_index()
    with np.errstate(invalid="ignore", divide="ignore"):
        safe = tvr.where(np.isfinite(tvr) & (tvr > 0))
        faces = {}
        for name, col, kind in FACE_SPECS:
            raw = pd.DataFrame({s: univ[s][col] for s in syms}) \
                .reindex(index=idx).sort_index()
            faces[name] = raw.div(safe) if kind == "ratio" else raw
    return idx, syms, faces


def export(per_dir=PER_DIR):
    t0 = time.time()
    univ, rep = load_panel_rows(per_dir=per_dir)
    if univ is None or not rep["ok"]:
        print("DATA GATE FAIL (fail-closed, exit 2):", rep.get("fail"))
        return 2
    print("[gate]", json.dumps(rep, ensure_ascii=False))
    idx, syms, faces = build_face_matrices(univ)
    os.makedirs(OUT_DIR, exist_ok=True)
    payload = {"dates_iso": np.array([str(x.date()) for x in idx]),
               "syms": np.array(syms)}
    for name in [n for n, _, _ in FACE_SPECS]:
        payload[name] = np.ascontiguousarray(
            faces[name].values, dtype=np.float64)
    np.savez_compressed(OUT_NPZ, **payload)
    sha = sha256_of(OUT_NPZ)
    size = os.path.getsize(OUT_NPZ)

    status_panel = None
    if os.path.exists(STATUS_JSON):
        with open(STATUS_JSON, encoding="utf-8") as fh:
            status_panel = json.load(fh).get("panel")

    manifest = {
        "batch": BATCH, "ticket": TICKET, "roster_ref": ROSTER_REF,
        "artifact": "data/census_w2b/w2b_d8_faces.npz",
        "sha256": sha, "bytes": int(size),
        "n_dates": len(idx), "n_syms": len(syms),
        "date_start": str(idx.min().date()), "date_end": str(idx.max().date()),
        "faces": [n for n, _, _ in FACE_SPECS],
        "face_ctor": ("RAW values: 4 net = r0_net..r3_net verbatim; 4 ratio = "
                      "rX_net/turnover with the judged turnover>0 guard "
                      "(SINA_CONSTRUCT_P1 sec.3 TIER literal formula); "
                      "z-scoring happens IN-RUNNER (W1._zscore wave-1 "
                      "convention) -- do NOT pre-z-score"),
        "law_lineage": ("row laws mirrored from sina_construct_ic."
                        "load_sina_panel (judged batch): dtype=str read + "
                        "to_numeric coerce; self-collapse |netamount - "
                        "sum(rX_net)| > 1e-3 rejected+counted (the %.10g "
                        "write-rounding latent defect lands ~9-10% of rows "
                        "at |netamount|>=1e9 -- known, disclosed, "
                        "non-blocking); netamount finite + tier missing -> "
                        "unverifiable rejection; duplicate-date keep-last; "
                        "cutoff lockbox 2026-09-24; NO calendar/mask filter "
                        "at export (runner-side alignment drops non-panel "
                        "dates)"),
        "panel_report": rep,
        "panel_status_echo": status_panel,
        "transfer": {
            "channel": "git plan-A transfer branch (fleet/TRANSFER.md sec.2)",
            "branch_hint": "transfer/w2b-d8",
            "note": ("zip container timestamps are NOT byte-stable across "
                      "reruns; regenerate manifest with every export; the "
                      "runner gate binds this manifest sha to the exact "
                      "transferred npz (fail-closed)")},
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "generated_at_epoch_utc": int(time.time()),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    s = json.dumps(manifest, ensure_ascii=False, indent=1)
    json.loads(s)
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        fh.write(s)
    print(f"[done] npz={size/1e6:.1f}MB sha256={sha[:16]}... "
          f"dates={len(idx)} syms={len(syms)} faces=8 "
          f"collapse_reject={rep['collapse_rejected']} "
          f"unver={rep['unverifiable_rows']} "
          f"cutoff_drop={rep['rows_dropped_post_cutoff']} "
          f"elapsed={manifest['elapsed_sec']}s")
    return 0


# ---------------------------------------------------------------- selftest

def selftest():
    """Hermetic (no real panel, no network). r263 law."""
    import tempfile
    ok = True

    def t(name, cond):
        nonlocal ok
        print(("PASS" if cond else "FAIL"), name)
        ok = ok and bool(cond)

    with tempfile.TemporaryDirectory() as td:
        per = os.path.join(td, "per")
        os.makedirs(per)
        rng = np.random.default_rng(7)
        dates = pd.bdate_range("2026-06-01", periods=30)
        for i in range(6):
            code = f"00000{i}"
            n = len(dates)
            turnover = rng.uniform(10, 100, n)
            tiers = rng.normal(0, 5e6, (n, 4))
            net = tiers.sum(axis=1)
            df = pd.DataFrame({
                "opendate": [str(d.date()) for d in dates],
                "netamount": net, "turnover": turnover,
                "r0_net": tiers[:, 0], "r1_net": tiers[:, 1],
                "r2_net": tiers[:, 2], "r3_net": tiers[:, 3]})
            # [1] cutoff lockbox: one future row (past 2026-09-24)
            df.loc[len(df)] = ["2099-01-01", 0.0, 50.0, 0, 0, 0, 0]
            # [2] self-collapse law: |1e9 - 4e8| = 6e8 > 1e-3 -> bad
            df.loc[len(df)] = [str(dates[5].date()), 1e9, 50.0,
                               1e8, 1e8, 1e8, 1e8]
            # [3] unverifiable: net finite + r3_net missing -> reject
            df.loc[len(df)] = [str(dates[6].date()), 5e6, 50.0,
                               1e6, 1e6, 1e6, np.nan]
            # [4] duplicate date: keep-last wins
            df.loc[len(df)] = [str(dates[7].date()), 0.0, 0.0,
                               0, 0, 0, 0]
            df.to_csv(os.path.join(per, f"{code}.csv"), index=False)
        univ, rep = load_panel_rows(per_dir=per, cutoff="2026-09-24")
        t("[1] cutoff lockbox drops the 2099 row (6 files x 1)",
          rep["ok"] and rep["rows_dropped_post_cutoff"] == 6
          and rep["n_symbols"] == 6)
        # per-file expectation math: 3 injected rows land on EXISTING dates
        # -> 3 keep-last dups; the unver row (r3_net NaN, |5e6-3e6|>tol)
        # trips BOTH counters (nansum skips the missing tier) -- same
        # double-count property as the judged construct loader accounting.
        t("[2] collapse law: 6 true-bad + 6 unver-also-tripping-tol = 12",
          rep["collapse_rejected"] == 12)
        t("[3] unverifiable rows counted separately (6 files x 1)",
          rep["unverifiable_rows"] == 6)
        t("[4] dup keep-last 3/file=18; kept rows 30-2laws=28",
          rep["duplicate_date_rows_dropped"] == 18
          and all(len(d) == 28 for d in univ.values()))
        idx, syms, faces = build_face_matrices(univ)
        tvr0 = univ[syms[0]]["turnover"]
        t("[5] pivot shapes (28,6) + net verbatim + ratio w/ guard",
          all(faces[n].shape == (28, 6) for n in faces)
          and np.allclose(faces["sina_mf_eltra_large_net"].values[:, 0],
                          univ[syms[0]]["r0_net"], equal_nan=True)
          and np.allclose(
              faces["sina_mf_eltra_large_ratio"].values[:, 0],
              univ[syms[0]]["r0_net"] / tvr0.where(tvr0 > 0),
              equal_nan=True))
        # [6] turnover<=0 guard: ratio NaN, net verbatim (kept row 7 col)
        r_col = faces["sina_mf_eltra_large_ratio"].values[
            list(idx).index(dates[7]), 0]
        n_col = faces["sina_mf_eltra_large_net"].values[
            list(idx).index(dates[7]), 0]
        t("[6] turnover<=0 dup-row: ratio=NaN, net verbatim 0.0",
          np.isnan(r_col) and n_col == 0.0)
        # [7] full export round-trip on synthetic dir (ALL paths swapped)
        global OUT_DIR, OUT_NPZ, MANIFEST
        saved = (OUT_DIR, OUT_NPZ, MANIFEST)
        try:
            OUT_DIR = os.path.join(td, "out")
            OUT_NPZ = os.path.join(OUT_DIR, "w2b_d8_faces.npz")
            MANIFEST = os.path.join(td, "manifest.json")
            rc = export(per_dir=per)
            mf = json.load(open(MANIFEST, encoding="utf-8"))
            t("[7] export rc=0 + manifest sha matches recomputed npz hash",
              rc == 0 and mf["sha256"] == sha256_of(OUT_NPZ)
              and mf["n_dates"] == 28 and mf["n_syms"] == 6)
            with np.load(OUT_NPZ) as z:
                t("[8] npz round-trip: dates/syms/faces byte-faithful",
                  list(z["syms"]) == syms
                  and all(np.allclose(z[n], faces[n].values, equal_nan=True)
                          for n in [x[0] for x in FACE_SPECS]))
        finally:
            OUT_DIR, OUT_NPZ, MANIFEST = saved
    # [9] lane gate: absent panel dir -> fail-closed
    univ2, rep2 = load_panel_rows(per_dir=os.path.join("Z:", "nope"))
    t("[9] absent panel -> ok=False (lane=bm-a honest exit 2)",
      univ2 is None and not rep2["ok"])
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["export", "selftest"])
    a = ap.parse_args()
    return selftest() if a.cmd == "selftest" else export()


if __name__ == "__main__":
    sys.exit(main())
