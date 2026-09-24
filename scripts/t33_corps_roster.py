"""T-2026-09-24-33 deliverable-1: corps assignment roster (28 members).

Aggregation batch over recorded cells -- ZERO new trials (t24_prospect_paper
precedent: aggregation/labeling is not an experiment; source batches
T22_VIRTUAL_TIMEPOINTS / T24_G2_PACK already ledgered their cells).

Prereg (frozen pre-run): research/T33_CORPS_ROSTER.md
Canon: firm/STYLE_CORPS.md v1.1 (O-20260924-2012/2030)

Assignment rule (frozen, data-driven per STYLE_CORPS s5):
  registered (6): segment = regime_proxy state at T-22 startpoint; primary
  judgment = base face 12m window; segment_pass = beat_rate_12m >= 0.50 AND
  n_startpoints >= 30; corps = argmax beat_rate among passing segments
  (tie-break pooled excess); no_blowup gate = worst dd (all windows) >= -0.35.
  x2 face / 6m / 24m disclosed-only (anti post-hoc).
  prospect (22): candidate corps from the O-2012 s3 CEO-named family lists
  ONLY; unlisted families = pending-classification (honest); segment evidence
  absent (T-22 covered registered only) -> status=candidate, never assigned.

Exit contract: 0 = ok, 2 = data gates red. selftest = offline fixtures.
"""
import argparse
import hashlib
import json
import math
import os
import sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
T22_DIR = os.path.join(RESULTS, "t22")
G2_DIR = os.path.join(RESULTS, "prospect_g2")
POOL_PATH = os.path.join(RESULTS, "prospect_pool.json")
OUT_PATH = os.path.join(RESULTS, "corps_roster.json")
PREREG_PATH = os.path.join(ROOT, "research", "T33_CORPS_ROSTER.md")
EVIDENCE_CUTOFF = "2026-09-23"

CORPS_ATTACK, CORPS_CHOP, CORPS_DEFENSE = "attack", "chop", "defense"
SEG_TO_CORPS = {"bull": CORPS_ATTACK, "chop": CORPS_CHOP, "bear": CORPS_DEFENSE}
BEAT_RATE_LINE = 0.50
MIN_N = 30
BLOWUP_LINE = -0.35
Z = 1.96

# Frozen family -> candidate corps map (O-20260924-2012 s3 CEO-named lists ONLY;
# strategy-name keyed = pool "name" / G2 entry_key prefix before "(").
FAMILY_CORPS_MAP = {
    "vol_breakout": CORPS_ATTACK,
    "inside_bar_breakup": CORPS_ATTACK,
    "duck_head": CORPS_ATTACK,
    "bb_squeeze_breakout": CORPS_CHOP,
    "doji_at_low": CORPS_CHOP,
    "hammer_reversal": CORPS_CHOP,
    "three_methods_up": CORPS_CHOP,
    "oversold_bounce_20_15": CORPS_CHOP,
    # alias: same CEO-named strategy (超卖反弹) -- pool name vs G2 entry_key
    # function-name spelling differ; map semantics unchanged (join fix, J18).
    "oversold_bounce": CORPS_CHOP,
}
# unlisted -> pending-classification (prereg s3): ma_converge_break,
# immortal_guide, ants_climb, rsrs_timing.

WINDOWS = ("6m", "12m", "24m")


def wilson_ci(k, n):
    if n == 0:
        return (None, None)
    p = k / n
    z2 = Z * Z
    denom = 1 + z2 / n
    center = p + z2 / (2 * n)
    spread = Z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return (round(max(0.0, (center - spread) / denom), 4),
            round(min(1.0, (center + spread) / denom), 4))


def load_cells(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))  # natural JSON face (r52 pitfall law)
    return rows


def episode_blocks(cells):
    """Count contiguous same-regime startpoint blocks per regime (pos-ordered);
    honest lower bound of independent segment windows (prereg s3)."""
    blocks = {s: 0 for s in SEG_TO_CORPS}
    prev_pos, prev_reg = None, None
    for c in sorted(cells, key=lambda x: x["pos"]):
        r = c["regime"]
        if r not in blocks:
            continue
        if r != prev_reg or c["pos"] != (prev_pos + 1 if prev_pos is not None else c["pos"]):
            blocks[r] += 1
        prev_pos, prev_reg = c["pos"], r
    return blocks


