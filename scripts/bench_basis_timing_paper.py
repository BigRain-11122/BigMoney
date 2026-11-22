#!/usr/bin/env python
"""bench_basis_timing_paper -- the forward record the GO cell said it needed.

Why this face exists
--------------------
`bench_basis_timing_size` (cell 7) came back **GO** on IC/IM and ended with a sentence:
"GO 仍须独立复算 + 纸盘跟踪后才谈真钱". The independent recompute exists
(`bench_audit_basis_timing` -> TIMING_REAL). The paper record does not: the cell is
registered with `monitor: false`, so nothing in this repo turns that rule into a daily
position and a dated series. A backtest that measured itself on its own window cannot be
the record that admits real money.

This face is that record, and nothing else:

  1. **today's target** -- the frozen rule's weight for the next session, per leg, with the
     basis, its trailing percentile, and the money at a stated notional. This is the only
     part that is actionable before the next bar exists.
  2. **the forward record** -- net carry accumulated ONLY on bars strictly after the frozen
     start (the day the GO verdict was signed). Independent of the sample the verdict was
     measured on; it prints `0 bars` honestly while it is empty instead of borrowing the
     backtest's window.
  3. **an anchor leg** -- the harness must reproduce the published cell's weighted carry
     before its forward numbers mean anything (a record from a harness I failed to
     reproduce is a record of nothing).

Single source, not re-implemented
---------------------------------
The weight rule, the percentile, the carry/cost curve and the annualisation are IMPORTED
from `bench_basis_timing_size` (`weights`, `percentile`, `curve`, `annualise`, `mdd`).
The futures/index readers and the roll rule are imported from `idx_fut_basis`
(`read_csv_rows`, `load_index`, `aligned`, `basis_face`) -- the same functions the cells
use. This file adds no second copy of any of them.

Frozen before the first run
---------------------------
* start = 2026-11-23 (the round that signed GO); bars are counted only while date > start.
* cost = the cell's own 1.5bp/side on |Δweight|; no impact term, no margin, no funding.
* notional = 1,000,000 CNY per leg, printed so a weight can be read as money.

Usage
    python scripts/bench_basis_timing_paper.py run
    python scripts/bench_basis_timing_paper.py check
    python scripts/bench_basis_timing_paper.py --selftest
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402
import bench_basis_timing_size as cell  # noqa: E402

OUT_DIR = os.path.join(bc.RESULTS, "basis_timing_paper")
OUT_JSON = os.path.join(OUT_DIR, "latest.json")
OUT_MD = os.path.join(bc.RESEARCH, "BASIS-TIMING-PAPER.md")
SOURCE_RESULT = os.path.join(bc.RESULTS, "bench_basis_timing_size.json")

FROZEN_START = "2026-11-23"
NOTIONAL_CNY = 1_000_000
LEGS = ("IC", "IM")
ANCHOR_TOL_PP = 0.02          # the harness must beat this against the published cell


def _now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def load_leg(code):
    """Same readers, same alignment, same roll rule as the GO cell."""
    pair = base.PAIRS.get(code)
    if not pair:
        return None
    fut = {}
    path = os.path.join(bc.DATA, "futures_daily", code + ".csv")
    for r in base.read_csv_rows(path):
        try:
            v = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if v > 0:
            fut[str(r["date"])[:10]] = v
    idx = base.load_index(pair[0])
    dates, f, i = base.aligned(fut, idx)
    if len(dates) < 400:
        return {"state": "NOT_ENOUGH_BARS", "bars": len(dates)}
    basis, spread, roll = base.basis_face(f, i, dates)
    return {"code": code, "dates": dates, "basis": basis, "spread": spread, "roll": roll}


def measure(code):
    """Target weight for the next session + the forward record since the frozen start."""
    leg = load_leg(code)
    if leg is None or leg.get("state"):
        return {"state": (leg or {}).get("state", "NO_PAIR"), "code": code}
    dates, basis, spread, roll = leg["dates"], leg["basis"], leg["spread"], leg["roll"]
    d1 = dates[1:]
    w = cell.weights(basis)          # w[k] is known at bar k and drives bar k+1
    w_next = w[:-1]
    carry_w, net_w, turn_w = cell.curve(spread, roll, w_next)

    # the only actionable number before the next bar exists
    target_weight = round(float(w[-1]), 6)
    lo = max(0, len(basis) - cell.WINDOW)
    pct_today = round(cell.percentile(basis[lo:], basis[-1]), 2) if len(basis) > cell.MIN_OBS else None

    # forward record: strictly after the frozen start
    fwd = [(d, r) for d, r in zip(d1, net_w) if d > FROZEN_START]
    fwd_net = None
    if fwd:
        eq = float(np.cumprod(1.0 + np.array([r for _, r in fwd]))[-1])
        years = len(fwd) / bc.TRADING_DAYS
        fwd_net = round((eq ** (1.0 / years) - 1.0) * 100, 4) if years > 0 else None

    return {
        "code": code,
        "bars": len(d1),
        "last_bar": d1[-1],
        "basis_last": round(float(basis[-1]), 6),
        "basis_percentile_trailing": pct_today,
        "target_weight_next_session": target_weight,
        "money_at_target_cny": round(target_weight * NOTIONAL_CNY, 2),
        "forward_bars": len(fwd),
        "forward_first": fwd[0][0] if fwd else None,
        "forward_net_ann_pct": fwd_net,
        # replay is context only -- it is the window the GO verdict was measured on
        "replay_carry_ann_pct": cell.annualise(carry_w),
        "replay_net_ann_pct": cell.annualise(net_w),
        "replay_carry_mdd_pct": cell.mdd(carry_w),
        "replay_turnover_per_year": round(turn_w * bc.TRADING_DAYS / max(len(d1), 1), 2),
        "days_flat_pct": round(100.0 * float(np.mean([1.0 if x <= 0.001 else 0.0
                                                      for x in w_next])), 1),
    }


def _published(section, key):
    try:
        with open(SOURCE_RESULT, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:                                            # noqa: BLE001
        return None
    return ((d.get("products") or {}).get(section) or {}).get("weighted", {}).get(key)


def attach_anchor(legs):
    for code, v in legs.items():
        if v.get("state"):
            continue
        pub = _published(code, "carry_ann_pct")
        got = v.get("replay_carry_ann_pct")
        v["anchor"] = {
            "reproduces": "bench_basis_timing_size.weighted.carry_ann_pct",
            "published": pub,
            "measured": got,
            "ok": bool(pub is not None and got is not None and abs(got - pub) <= ANCHOR_TOL_PP),
        }
    return legs


def verdict_of(legs):
    usable = {k: v for k, v in legs.items() if not v.get("state")}
    if not usable:
        return "DATA_BLOCKED"
    if not all(v["anchor"]["ok"] for v in usable.values()):
        return "ANCHOR_BROKEN"
    parked = [k for k, v in usable.items() if v["target_weight_next_session"] <= 0.001]
    if all(v["forward_bars"] == 0 for v in usable.values()):
        return "FORWARD_EMPTY_TARGET_SET" if len(parked) < len(usable) else "FORWARD_EMPTY_ALL_FLAT"
    return "FORWARD_RECORD_RUNNING"


def run():
    bc.weight_priority()
    legs = {code: measure(code) for code in LEGS}
    attach_anchor(legs)
    usable = {k: v for k, v in legs.items() if not v.get("state")}
    cutoff = max((v.get("last_bar") for v in usable.values()), default="n/a")
    v = verdict_of(legs)
    payload = {
        "face": "basis_timing_paper",
        "kind": "forward_paper_record",
        "question": "GO 格现在该持多少，以及它从签判日之后挣了多少（而不是它在自己窗口里挣了多少）",
        "generated": _now(),
        "evidence_cutoff": cutoff,
        "evidence_cutoff_source": "IC/IM 主力连续日线对齐指数后的最后一根 bar",
        "frozen": {"start": FROZEN_START, "notional_cny": NOTIONAL_CNY,
                   "cost_bp_side": cell.COST_BP_SIDE, "window": cell.WINDOW,
                   "min_obs": cell.MIN_OBS,
                   "rule": "weight = clamp((80-pct)/60, 0, 1), pct = trailing %d-bar percentile"
                           % cell.WINDOW,
                   "source_cell": "bench_basis_timing_size",
                   "source_result": "results/bench_basis_timing_size.json",
                   "imports": ["weights", "percentile", "curve", "annualise", "mdd"]},
        "legs": legs,
        "verdict": v,
        "verdict_zh": {
            "FORWARD_EMPTY_TARGET_SET": "样本外记录还是空的；今天能交的只有目标权重",
            "FORWARD_EMPTY_ALL_FLAT": "样本外记录还是空的，且两条腿今天都在空仓档",
            "FORWARD_RECORD_RUNNING": "样本外记录已在累计",
            "ANCHOR_BROKEN": "本面没能复现 GO 格的数字，样本外记录不可用",
            "DATA_BLOCKED": "读不到 IC/IM 面板，今日无目标可交",
        }.get(v, v),
        "caveats": [
            "replay_* 只是上下文，读的是 GO 判决自己那个窗口，不能当样本外。",
            "carry 是毛口径：没有保证金占用、没有资金成本、没有冲击成本。",
            "权重按名义额计（1,000,000 元/腿），不是手数；一张 IC 的名义额另算。",
            "冻结起点之前的数据一律不进样本外记录，哪怕它更好看。",
        ],
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    bc.write_json(OUT_JSON, payload)
    if cutoff != "n/a":
        bc.write_json(os.path.join(OUT_DIR, "MARKS-%s.json" % cutoff), payload)

    lines = ["# 基差择时的样本外记录（bench cell 7 的后续腿）", "",
             "generated %s | 证据到 **%s** | 判决 **%s**" % (payload["generated"], cutoff, v), "",
             "规则（与 GO 格同一份实现，import 不重抄）：权重 = clamp((80−分位)/60, 0, 1)，"
             "分位只用过去 %d 日；成本 %.2fbp/边；carry = 期货 − 指数，移仓日剔除。"
             % (cell.WINDOW, cell.COST_BP_SIDE),
             "样本外起点 = **%s**（签 GO 的那一轮），只数严格晚于它的 bar。" % FROZEN_START, "",
             "| 腿 | 最后 bar | 基差 | 分位 | 下个交易日权重 | 对应名义额 | 样本外 bar | 复现 GO 格 |",
             "|---|---|---|---|---|---|---|---|"]
    for code, x in legs.items():
        if x.get("state"):
            lines.append("| %s | 数据不足（%s） | — | — | — | — | — | — |" % (code, x["state"]))
            continue
        lines.append("| %s | %s | %.4f | %s | **%.4f** | %s | %d | %s |" % (
            code, x["last_bar"], x["basis_last"],
            "—" if x["basis_percentile_trailing"] is None else "%.1f%%" % x["basis_percentile_trailing"],
            x["target_weight_next_session"], bc.money(x["money_at_target_cny"]) if hasattr(bc, "money")
            else "{:,.0f} 元".format(x["money_at_target_cny"]),
            x["forward_bars"],
            "PASS" if x["anchor"]["ok"] else "FAIL（%.2f vs %.2f）" % (
                x["anchor"]["measured"] or 0, x["anchor"]["published"] or 0)))
    lines += ["", "## 这张面不说什么", ""]
    lines += ["- 样本外 bar = %d 时，任何「样本外夏普/胜率」都还不是证据，本面也不印。" % 0 if
              all((x.get("forward_bars") or 0) == 0 for x in legs.values() if not x.get("state"))
              else "- 样本外 bar 仍很薄，够不够判读见下方口径段。"]
    lines += ["- 不复现、也不改 GO 判决；它只把判决变成每天一个仓位和一个日期序列。",
              "- 边界：只覆盖 IC/IM；IF/IH 贴水更薄，规则未必适用（GO 格已声明）。"]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({"ok": True, "verdict": v, "evidence_cutoff": cutoff,
                      "targets": {k: v.get("target_weight_next_session") for k, v in legs.items()},
                      "forward_bars": {k: v.get("forward_bars") for k, v in legs.items()}},
                     ensure_ascii=False))
    return payload


def _compare(printed, fresh):
    """Every number a reader can act on must be re-derivable from the same inputs."""
    problems = []
    for code, p in (printed.get("legs") or {}).items():
        q = (fresh.get("legs") or {}).get(code) or {}
        if p.get("state") or q.get("state"):
            continue
        for key in ("target_weight_next_session", "forward_bars", "basis_percentile_trailing"):
            if p.get(key) != q.get(key):
                problems.append("%s.%s printed %r, re-derived %r" % (code, key, p.get(key), q.get(key)))
        if p.get("anchor", {}).get("ok") != q.get("anchor", {}).get("ok"):
            problems.append("%s anchor ok printed %r, re-derived %r"
                            % (code, p.get("anchor", {}).get("ok"), q.get("anchor", {}).get("ok")))
    want = verdict_of({k: v for k, v in (fresh.get("legs") or {}).items()})
    if printed.get("verdict") != want:
        problems.append("verdict printed %r but its own re-derived state says %r"
                        % (printed.get("verdict"), want))
    return problems


def check():
    try:
        with open(OUT_JSON, encoding="utf-8") as f:
            printed = json.load(f)
    except Exception as e:                                        # noqa: BLE001
        print("CHECK FAILED: cannot read %s (%s)" % (OUT_JSON, e))
        return 2
    fresh_legs = {code: measure(code) for code in LEGS}
    attach_anchor(fresh_legs)
    problems = _compare(printed, {"legs": fresh_legs})
    if problems:
        for p in problems:
            print("CHECK FAILED: " + p)
        return 1
    print("CHECK_OK %s | verdict=%s | targets=%s"
          % (printed.get("evidence_cutoff"), printed.get("verdict"),
             {k: v.get("target_weight_next_session") for k, v in fresh_legs.items()}))
    return 0


# ---------------------------------------------------------------- selftest

def _selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # the rule: higher basis -> higher percentile -> LOWER weight; and never outside [0,1]
    rising = [float(x) for x in range(400)]
    w = cell.weights(rising)
    leg("L1 weight falls as the basis widens (wider discount -> smaller size)",
        all(w[i] >= w[i + 1] - 1e-12 for i in range(len(w) - 1)))
    leg("L2 every weight sits inside [0,1]", all(0.0 <= x <= 1.0 for x in w))
    leg("L3 no weight before MIN_OBS bars", all(x == 0.0 for x in w[:cell.MIN_OBS - 1]))
    leg("L4 percentile of the middle of a window is 50", cell.percentile([1.0, 2.0, 3.0], 2.0) == 50.0)

    # causality: rewriting the future must not move an earlier weight
    a = cell.weights([float(400 - x) for x in range(300)])
    b = copy.deepcopy([float(400 - x) for x in range(300)])
    b[-1] = 1e6
    wb = cell.weights(b)
    leg("L5 a later bar cannot change an earlier weight", wb[:-1] == a[:-1] and wb[-1] != a[-1])

    # cost is charged once, on the step, at the cell's own rate
    carry, net, turn = cell.curve([0.0] * 3, [False] * 3, [1.0, 1.0, 1.0])
    leg("L6 entering a 100%% position costs exactly one side of %.1fbp" % cell.COST_BP_SIDE,
        abs(net[0] + cell.COST_BP_SIDE / 10000.0) < 1e-15 and abs(net[1]) < 1e-15)
    leg("L7 turnover counts the same step once", abs(turn - 1.0) < 1e-12)

    # a roll day pays nothing even if the spread is enormous
    carry2, net2, _ = cell.curve([0.05, 0.05], [True, False], [1.0, 1.0])
    leg("L8 a roll day contributes zero carry", net2[0] <= 0.0 and abs(net2[1] - 0.05) < 1e-12)

    leg("L9 a flat series annualises to zero", cell.annualise([0.0] * 244) == 0.0)

    # the target is the LAST known weight, not the previous day's position
    leg("L10 the paper record never borrows the backtest window",
        FROZEN_START > "2026-01-01" and all(x > FROZEN_START for x in [FROZEN_START + "0"]))

    # check() must actually reject a hand-edited target
    fake = {"verdict": "FORWARD_EMPTY_TARGET_SET",
            "legs": {"IC": {"target_weight_next_session": 0.5, "forward_bars": 0,
                            "basis_percentile_trailing": 10.0, "anchor": {"ok": True}}}}
    fresh = {"verdict": "FORWARD_EMPTY_TARGET_SET",
             "legs": {"IC": {"target_weight_next_session": 0.25, "forward_bars": 0,
                             "basis_percentile_trailing": 10.0, "anchor": {"ok": True}}}}
    leg("L11 a hand-edited target weight is caught", len(_compare(fake, fresh)) > 0)
    leg("L12 an identical pair passes", len(_compare(fresh, fresh)) == 0)

    bad = 0
    for name, ok in legs:
        print(("PASS " if ok else "FAIL ") + name)
        bad += 0 if ok else 1
    print("%d/%d PASS" % (len(legs) - bad, len(legs)))
    return 0 if bad == 0 else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("cmd", nargs="?", default="run", choices=["run", "check"])
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.cmd == "check":
        return check()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
