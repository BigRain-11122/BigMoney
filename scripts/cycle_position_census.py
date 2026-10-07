# -*- coding: utf-8 -*-
"""cycle_position 3-axis census (REGIME-5 supply line next piece).

Measures the emotion-cycle three-axis panel on the frozen S5_01_ZT_PILOT
replay window (12 trading days, 2026-09-14..2026-09-30):

  axis 1  N_zt     -- limit-up pool size   (profit-effect breadth)
  axis 2  N_dt     -- limit-down pool size (loss-effect breadth)
  axis 3  zb_rate  -- opened-board rate    (attack divergence),
                      per-day = zbgc / (zt + zbgc), zero-attack day = null

Descriptive census only -- NOT a judged face, no backtest, no engine, no
admission.  Thresholds derive from this same window's distributions and
will be re-anchored when the forward zt_pool accrual (FIRST_DATE
2026-10-08, >=10td) feeds the REGIME-5 supply prereg (~2026-10-22 usable).

Inputs : results/zt_pool_pilot_replay.json + results/zt_pool_pilot_replay_days.csv
Output : results/cycle_position_census.json
Exit   : 0 ok / 2 mechanism fault.  selftest subcommand = offline.
"""
import csv
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_JSON = os.path.join(ROOT, "results", "zt_pool_pilot_replay.json")
SRC_CSV = os.path.join(ROOT, "results", "zt_pool_pilot_replay_days.csv")
OUT = os.path.join(ROOT, "results", "cycle_position_census.json")

CORE_FACES = ("zt", "zbgc", "dtgc")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def pct(sorted_vals, q):
    """Linear-interpolation percentile on an already-sorted list."""
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    pos = q * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return float(sorted_vals[lo]) * (1 - frac) + float(sorted_vals[hi]) * frac


def median(vals):
    s = sorted(vals)
    return pct(s, 0.5)


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs)
    dy = sum((y - my) ** 2 for y in ys)
    if dx <= 0 or dy <= 0:
        return None
    return num / (dx ** 0.5 * dy ** 0.5)


def rankdata(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs, ys):
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    return pearson(rankdata(xs), rankdata(ys))