def segment_stats(cells):
    """cells = one trader's base-face cells; x2 disclosure joined by key."""
    segs = {}
    for c in cells:
        segs.setdefault(c["regime"], []).append(c)
    out = {}
    for seg, rows in segs.items():
        n = len(rows)
        beats = sum(1 for r in rows if r.get("beat_12m"))
        k12 = sum(1 for r in rows if r.get("beat_12m"))
        rate = round(k12 / n, 4) if n else None
        excess = round(sum(r["ret_12m"] - r["p_ret_12m"] for r in rows) / n, 6) if n else None
        worst_dd = round(min(min(r["dd_6m"], r["dd_12m"], r["dd_24m"]) for r in rows), 4) if n else None
        lo, hi = wilson_ci(k12, n)
        out[seg] = {
            "n_startpoints": n,
            "beat_rate_12m": rate,
            "beat_ci95_12m": [lo, hi],
            "pooled_excess_12m": excess,
            "n_trades_12m": int(sum(r.get("trades_12m", 0) for r in rows)),
            "worst_dd_all_windows": worst_dd,
            "beat_rate_6m": round(sum(1 for r in rows if r.get("beat_6m")) / n, 4) if n else None,
            "beat_rate_24m": round(sum(1 for r in rows if r.get("beat_24m")) / n, 4) if n else None,
        }
    return out


def x2_face_disclosure(x2_cells):
    segs = {}
    for c in x2_cells:
        segs.setdefault(c["regime"], []).append(c)
    out = {}
    for seg, rows in segs.items():
        n = len(rows)
        out[seg] = {
            "n_startpoints": n,
            "beat_rate_12m": round(sum(1 for r in rows if r.get("beat_12m")) / n, 4) if n else None,
            "pooled_excess_12m": round(sum(r["ret_12m"] - r["p_ret_12m"] for r in rows) / n, 6) if n else None,
        }
    return out


def assign_corps(stats):
    """Frozen rule (prereg s3): passing segments by beat_rate_12m>=0.50 & n>=30;
    corps = argmax beat_rate (tie -> pooled excess); blowup veto overrides."""
    passing = [s for s, v in stats.items()
               if v["n_startpoints"] >= MIN_N and v["beat_rate_12m"] is not None
               and v["beat_rate_12m"] >= BEAT_RATE_LINE]
    worst = min((v["worst_dd_all_windows"] for v in stats.values()
                 if v["worst_dd_all_windows"] is not None), default=None)
    no_blowup = worst is not None and worst >= BLOWUP_LINE
    if not no_blowup:
        return {"corps": "blowup-veto", "basis": f"worst_dd {worst} < {BLOWUP_LINE}",
                "passing_segments": sorted(passing), "no_blowup": False}
    if not passing:
        return {"corps": "no-dominant-segment",
                "basis": f"no segment with beat_rate_12m>={BEAT_RATE_LINE} AND n>={MIN_N}",
                "passing_segments": [], "no_blowup": True}
    best = max(passing, key=lambda s: (stats[s]["beat_rate_12m"], stats[s]["pooled_excess_12m"]))
    return {"corps": SEG_TO_CORPS.get(best, "unmapped-segment"),
            "basis": f"argmax beat_rate_12m={stats[best]['beat_rate_12m']} on segment {best} "
                     f"(n={stats[best]['n_startpoints']}, excess={stats[best]['pooled_excess_12m']})",
            "passing_segments": sorted(passing), "no_blowup": True, "best_segment": best}


def data_gates(cells_b, cells_x, pool, g2_files):
    errs = []
    if len(cells_b) != 7530 or len(cells_x) != 7530:
        errs.append(f"cells line counts {len(cells_b)}/{len(cells_x)} != 7530/7530")
    traders = {c["trader"] for c in cells_b}
    if len(traders) != 6:
        errs.append(f"registered traders {len(traders)} != 6")
    if len(pool.get("candidates", [])) != 22:
        errs.append(f"pool candidates {len(pool.get('candidates', []))} != 22")
    if len(g2_files) != 22:
        errs.append(f"g2 packs {len(g2_files)} != 22")
    return errs


def _pool_lookup(by_name, name, exit_r):
    """Exact (name, exit_regime) join, then underscore-variant fallback
    (pool 'oversold_bounce_20_15' vs entry_key fn 'oversold_bounce')."""
    c = by_name.get((name, exit_r))
    if c is not None:
        return c
    for (pn, pe), cand in by_name.items():
        if pe == exit_r and (pn.startswith(name + "_") or name.startswith(pn + "_")):
            return cand
    return None


