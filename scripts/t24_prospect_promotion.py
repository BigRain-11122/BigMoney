"""T-24 slice (b): PROSPECT->INTERN promotion gate evaluator (read-only).

hr.PROSPECT_PROMOTION_GATE verbatim (firm/hr.py): promotion requires
full G2 (neighborhood + cost x2/x3 + per-year) AND the T-22 virtual-
timepoint mass batch beat_rate_6m >= 0.70 (O-20260924-1532, P-5/P-5B
frozen caliber). This evaluator ASSEMBLES the evidence pack per member
and emits an honest verdict; it NEVER writes member files (promotion
execution stays a separate registration-pipeline step -- hr always
HOLDs PROSPECT) and never touches results/paper/.

Legs:
  1 paper_months    >= 1 (hr ladder precondition, mirror of
                    INTERN_TO_TRAINEE paper_months_min; months come
                    from the slice-a tracking lane t24_prospect_paper)
  2 g2_full        onboarding recorded legs (backtest full/out_sample/
                    cost_x2) AND the G2 evidence pack
                    results/prospect_g2/<ID>.json with neighborhood_pass +
                    cost_x3_pass + per_year_pass (produced by the G2
                    pack batch under its own prereg; missing = honest
                    leg fail, never blocking evidence collection)
  3 t22_beat       beat_rate_6m >= 0.70 from results/t22/*.jsonl cells
                    (base face gates; x2 face disclosed). T-22 grid
                    currently covers the registered 6 only -- PROSPECT
                    timepoint sharding is pending (T-26 first-job pack),
                    so zero rows = honest leg fail "no_evidence".

Usage:
  python scripts/t24_prospect_promotion.py run       # all PROSPECT members
  python scripts/t24_prospect_promotion.py status    # last summary
  python scripts/t24_prospect_promotion.py selftest  # offline gates
Exit contract: 0 = evaluation ran (all-NOT-ELIGIBLE is a VALID verdict);
2 = mechanism error (no PROSPECT roster / unreadable member file).
Zero engine runs, ledger_trials_added=0 (evidence aggregation only).
"""
import argparse
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

OUT_DIR = os.path.join(PATHS.results_dir, "prospect_promotion")
G2_DIR = os.path.join(PATHS.results_dir, "prospect_g2")
T22_DIR = os.path.join(PATHS.results_dir, "t22")
SUMMARY_PATH = os.path.join(OUT_DIR, "_summary.json")
TICKET = "T-2026-09-24-24"

BEAT_RATE_MIN = 0.70          # O-20260924-1532 frozen caliber (P-5/P-5B)
G2_PACK_SUBLEGS = ("neighborhood_pass", "cost_x3_pass", "per_year_pass")


