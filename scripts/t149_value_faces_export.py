"""T-2026-10-02-149-P1: value_faces.parquet consolidated export (bm-c -> bm-a).

Data gate only, zero burns (ticket note). Source = machine-local
data/fund_history/<code>/{pe_ttm,pb}.json baidu semi-monthly anchors
(T-131 done lane, R31/R65). One row per (code, anchor_date) with pe_ttm/pb
unioned on date; missing face value = null. ALL done symbols included
(bm-a joins by p1c_stock panel codes).

Sender gates (fail-closed, ticket spec / prereg sec.2):
  n_symbols >= 5100  AND  per-symbol anchor-count median >= 550
  AND anchor coverage 2001-01..2026-09 (global min <= 2001-01-31,
  global max >= 2026-09-01)
Gates not passed -> exit 2, parquet NOT written.

exit 0 = pass/written, 2 = gate fail (fail-closed), 3 = mechanism error.
Idempotent full rebuild; sidecar results/t149_value_faces_export.json.
"""
import json
import os
import statistics
import sys
import time

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "fund_history")
OUT_DIR = os.path.join(ROOT, "data", "fund_history_export")
OUT = os.path.join(OUT_DIR, "value_faces.parquet")
SIDECAR = os.path.join(ROOT, "results", "t149_value_faces_export.json")

MIN_SYMBOLS = 5100
MIN_ANCHOR_MEDIAN = 550.0
COVER_MIN = "2001-01-31"   # global min anchor date must be <= this
COVER_MAX = "2026-09-01"   # global max anchor date must be >= this


def _face_map(code, face):
    path = os.path.join(SRC, code, face + ".json")
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    out = {}
    for r in d.get("rows", []):
        dt = r.get("date")
        if not dt:
            continue
        out[str(dt)[:10]] = r.get("value")
    return out


def main():
    t0 = time.time()
    if not os.path.isdir(SRC):
        print("FAIL no fund_history dir"); sys.exit(3)
    codes = sorted(d for d in os.listdir(SRC)
                   if os.path.isdir(os.path.join(SRC, d)))
    frames = []
    per_sym_n = {}
    missing_face = []
    g_min, g_max = None, None
    for i, code in enumerate(codes):
        try:
            pe = _face_map(code, "pe_ttm")
            pb = _face_map(code, "pb")
        except Exception:
            missing_face.append(code)
            continue
        dates = sorted(set(pe) | set(pb))
        if not dates:
            continue
        per_sym_n[code] = len(dates)
        lo, hi = dates[0], dates[-1]
        g_min = lo if g_min is None or lo < g_min else g_min
        g_max = hi if g_max is None or hi > g_max else g_max
        frames.append(pd.DataFrame({
            "code": code,
            "anchor_date": dates,
            "pe_ttm": [pe.get(d) for d in dates],
            "pb": [pb.get(d) for d in dates],
        }))
        if (i + 1) % 1000 == 0:
            print(f"[{i+1}/{len(codes)}] syms={len(per_sym_n)} "
                  f"t={time.time()-t0:.0f}s", flush=True)

    n_syms = len(per_sym_n)
    med = statistics.median(per_sym_n.values()) if per_sym_n else 0.0
    gates = {
        "n_symbols_ok": n_syms >= MIN_SYMBOLS,
        "anchor_median_ok": med >= MIN_ANCHOR_MEDIAN,
        "coverage_ok": bool(g_min and g_max and g_min <= COVER_MIN
                            and g_max >= COVER_MAX),
    }
    report = {
        "ticket": "T-2026-10-02-149-P1",
        "machine": "bm-c",
        "n_symbols": n_syms,
        "dir_count": len(codes),
        "missing_face_syms": len(missing_face),
        "anchor_median": med,
        "anchor_global_min": g_min,
        "anchor_global_max": g_max,
        "gates": gates,
        "out": OUT,
    }
    if not all(gates.values()):
        report["verdict"] = "GATE_FAIL fail-closed, parquet not written"
        with open(SIDECAR, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
        print("GATE_FAIL " + json.dumps(gates))
        sys.exit(2)

    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.concat(frames, ignore_index=True)
    report["n_rows"] = int(len(df))
    report["n_pe_ttm_nonnull"] = int(df["pe_ttm"].notna().sum())
    report["n_pb_nonnull"] = int(df["pb"].notna().sum())
    df.to_parquet(OUT, engine="pyarrow", compression="zstd", index=False)
    report["bytes"] = os.path.getsize(OUT)
    report["elapsed_sec"] = round(time.time() - t0, 1)
    report["verdict"] = "PASS"
    with open(SIDECAR, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print(f"PASS n_symbols={n_syms} median={med} rows={len(df)} "
          f"bytes={report['bytes']} cov={g_min}..{g_max} "
          f"t={report['elapsed_sec']}s")


if __name__ == "__main__":
    main()