def build_prospect_rows(pool, g2_packs):
    by_name = {}
    for c in pool["candidates"]:
        by_name[(c["name"], c.get("exit_regime"))] = c
    rows = []
    for pack in g2_packs:
        name = pack["entry_key"].split("(")[0]
        exit_r = pack.get("exit_regime")
        cand = _pool_lookup(by_name, name, exit_r)
        corps = FAMILY_CORPS_MAP.get(name, "pending-classification")
        worst_year = pack.get("worst_year")
        rec_dd = cand["recorded_max_dd"] if cand else None
        no_blowup = (rec_dd is not None and rec_dd >= BLOWUP_LINE
                     and worst_year is not None and worst_year >= BLOWUP_LINE)
        rows.append({
            "member": pack["member"],
            "strategy": name,
            "family": pack.get("family"),
            "exit_regime": exit_r,
            "candidate_corps": corps,
            "mapping_source": ("O-20260924-2012 s3 CEO-named list" if name in FAMILY_CORPS_MAP
                               else "pending-classification (not in CEO-named lists; honest)"),
            "status": "candidate",
            "segment_evidence": "absent (T-22 covered registered only; awaits d2 G1' wave + segment batches)",
            "no_blowup": no_blowup,
            "evidence": {
                "g2_neighborhood_pass": pack.get("neighborhood_pass"),
                "g2_cost_x3_pass": pack.get("cost_x3_pass"),
                "g2_per_year_pass": pack.get("per_year_pass"),
                "g2_worst_year": worst_year,
                "recorded_oos_sharpe": cand["recorded_oos_sharpe"] if cand else None,
                "recorded_x2_full_sharpe": cand["recorded_x2_full_sharpe"] if cand else None,
                "recorded_oos_trades": cand["recorded_oos_trades"] if cand else None,
                "recorded_max_dd": rec_dd,
            },
        })
    return rows


def now_iso():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def run():
    base_p = os.path.join(T22_DIR, "cells_legacy_base_c1.jsonl")
    x2_p = os.path.join(T22_DIR, "cells_legacy_x2_c1.jsonl")
    if not (os.path.exists(base_p) and os.path.exists(x2_p) and os.path.exists(POOL_PATH)):
        print("[t33] DATA GATE RED: missing source files", file=sys.stderr)
        return 2
    cells_b, cells_x = load_cells(base_p), load_cells(x2_p)
    pool = json.load(open(POOL_PATH, encoding="utf-8"))
    g2_files = sorted(f for f in os.listdir(G2_DIR) if f.startswith("PROS-") and f.endswith(".json"))
    errs = data_gates(cells_b, cells_x, pool, g2_files)
    if errs:
        for e in errs:
            print(f"[t33] DATA GATE RED: {e}", file=sys.stderr)
        return 2

    traders = sorted({c["trader"] for c in cells_b})
    registered = []
    for t in traders:
        tb = [c for c in cells_b if c["trader"] == t]
        tx = [c for c in cells_x if c["trader"] == t]
        stats = segment_stats(tb)
        asg = assign_corps(stats)
        eps = episode_blocks(tb)
        for seg, v in stats.items():
            v["n_episode_blocks"] = eps.get(seg, 0)
        registered.append({
            "member": t,
            "tier": "registered",
            "style_note": "registered defensive/reversal cohort (T-33 ticket note, O-1600 bear-segment evidence)",
            "segments": stats,
            "x2_face_disclosure": x2_face_disclosure(tx),
            "no_blowup": asg["no_blowup"],
            "corps": asg["corps"],
            "assignment_basis": asg["basis"],
            "passing_segments": asg["passing_segments"],
        })

    g2_packs = [json.load(open(os.path.join(G2_DIR, f), encoding="utf-8")) for f in g2_files]
    prospect = build_prospect_rows(pool, g2_packs)

    reg_counts = {}
    for r in registered:
        reg_counts[r["corps"]] = reg_counts.get(r["corps"], 0) + 1
    pros_counts = {}
    for p in prospect:
        pros_counts[p["candidate_corps"]] = pros_counts.get(p["candidate_corps"], 0) + 1

    prereg_sha = hashlib.sha256(open(PREREG_PATH, "rb").read()).hexdigest()[:16]
    payload = {
        "evidence_cutoff": EVIDENCE_CUTOFF,  # science_gates.cutoff_meta (C2 key)
        "batch": "T33_CORPS_ROSTER",
        "ticket": "T-2026-09-24-33",
        "generated": now_iso(),
        "prereg": "research/T33_CORPS_ROSTER.md",
        "prereg_sha256_16": prereg_sha,
        "rule": {"beat_rate_12m_line": BEAT_RATE_LINE, "min_n": MIN_N,
                 "blowup_line": BLOWUP_LINE, "face": "base", "primary_window": "12m",
                 "segmentation": "t22 regime_proxy (510300 vs MA200 disclosed proxy)",
                 "family_map": FAMILY_CORPS_MAP},
        "registered": registered,
        "prospect": prospect,
        "summary": {"n_members": len(registered) + len(prospect),
                    "registered_corps_counts": reg_counts,
                    "prospect_candidate_counts": pros_counts,
                    "assigned_total": sum(v for k, v in reg_counts.items() if k in SEG_TO_CORPS.values()),
                    "candidate_total": len(prospect)},
        "audit": {"ledger_trials_added": 0, "engine_runs": 0,
                  "source_batches": ["T22_VIRTUAL_TIMEPOINTS", "T24_G2_PACK"],
                  "note": "aggregation/labeling over recorded cells (t24_prospect_paper precedent); "
                          "source cells already ledgered by their batches; zero new trials"},
        "verdict": f"corps roster v1: registered {reg_counts} | prospect candidates {pros_counts} "
                   f"(assignment requires segment evidence per rule; PROSPECT = candidate-only)",
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"[t33] corps_roster.json written: {payload['summary']}")
    print(f"[t33] verdict: {payload['verdict']}")
    return 0


