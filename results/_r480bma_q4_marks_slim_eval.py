"""D-20260930-27 Q4 marks-slimming evaluation probe (read-only, v2).

Marks line shape (verified against live file): top-level {date, kind,
source, source_rows, traders: {tid: {cash_cny, equity_mark_cny,
positions: [{symbol, quantity, cost_price, mark, ...}], ...}}, ts}.

Audit Q4 caliber: a tick is REDUNDANT when no trader's equity moved >=5bp
AND no position-set change (symbol/quantity/cost_price) AND it is not the
first tick / settle face. This probe measures suppression rates on the
last 3 trading days so the writer change is decided on data, not on the
audit's single-day read. Read-only. rc 0 = measured.
"""
import io
import json
import os
import sys

MARKS_DIR = os.path.join("results", "paper", "marks")
OUT = os.path.join("results", "_r480bma_q4_marks_slim_eval.json")
BP = 5.0  # audit Q4 retention threshold


def _state_key(traders: dict) -> str:
    parts = []
    for tid in sorted(traders):
        t = traders[tid]
        pos = ";".join(
            f"{p.get('symbol')}|{p.get('quantity')}|{p.get('cost_price')}"
            for p in (t.get("positions") or []))
        parts.append(f"{tid}|cash={t.get('cash_cny')}|{pos}")
    return "|".join(parts)


def _min_move_bp(prev: dict, cur: dict) -> float:
    """Smallest per-trader equity move in bp across common traders (bp)."""
    worst = None
    for tid, t in cur.items():
        if tid not in prev:
            return float("inf")  # trader set changed -> state change anyway
        e0 = prev[tid].get("equity_mark_cny")
        e1 = t.get("equity_mark_cny")
        if not e0 or not e1:
            return float("inf")  # unpriced -> keep, never suppress
        move = abs(e1 - e0) / e0 * 1e4
        worst = move if worst is None else min(worst, move)
    return worst if worst is not None else float("inf")


def main() -> int:
    files = sorted(f for f in os.listdir(MARKS_DIR)
                   if f.startswith("marks-") and f.endswith(".jsonl"))
    kept, suppressed = [], []
    per_day = {}
    for fn in files[-3:]:
        rows = [json.loads(l) for l in io.open(os.path.join(MARKS_DIR, fn),
                                               encoding="utf-8") if l.strip()]
        per_day[fn] = len(rows)
        prev = None
        for r in rows:
            kind = r.get("kind", "intraday")
            traders = r.get("traders") or {}
            if prev is None:
                keep, why = True, "first-tick"
            elif kind == "settle":
                keep, why = True, "settle-face"
            else:
                sk = _state_key(traders)
                if sk != prev["sk"]:
                    keep, why = True, "state-change"
                else:
                    mv = _min_move_bp(prev["tr"], traders)
                    if mv >= BP:
                        keep, why = True, f"move {mv:.1f}bp"
                    else:
                        keep, why = False, f"move {mv:.1f}bp < {BP}bp"
            rec = {"file": fn, "ts": r.get("ts"), "kind": kind, "why": why}
            (kept if keep else suppressed).append(rec)
            prev = {"sk": _state_key(traders), "tr": traders}

    n_k, n_s = len(kept), len(suppressed)
    total = n_k + n_s
    out = {
        "probe": "D-20260930-27 Q4 marks slimming evaluation v2",
        "files_read": sorted(per_day), "ticks_per_file": per_day,
        "threshold_bp": BP,
        "total_ticks": total, "kept": n_k, "suppressed": n_s,
        "suppressed_pct": round(100.0 * n_s / total, 1) if total else None,
        "retention_rule": "first-tick + settle + state-change + any trader "
                          "equity move >= 5bp",
        "sample_suppressed": suppressed[:6],
        "note": "writer untouched; decision data for D-27 Q4 (per-trader "
                "caliber: suppress only if ALL traders <5bp and no state "
                "change)",
    }
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"Q4 eval v2: {total} ticks -> keep {n_k}, suppress {n_s} "
          f"({out['suppressed_pct']}%) under >= {BP}bp any-trader rule")
    for fn in sorted(per_day):
        d_sup = sum(1 for r in suppressed if r["file"] == fn)
        print(f"  {fn}: {per_day[fn]} ticks, {d_sup} suppressible "
              f"({100.0 * d_sup / per_day[fn]:.0f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