def load_day_panel():
    """rows: {day: {face: n}} from the pilot days csv (dedup counts)."""
    rows = {}
    with open(SRC_CSV, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["face"] not in CORE_FACES:
                continue
            rows.setdefault(r["day"], {})[r["face"]] = int(r["n"])
    return {d: rows[d] for d in sorted(rows)}


def build_panel(day_rows):
    panel = []
    for day, faces in sorted(day_rows.items()):
        n_zt = faces.get("zt", 0)
        n_zbgc = faces.get("zbgc", 0)
        n_dt = faces.get("dtgc", 0)
        attacks = n_zt + n_zbgc
        panel.append({
            "day": day,
            "n_zt": n_zt,
            "n_dt": n_dt,
            "n_zbgc": n_zbgc,
            "zb_rate": round(n_zbgc / attacks, 6) if attacks > 0 else None,
        })
    return panel


def axis_stats(panel, key):
    vals = [r[key] for r in panel if r[key] is not None]
    s = sorted(vals)
    return {
        "n": len(vals),
        "min": s[0] if s else None,
        "p25": round(pct(s, 0.25), 4) if s else None,
        "median": round(pct(s, 0.5), 4) if s else None,
        "p75": round(pct(s, 0.75), 4) if s else None,
        "p99": round(pct(s, 0.99), 4) if s else None,
        "max": s[-1] if s else None,
    }


def marker_rows(panel, stats):
    """Descriptive markers, thresholds from this window's own distribution."""
    zt_med = stats["n_zt"]["median"] or 0
    dt_med = stats["n_dt"]["median"] or 0
    zb_med = stats["zb_rate"]["median"] or 0
    out = []
    for r in panel:
        marks = []
        if zt_med and r["n_zt"] < 40:
            marks.append("n_zt_lowband(<40)")  # pilot P2 partial-miss band
        if dt_med and r["n_dt"] >= 4 * dt_med:
            marks.append("n_dt_spike(>=4x med)")  # r857 09-28 observation
        if zb_med and r["zb_rate"] is not None and r["zb_rate"] > 1.5 * zb_med:
            marks.append("zb_divergence_high(>1.5x med)")
        out.append({"day": r["day"], "markers": marks})
    return out


def next_day_associations(panel):
    """Illustrative only: t -> t+1 axis association (N-1 pairs)."""
    pairs_zt_dt, pairs_zt_zb = [], []
    for a, b in zip(panel, panel[1:]):
        pairs_zt_dt.append((a["n_dt"], b["n_zt"]))
        if a["zb_rate"] is not None:
            pairs_zt_zb.append((a["zb_rate"], b["n_zt"]))
    res = {"pair_count": len(pairs_zt_dt)}
    if pairs_zt_dt:
        xs, ys = zip(*pairs_zt_dt)
        res["n_dt_t_vs_n_zt_t1"] = {
            "pearson": round(pearson(xs, ys), 4) if pearson(xs, ys) is not None else None,
            "spearman": round(spearman(list(xs), list(ys)), 4) if spearman(list(xs), list(ys)) is not None else None,
        }
    if pairs_zt_zb:
        xs, ys = zip(*pairs_zt_zb)
        sp = spearman(list(xs), list(ys))
        pe = pearson(xs, ys)
        res["zb_rate_t_vs_n_zt_t1"] = {
            "pearson": round(pe, 4) if pe is not None else None,
            "spearman": round(sp, 4) if sp is not None else None,
        }
    return res


def run():
    pilot = json.load(open(SRC_JSON, encoding="utf-8"))
    panel = build_panel(load_day_panel())
    if len(panel) < 5:
        print("census: panel too small (%d days) -- fault" % len(panel))
        return 2
    stats = {
        "n_zt": axis_stats(panel, "n_zt"),
        "n_dt": axis_stats(panel, "n_dt"),
        "zb_rate": axis_stats(panel, "zb_rate"),
    }
    out = {
        "face": "cycle_position_census",
        "lane": "bm-a",
        "descriptive_census": True,
        "not_a_judged_face": True,
        "zero_backtest_zero_engine_zero_admission": True,
        "evidence_cutoff": "2026-09-30",
        "window_note": (
            "12 trading days from frozen S5_01_ZT_PILOT replay batch; "
            "associations are illustrative at this N; forward zt_pool "
            "accrual (FIRST_DATE 2026-10-08, >=10td) re-anchors thresholds "
            "in the REGIME-5 supply prereg (~2026-10-22 usable)"),
        "provenance": {
            "pilot_batch": pilot.get("batch"),
            "pilot_spec": pilot.get("spec"),
            "src_json_sha256": sha256_file(SRC_JSON),
            "src_csv_sha256": sha256_file(SRC_CSV),
        },
        "axes": {
            "axis_1_n_zt": "limit-up pool size (profit-effect breadth)",
            "axis_2_n_dt": "limit-down pool size (loss-effect breadth)",
            "axis_3_zb_rate": "opened-board rate zbgc/(zt+zbgc) (divergence)",
        },
        "per_day": panel,
        "distribution": stats,
        "markers": marker_rows(panel, stats),
        "next_day_associations": next_day_associations(panel),
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("census: %d days, N_zt med=%s p99=%s | N_dt med=%s max=%s | "
          "zb med=%s -> %s" % (
              len(panel), stats["n_zt"]["median"], stats["n_zt"]["p99"],
              stats["n_dt"]["median"], stats["n_dt"]["max"],
              stats["zb_rate"]["median"], OUT))
    return 0


def selftest():
    import tempfile
    global SRC_JSON, SRC_CSV, OUT
    td = tempfile.mkdtemp()
    day_rows = {}
    data = [("2026-01-05", 50, 10, 8), ("2026-01-06", 30, 2, 12),
            ("2026-01-07", 80, 0, 5), ("2026-01-08", 55, 1, 3),
            ("2026-01-09", 0, 0, 0), ("2026-01-12", 60, 40, 6)]
    csv_path = os.path.join(td, "days.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        fh.write("day,face,rows_raw,rows_dedup,dup_codes,n,max_board,ladder,"
                 "path2_identity\n")
        for day, zt, dt, zb in data:
            for face, n in (("zt", zt), ("dtgc", dt), ("zbgc", zb)):
                fh.write("%s,%s,%d,%d,0,%d,None,null,True\n"
                        % (day, face, n, n, n))
    json_path = os.path.join(td, "pilot.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump({"batch": "SELFTEST", "spec": "x"}, fh)
    out_path = os.path.join(td, "census.json")
    SRC_JSON, SRC_CSV, OUT = json_path, csv_path, out_path
    rc = run()
    assert rc == 0
    d = json.load(open(out_path, encoding="utf-8"))
    p = {r["day"]: r for r in d["per_day"]}
    # axis math: zb_rate = zbgc/(zt+zbgc), stored 6-decimal rounded
    assert abs(p["2026-01-05"]["zb_rate"] - round(8 / 58, 6)) < 1e-9
    # zero-attack day -> zb_rate null (honest, not 0)
    assert p["2026-01-09"]["zb_rate"] is None
    assert p["2026-01-09"]["n_zt"] == 0 and p["2026-01-09"]["n_dt"] == 0
    # spike marker: N_dt=40 vs median of [0,0,1,2,10,40]=1.0 -> 40>=4x
    marks = {m["day"]: m["markers"] for m in d["markers"]}
    assert any("n_dt_spike" in x for x in marks["2026-01-12"])
    assert any("n_zt_lowband" in x for x in marks["2026-01-06"])
    # determinism: re-run byte-identical
    b1 = open(out_path, "rb").read()
    run()
    assert open(out_path, "rb").read() == b1
    assert d["next_day_associations"]["pair_count"] == 5
    print("selftest: 8/8 PASS")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    sys.exit(run())