def selftest():
    import tempfile
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    # S1 wilson CI sanity
    lo, hi = wilson_ci(0, 10)
    check("S1 wilson k=0 n=10 -> [0, ~0.28]", lo == 0 and 0.25 < hi < 0.30)
    lo2, hi2 = wilson_ci(10, 10)
    check("S1 wilson k=10 n=10 -> hi=1", hi2 == 1.0 and lo2 > 0.7)

    # S2 assignment rule on synthetic natural-JSON-face fixtures
    def mk(trader, pos, regime, beat12, dd12=-0.1, trades=10, ret=0.02, pret=-0.01):
        return {"key": f"{trader}|{pos}", "trader": trader, "pos": pos, "start": "2021-01-15",
                "face": "base", "regime": regime, "n_listed": 46,
                "ret_6m": ret, "ret_12m": ret, "ret_24m": ret,
                "p_ret_6m": pret, "p_ret_12m": pret, "p_ret_24m": pret,
                "dd_6m": dd12, "dd_12m": dd12, "dd_24m": dd12,
                "sharpe_6m": 0.5, "sharpe_12m": 0.5, "sharpe_24m": 0.5,
                "trades_6m": trades, "trades_12m": trades, "trades_24m": trades,
                "beat_6m": beat12, "beat_12m": beat12, "beat_24m": beat12}

    def cells_for(name, n_bull_beat, n_bear_beat, n_bull=40, n_bear=40, n_chop=10, dd12=-0.1):
        cs = []
        pos = 0
        for i in range(n_bull):
            cs.append(mk(name, pos, "bull", i < n_bull_beat)); pos += 1
        for i in range(n_bear):
            cs.append(mk(name, pos, "bear", i < n_bear_beat)); pos += 1
        for i in range(n_chop):
            cs.append(mk(name, pos, "chop", False)); pos += 1
        if dd12 != -0.1 and cs:
            cs[-1]["dd_24m"] = dd12
        return cs

    t1 = cells_for("T1", n_bull_beat=10, n_bear_beat=32)   # bear 0.8 pass, bull 0.25 fail, chop n=10 fail
    a1 = assign_corps(segment_stats(t1))
    check("S2 T1 assigned defense via bear (0.8)", a1["corps"] == "defense" and a1["best_segment"] == "bear")
    t2 = cells_for("T2", n_bull_beat=18, n_bear_beat=15)  # 0.45/0.375 both fail
    a2 = assign_corps(segment_stats(t2))
    check("S2 T2 no-dominant-segment", a2["corps"] == "no-dominant-segment")
    t3 = cells_for("T3", n_bull_beat=5, n_bear_beat=30, dd12=-0.5)
    a3 = assign_corps(segment_stats(t3))
    check("S2 T3 blowup-veto (dd -0.5 < -0.35)", a3["corps"] == "blowup-veto" and a3["no_blowup"] is False)
    tie = cells_for("T4", n_bull_beat=20, n_bear_beat=20)  # both 0.5 pass -> tie-break excess equal -> bull first? rule: max by (rate, excess); equal -> max() picks first in dict order
    a4 = assign_corps(segment_stats(tie))
    check("S2 tie both-pass yields a corps", a4["corps"] in ("attack", "defense"))

    # natural JSON face roundtrip (r52 pitfall law)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "cells.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            for c in t1:
                f.write(json.dumps(c) + "\n")
        back = load_cells(p)
        check("S3 natural JSON face roundtrip", len(back) == len(t1) and back[0]["regime"] == "bull")

    # S4 family map (frozen CEO lists)
    check("S4 attack families 3", sum(1 for v in FAMILY_CORPS_MAP.values() if v == "attack") == 3)
    chop_fams = {"bb_squeeze_breakout", "doji_at_low", "hammer_reversal",
                 "three_methods_up", "oversold_bounce_20_15"}
    check("S4 chop families 5", all(FAMILY_CORPS_MAP.get(k) == CORPS_CHOP for k in chop_fams))
    check("S4 vol_breakout -> attack", FAMILY_CORPS_MAP["vol_breakout"] == "attack")
    check("S4 ma_converge_break not mapped (pending)", "ma_converge_break" not in FAMILY_CORPS_MAP)

    # S5 episode blocks
    eps = episode_blocks(t1[:5] + t1[45:47])  # 5 bull then 2 bear -> bull 1 block, bear 1 block
    check("S5 episode blocks bull=1 bear=1", eps["bull"] == 1 and eps["bear"] == 1)
    eps2 = episode_blocks(t1[:3] + t1[40:43] + [mk("T1", 100, "bull", False), mk("T1", 101, "bull", False)])
    check("S5 disjoint bull blocks = 2", eps2["bull"] == 2 and eps2["bear"] == 1)

    # S6 prospect join + corps map + no_blowup
    pool = {"candidates": [
        {"name": "vol_breakout", "exit_regime": "ce", "recorded_oos_sharpe": 1.267,
         "recorded_x2_full_sharpe": 0.2, "recorded_oos_trades": 41, "recorded_max_dd": -0.117},
        {"name": "ma_converge_break", "exit_regime": "ce", "recorded_oos_sharpe": 0.9,
         "recorded_x2_full_sharpe": 0.1, "recorded_oos_trades": 30, "recorded_max_dd": -0.11},
    ]}
    packs = [
        {"member": "PROS-VOB-CE-01", "family": "VOB", "exit_regime": "ce",
         "entry_key": "vol_breakout(20/1.5/20/10)", "worst_year": -0.04,
         "neighborhood_pass": False, "cost_x3_pass": False, "per_year_pass": True},
        {"member": "PROS-MCB-CE-01", "family": "MCB", "exit_regime": "ce",
         "entry_key": "ma_converge_break(20,60,2)", "worst_year": -0.5,
         "neighborhood_pass": True, "cost_x3_pass": True, "per_year_pass": True},
    ]
    rows = build_prospect_rows(pool, packs)
    check("S6 VOB -> attack candidate", rows[0]["candidate_corps"] == "attack" and rows[0]["status"] == "candidate")
    check("S6 VOB recorded join ok", rows[0]["evidence"]["recorded_oos_sharpe"] == 1.267)
    check("S6 MCB -> pending-classification", rows[1]["candidate_corps"] == "pending-classification")
    check("S6 MCB no_blowup False (worst_year -0.5)", rows[1]["no_blowup"] is False)
    check("S6 VOB no_blowup True", rows[0]["no_blowup"] is True)

    # S6b underscore-variant join (pool 'oversold_bounce_20_15' vs fn 'oversold_bounce')
    pool2 = {"candidates": [
        {"name": "oversold_bounce_20_15", "exit_regime": "ce", "recorded_oos_sharpe": 0.47,
         "recorded_x2_full_sharpe": 0.1, "recorded_oos_trades": 41, "recorded_max_dd": -0.05},
    ]}
    packs2 = [
        {"member": "PROS-OVB-CE-01", "family": "OVB", "exit_regime": "ce",
         "entry_key": "oversold_bounce(lookback=20, drop=-15%, shrink=0.8)",
         "worst_year": -0.02, "neighborhood_pass": True, "cost_x3_pass": True, "per_year_pass": True},
    ]
    rows2 = build_prospect_rows(pool2, packs2)
    check("S6b OVB underscore join -> chop candidate", rows2[0]["candidate_corps"] == "chop")
    check("S6b OVB evidence join non-null", rows2[0]["evidence"]["recorded_oos_sharpe"] == 0.47
          and rows2[0]["evidence"]["recorded_max_dd"] == -0.05)

    # S7 data gates red path
    check("S7 gates red on wrong counts", len(data_gates([], [], {"candidates": []}, [])) >= 3)

    n_pass = sum(1 for _, v in ok if v)
    print(f"selftest: {n_pass}/{len(ok)} {'ALL PASS' if n_pass == len(ok) else 'FAIL'}")
    return 0 if n_pass == len(ok) else 1


def main():
    ap = argparse.ArgumentParser(description="T-33 d1 corps roster batch")
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    return run() if a.cmd == "run" else selftest()


if __name__ == "__main__":
    sys.exit(main())
