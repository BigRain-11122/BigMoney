"""FUND-STAGESTYLE-COMBO-P1 pre-run priors (freeze leg, zero-network).

Prereg sec.5 requires numeric run-before predictions; the placeholder-honesty
rule forbids writing numbers that were not computed. This tool computes the
only numbers a pre-freeze batch may legitimately cite: BASE RATES of the stage
label face itself (how the benchmark behaved inside each frozen stage), never
any conditional-combo outcome.

Inputs (all frozen faces already cited by the prereg):
  results/regime5_labels/REGIME5-<cutoff>.json   stage labels
  data/daily/sh510300.csv                        core48 benchmark daily bars

Output: results/_r1049bmb_sscombo_stage_priors.json

Usage:
    python scripts/sscombo_stage_priors.py run [--labels F] [--bench F] [--tail-q 0.01]
    python scripts/sscombo_stage_priors.py selftest

Exit codes: 0 = normal, 2 = mechanism fault (reported verbatim).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL_DIR = os.path.join(ROOT, "results", "regime5_labels")
BENCH = os.path.join(ROOT, "data", "daily", "sh510300.csv")
RECEIPT = os.path.join(ROOT, "results", "_r1049bmb_sscombo_stage_priors.json")
STATES = ("BULL", "CHOP", "GRIND", "BEAR", "SUPPORT")


def load_labels(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    out = {}
    for row in doc.get("labels") or []:
        out[row["date"]] = row["state"]
    if not out:
        raise ValueError(f"{path}: empty label face")
    return out


def load_bench(path: str) -> list[tuple[str, float]]:
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        for r in rd:
            d = (r.get("date") or "").strip()
            c = (r.get("close") or "").strip()
            if not d or not c:
                continue
            rows.append((d, float(c)))
    if len(rows) < 3:
        raise ValueError(f"{path}: too few bars")
    return rows


def _stats(xs: list[float]) -> dict:
    n = len(xs)
    if not n:
        return {"n": 0}
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / (n - 1) if n > 1 else 0.0
    sd = var ** 0.5
    return {
        "n": n,
        "mean_bp": round(mean * 1e4, 2),
        "sd_bp": round(sd * 1e4, 2),
        "ann_vol_pct": round(sd * (252 ** 0.5) * 100, 2),
        "share_pos": round(sum(1 for x in xs if x > 0) / n, 4),
    }


def compute(labels_path: str, bench_path: str, tail_q: float) -> dict:
    labels = load_labels(labels_path)
    bars = load_bench(bench_path)
    rets: list[tuple[str, float]] = []
    for i in range(1, len(bars)):
        d, c = bars[i]
        prev = bars[i - 1][1]
        if prev <= 0:
            continue
        rets.append((d, c / prev - 1.0))

    # label(t) is assigned to the return realized on day t (close-to-close).
    by_state: dict[str, list[float]] = {s: [] for s in STATES}
    unlabeled = 0
    for d, r in rets:
        s = labels.get(d)
        if s is None:
            unlabeled += 1
            continue
        by_state[s].append(r)

    ordered = sorted(r for _, r in rets)
    k = max(1, int(round(len(ordered) * tail_q)))
    lo_cut, hi_cut = ordered[k - 1], ordered[-k]
    extremes = [(d, r) for d, r in rets if r <= lo_cut or r >= hi_cut]

    per_state = {s: _stats(v) for s, v in by_state.items()}
    total_labeled = sum(per_state[s].get("n", 0) for s in STATES)
    ext_by_state: dict[str, int] = {s: 0 for s in STATES}
    for d, _ in extremes:
        s = labels.get(d)
        if s in ext_by_state:
            ext_by_state[s] += 1

    rows = []
    for s in STATES:
        n = per_state[s].get("n", 0)
        e = ext_by_state[s]
        rows.append({
            "state": s,
            "days": n,
            "day_share_pct": round(100.0 * n / total_labeled, 2) if total_labeled else 0.0,
            "mean_bp": per_state[s].get("mean_bp"),
            "ann_vol_pct": per_state[s].get("ann_vol_pct"),
            "share_pos": per_state[s].get("share_pos"),
            "extreme_days": e,
            "extreme_share_of_state_pct": round(100.0 * e / n, 2) if n else 0.0,
        })

    return {
        "labels_file": os.path.basename(labels_path),
        "bench_file": os.path.basename(bench_path),
        "bars": len(bars),
        "return_days": len(rets),
        "labeled_return_days": total_labeled,
        "unlabeled_return_days": unlabeled,
        "first_day": rets[0][0] if rets else None,
        "last_day": rets[-1][0] if rets else None,
        "bench_min": bars[0][0],
        "bench_max": bars[-1][0],
        "tail_quantile": tail_q,
        "extreme_thresholds_bp": {"low": round(lo_cut * 1e4, 2), "high": round(hi_cut * 1e4, 2)},
        "extreme_days_total": len(extremes),
        "states": rows,
    }


def run(labels_path: str, bench_path: str, tail_q: float) -> int:
    try:
        rep = compute(labels_path, bench_path, tail_q)
    except Exception as exc:  # noqa: BLE001
        print(f"sscombo_stage_priors rc2 mechanism-fault: {exc}")
        return 2
    rep.update({
        "batch": "FUND-STAGESTYLE-COMBO-P1",
        "leg": "pre-run stage base rates (sec.5 prediction anchors)",
        "host": "bm-b",
        "round": "r1049",
        "honesty": "descriptive base rates of the frozen stage label face; no conditional-combo outcome is computed here",
    })
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    for row in rep["states"]:
        print("{state:8s} days={days:5d} share={day_share_pct:6.2f}% mean={mean_bp}bp vol={ann_vol_pct}% "
              "extreme={extreme_days:3d} ({extreme_share_of_state_pct}%)".format(**row))
    print(f"window={rep['first_day']}..{rep['last_day']} extremes_total={rep['extreme_days_total']} "
          f"thresholds={rep['extreme_thresholds_bp']}")
    print(f"receipt={RECEIPT}")
    return 0


def selftest() -> int:
    import tempfile

    tmp = tempfile.mkdtemp(prefix="sscombo_priors_")
    lab = os.path.join(tmp, "L.json")
    ben = os.path.join(tmp, "B.csv")
    days = [f"2020-01-{i:02d}" for i in range(1, 11)]
    states = ["BULL", "BULL", "CHOP", "CHOP", "CHOP", "BEAR", "BEAR", "GRIND", "SUPPORT", "CHOP"]
    with open(lab, "w", encoding="utf-8") as fh:
        json.dump({"labels": [{"date": d, "state": s} for d, s in zip(days, states)]}, fh)
    closes = [100, 110, 121, 121, 121, 110, 99, 99, 99, 99]
    with open(ben, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "open", "high", "low", "close", "volume"])
        for d, c in zip(days, closes):
            w.writerow([d, c, c, c, c, 1])
    rep = compute(lab, ben, 0.2)
    by = {r["state"]: r for r in rep["states"]}
    checks = [
        ("labeled days counted", rep["labeled_return_days"] == 9),
        ("BULL mean = +10% on its single labeled day", by["BULL"]["mean_bp"] == 1000.0 and by["BULL"]["days"] == 1),
        ("CHOP days = 4", by["CHOP"]["days"] == 4),
        ("BEAR direction negative", (by["BEAR"]["mean_bp"] or 0) < 0),
        # 9 returns, tail_q=0.2 -> k=2: two <= -9.09% and two >= +10% are flagged
        ("extremes flagged both tails", rep["extreme_days_total"] == 4),
        ("state shares sum ~100", abs(sum(r["day_share_pct"] for r in rep["states"]) - 100.0) < 0.05),
    ]
    ok = sum(1 for _, v in checks if v)
    for name, v in checks:
        print(f"[{'PASS' if v else 'FAIL'}] {name}")
    print(f"sscombo_stage_priors selftest: {ok}/{len(checks)}")
    return 0 if ok == len(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="SS-COMBO pre-run stage base rates")
    ap.add_argument("mode", choices=("run", "selftest"))
    ap.add_argument("--labels", default=os.path.join(LABEL_DIR, "REGIME5-2026-10-19.json"))
    ap.add_argument("--bench", default=BENCH)
    ap.add_argument("--tail-q", type=float, default=0.01)
    args = ap.parse_args()
    if args.mode == "selftest":
        return selftest()
    return run(args.labels, args.bench, args.tail_q)


if __name__ == "__main__":
    sys.exit(main())