def _load_prospects(traders_dir) -> list:
    out = []
    for f in sorted(os.listdir(traders_dir)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        with open(os.path.join(traders_dir, f), encoding="utf-8") as fh:
            t = json.load(fh)
        if t.get("level") == "PROSPECT":
            out.append(t)
    return out


def _beat_stats(t22_dir: str, trader_id: str) -> dict:
    """Per-face beat-passive stats from T-22 virtual-timepoint cells.
    Gate face = base; x2 disclosed when rows exist. Zero rows -> None
    rates (honest no_evidence, never fabricated)."""
    stats = {}
    if not os.path.isdir(t22_dir):
        return {"faces": {}, "n_rows": 0}
    for f in sorted(os.listdir(t22_dir)):
        if not f.endswith(".jsonl"):
            continue
        face = "x2" if "x2" in f else "base"
        acc = stats.setdefault(face, {"n": 0, "beat": 0})
        with open(os.path.join(t22_dir, f), encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    c = json.loads(line)
                except json.JSONDecodeError:
                    continue   # corrupt tail tolerated
                if c.get("trader") != trader_id:
                    continue
                acc["n"] += 1
                if c.get("beat_6m"):
                    acc["beat"] += 1
    faces = {}
    n_rows = 0
    for face, acc in stats.items():
        n_rows += acc["n"]
        if acc["n"]:
            faces[face] = {"beat_rate_6m": round(acc["beat"] / acc["n"], 4),
                           "n_timepoints": acc["n"]}
    return {"faces": faces, "n_rows": n_rows}


def _g2_pack(g2_dir: str, tid: str) -> dict:
    """G2 evidence pack (neighborhood/cost_x3/per_year) written by the
    prereg'd G2 pack batch. Missing file = honest pack_missing."""
    p = os.path.join(g2_dir, f"{tid}.json")
    if not os.path.exists(p):
        return {"pack": None, "status": "pack_missing"}
    try:
        with open(p, encoding="utf-8") as fh:
            pack = json.load(fh)
    except (OSError, ValueError):
        return {"pack": None, "status": "pack_invalid"}
    sub = {k: bool(pack.get(k)) for k in G2_PACK_SUBLEGS}
    ok3 = all(sub.values())
    return {"pack": pack, "status": "pass" if ok3 else "subleg_fail",
            "sublegs": sub}


def _evaluate(t: dict, beat: dict, g2: dict, paper_months_min: int) -> dict:
    """Three-leg gate; eligible only when every leg passes (spec: no
    relaxation, promotion standards NOT relaxed)."""
    months = int(t.get("paper", {}).get("months_tracked") or 0)
    leg_paper = {"required": paper_months_min, "actual": months,
                 "pass": months >= paper_months_min}
    bt = t.get("backtest", {})
    base_legs_ok = all([
        bt.get("full", {}).get("sharpe") is not None,
        bt.get("out_sample", {}).get("sharpe") is not None,
        bt.get("cost_x2", {}).get("full_sharpe") is not None,
    ])
    g2_pass = base_legs_ok and g2["status"] == "pass"
    leg_g2 = {"onboarding_legs_pass": base_legs_ok,
              "pack_status": g2["status"],
              "sublegs": g2.get("sublegs"),
              "pass": g2_pass}
    base_face = beat["faces"].get("base")
    rate = base_face["beat_rate_6m"] if base_face else None
    leg_t22 = {"beat_rate_6m": rate,
               "required": BEAT_RATE_MIN,
               "n_timepoints": base_face["n_timepoints"] if base_face else 0,
               "x2_face": beat["faces"].get("x2"),
               "pass": bool(base_face
                            and base_face["beat_rate_6m"] >= BEAT_RATE_MIN)}
    legs = {"paper_months": leg_paper, "g2_full": leg_g2,
            "t22_beat_passive": leg_t22}
    return {"trader": t["id"], "eligible": all(l["pass"] for l in
                                               legs.values()),
            "legs": legs}


def _run_eval(members: list, traders_dir: str, t22_dir: str, g2_dir: str,
              out_dir: str, paper_months_min: int) -> tuple:
    os.makedirs(out_dir, exist_ok=True)
    verdicts = []
    leg_pass = {"paper_months": 0, "g2_full": 0, "t22_beat_passive": 0}
    cutoff = ""
    for t in members:
        c = t.get("evidence_cutoff") or ""
        cutoff = max(cutoff, c)
        beat = _beat_stats(t22_dir, t["id"])
        g2 = _g2_pack(g2_dir, t["id"])
        v = _evaluate(t, beat, g2, paper_months_min)
        verdicts.append(v)
        for k in leg_pass:
            if v["legs"][k]["pass"]:
                leg_pass[k] += 1
        with open(os.path.join(out_dir, f"{t['id']}.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(v, fh, indent=2, ensure_ascii=False)
        print(f"{t['id']}: eligible={v['eligible']} "
              f"(paper={v['legs']['paper_months']['actual']}m "
              f"g2_pack={g2['status']} "
              f"t22_rows={beat['n_rows']})")
    n_eligible = sum(1 for v in verdicts if v["eligible"])
    summary = {
        "batch": "t24-prospect-promotion-gate",
        "ticket": TICKET,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "evidence_cutoff": cutoff or None,
        "n_members": len(members), "n_eligible": n_eligible,
        "leg_pass": leg_pass,
        "gate": {"g2_full": "G2 neighborhood + cost x2/x3 + per-year "
                           "(frozen, no relaxation)",
                 "t22_beat_passive": f"beat_rate_6m >= {BEAT_RATE_MIN} "
                                     "(O-20260924-1532 P-5/P-5B)",
                 "paper_months_min": paper_months_min},
        "read_only": True,
        "audit": {"ledger_trials_added": 0, "engine_runs": 0,
                  "note": "evidence aggregation only; promotion execution "
                          "is a separate registration-pipeline step"},
        "verdict": ("none eligible (honest -- legs fill as evidence "
                    "lands: paper months accumulate from first new bar, "
                    "G2 pack batch + T-22 PROSPECT sharding pending)"
                    if n_eligible == 0 else
                    f"{n_eligible} eligible -> registration pipeline"),
    }
    with open(os.path.join(out_dir, "_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    print(f"promotion gate: eligible={n_eligible}/{len(members)} "
          f"legs_pass={leg_pass} cutoff={cutoff or 'n/a'}")
    return summary, 0


def cmd_run() -> int:
    from firm.hr import TRADERS_DIR, THRESHOLDS
    members = _load_prospects(TRADERS_DIR)
    if not members:
        print("promotion gate: 0 PROSPECT members (mechanism error, rc 2)")
        return 2
    paper_min = THRESHOLDS["INTERN_TO_TRAINEE"]["paper_months_min"]
    _run_eval(members, TRADERS_DIR, T22_DIR, G2_DIR, OUT_DIR, paper_min)
    return 0


def cmd_status() -> int:
    if os.path.exists(SUMMARY_PATH):
        with open(SUMMARY_PATH, encoding="utf-8") as fh:
            s = json.load(fh)
        print(json.dumps({k: s.get(k) for k in ("generated",
                                                "evidence_cutoff",
                                                "n_members", "n_eligible",
                                                "leg_pass")},
                         ensure_ascii=False))
    else:
        print("no promotion-gate summary yet")
    return 0


def _ok(name: str, cond: bool, detail: str = "") -> bool:
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}"
          + (f" | {detail}" if detail else ""))
    return cond


def _member(tid: str, months: int, cutoff: str = "2026-09-22") -> dict:
    return {"id": tid, "level": "PROSPECT", "evidence_cutoff": cutoff,
            "backtest": {"full": {"sharpe": 0.4}, "out_sample":
                         {"sharpe": 0.5}, "cost_x2": {"full_sharpe": 0.2}},
            "paper": {"months_tracked": months}}


def _write_trader(d: str, t: dict) -> None:
    with open(os.path.join(d, f"{t['id']}.json"), "w",
              encoding="utf-8") as fh:
        json.dump(t, fh)


def cmd_selftest() -> int:
    print("== t24_prospect_promotion selftest ==")
    tmp = tempfile.mkdtemp(prefix="t24promo_")
    traders = os.path.join(tmp, "traders")
    t22 = os.path.join(tmp, "t22")
    g2 = os.path.join(tmp, "prospect_g2")
    out = os.path.join(tmp, "out")
    os.makedirs(traders), os.makedirs(t22), os.makedirs(g2)
    # T-22 cells: PROS-ELG beats 7/10 (base) + 8/10 (x2); PROS-LOW 3/10
    with open(os.path.join(t22, "cells_base_test.jsonl"), "w",
              encoding="utf-8") as fh:
        for i in range(10):
            fh.write(json.dumps({"trader": "PROS-ELG-01", "pos": i,
                                 "beat_6m": i < 7}) + "\n")
        for i in range(10):
            fh.write(json.dumps({"trader": "PROS-LOW-01", "pos": i,
                                 "beat_6m": i < 3}) + "\n")
    with open(os.path.join(t22, "cells_x2_test.jsonl"), "w",
              encoding="utf-8") as fh:
        for i in range(10):
            fh.write(json.dumps({"trader": "PROS-ELG-01", "pos": i,
                                 "beat_6m": i < 8}) + "\n")
    # G2 pack for the eligible member only
    with open(os.path.join(g2, "PROS-ELG-01.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"neighborhood_pass": True, "cost_x3_pass": True,
                   "per_year_pass": True}, fh)

    all_ok = True
    # S1 full-evidence member promotes eligible=True
    m1 = _member("PROS-ELG-01", months=2)
    _write_trader(traders, m1)
    v = _evaluate(m1, _beat_stats(t22, "PROS-ELG-01"),
                  _g2_pack(g2, "PROS-ELG-01"), paper_months_min=1)
    all_ok &= _ok("S1 all-legs member -> eligible", v["eligible"] is True,
                  str({k: v['legs'][k]['pass'] for k in v['legs']}))
    # S2 paper-months gate blocks (months=0)
    m0 = _member("PROS-ELG-01", months=0)
    v0 = _evaluate(m0, _beat_stats(t22, "PROS-ELG-01"),
                   _g2_pack(g2, "PROS-ELG-01"), 1)
    all_ok &= _ok("S2 months=0 blocks promotion",
                  v0["eligible"] is False
                  and v0["legs"]["paper_months"]["pass"] is False)
    # S3 G2 pack missing -> honest leg fail
    m2 = _member("PROS-NOPACK-01", months=2)
    v2 = _evaluate(m2, _beat_stats(t22, "PROS-NOPACK-01"),
                   _g2_pack(g2, "PROS-NOPACK-01"), 1)
    all_ok &= _ok("S3 g2 pack_missing -> leg fail",
                  v2["eligible"] is False
                  and v2["legs"]["g2_full"]["pack_status"] == "pack_missing")
    # S4 no T-22 rows -> honest no_evidence
    all_ok &= _ok("S4 t22 zero rows -> leg fail",
                  v2["legs"]["t22_beat_passive"]["pass"] is False
                  and v2["legs"]["t22_beat_passive"]["beat_rate_6m"] is None)
    # S5 beat rate arithmetic + 0.70 boundary (7/10 = 0.70 passes)
    b = _beat_stats(t22, "PROS-ELG-01")
    all_ok &= _ok("S5 beat arithmetic (base 0.7 gate-pass, x2 disclosed)",
                  b["faces"]["base"]["beat_rate_6m"] == 0.7
                  and b["faces"]["x2"]["beat_rate_6m"] == 0.8)
    bl = _evaluate(m1, _beat_stats(t22, "PROS-LOW-01"),
                   _g2_pack(g2, "PROS-ELG-01"), 1)
    all_ok &= _ok("S6 rate 0.3 < 0.70 -> leg fail",
                  bl["legs"]["t22_beat_passive"]["pass"] is False)
    # S7 read-only contract: run_eval leaves member files byte-identical
    before = open(os.path.join(traders, "PROS-ELG-01.json"),
                  "rb").read()
    s, rc = _run_eval([m1], traders, t22, g2, out, 1)
    after = open(os.path.join(traders, "PROS-ELG-01.json"), "rb").read()
    all_ok &= _ok("S7 read-only (member file byte-identical)",
                  before == after and s["n_eligible"] == 1 and rc == 0)
    # S8 subleg partial pack -> subleg_fail (no relaxation)
    with open(os.path.join(g2, "PROS-ELG-01.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"neighborhood_pass": True, "cost_x3_pass": False,
                   "per_year_pass": True}, fh)
    vp = _evaluate(m1, _beat_stats(t22, "PROS-ELG-01"),
                   _g2_pack(g2, "PROS-ELG-01"), 1)
    all_ok &= _ok("S8 partial G2 pack -> subleg_fail blocks",
                  vp["eligible"] is False
                  and vp["legs"]["g2_full"]["pack_status"] == "subleg_fail")
    print(f"== selftest {'ALL PASS' if all_ok else 'FAIL'} ==")
    return 0 if all_ok else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "status", "selftest"])
    a = ap.parse_args()
    return {"run": cmd_run, "status": cmd_status,
            "selftest": cmd_selftest}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())
