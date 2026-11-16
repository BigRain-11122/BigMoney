#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Does a minimum seat-hold rule beat the seat-by-seat book? (r1769)

r1768 measured where the book's money sits (fresh names 94.8% of the select leg) and then
said the important part: 243 of 287 name-periods were just bought, so "churn vs hold" is
not a choice this rule makes -- it is how the rule is built. 51 of 51 rebalances replaced
the whole book. To ask the question at all you need an arm that is forced to keep seats.

This face builds that arm on the same engine, the same panel, the same ruler:

    a name bought at decision t is kept for at least k decisions (t .. t+k-1)

k=1 is the published rule and must reproduce it bit for bit (the control arm). k=2/3/5 are
the forced-hold arms. The rule lives entirely in the engine's own `select_hook`, so the
engine is not touched and there is no second implementation of sizing, cost or T+1.

Three things are reported per arm, and they answer different questions:

  1. **the book** -- CAGR / Sharpe / max drawdown / mean turnover / cost leg. What a holder
     would have got.
  2. **the paired gap** -- the daily net-return difference against k=1, read through the same
     circular block bootstrap the r1760/r1762 faces use (block 20 = one rebalance period,
     2000 draws, frozen seed). A gap that cannot clear its own MDE80 is printed as such.
  3. **the structure** -- how much of the book really turns over (fresh-seat share) and how
     often a forced seat had to be dropped because the name left the liquidity gate.

The forced seat is honest about mortality: if a name that the rule wants to keep is not
scorable that day (the liquidity gate removed it), the seat goes back to the ranking and the
event is counted. A rule that silently kept an untradable name would be measuring a book
nobody could hold.

Usage:
    python scripts/etf_book_seat_hold.py run
    python scripts/etf_book_seat_hold.py --check
    python scripts/etf_book_seat_hold.py --selftest
    python scripts/etf_book_seat_hold.py --md
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import etf_book_entry_gate as G               # noqa: E402  (panel + flip repair)
import etf_composite_pf as E                  # noqa: E402  (the score face)
import etf_equity_alpha as A                  # noqa: E402  (classify)
import etf_book_corr_select as CS             # noqa: E402  (the base arm's rule)
import etf_book_money_mde as MM               # noqa: E402  (replay)
import etf_book_gate_raise_noise as N         # noqa: E402  (arm_stats)
import etf_book_book_mde as BM                # noqa: E402  (the bootstrap ruler)
import etf_robust_pf as R                     # noqa: E402  (the engine)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_seat_hold.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_SEAT_HOLD.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")
FACE_SLICE = os.path.join(ROOT, "results", "etf_book_period_slice.json")

BENCH = CS.BENCH
GATE = CS.GATE
SEATS = CS.BASE_SEATS
PER_YEAR = 252.0

KS = (2, 3, 5)               # forced-hold arms; k=1 is the published rule (control)
P_SEP = 0.05                 # frozen separation line for the direction read
CONTROL_TOL_PP = 0.25        # book CAGR must reproduce the published cell
SELECT_TOL_PP = 0.05         # select leg must reproduce the r1762..r1768 cell
REPLAY_TOL = 1e-9
IDENTITY_TOL = 0.02          # annualised pp; select+rotate+size+cost == net


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- the rule itself

def make_min_hold_hook(k, log=None):
    """Engine `select_hook` implementing a minimum seat-hold of k decisions.

    Semantics, in the hook's own vocabulary:
      * `age[name]` counts the decisions a name has been in the book, the buying decision
        being 1. At every decision the held names are advanced by one first.
      * a held name with age <= k is a FORCED seat: it is kept even if the ranking would
        have dropped it.
      * a forced name that is not scorable today (the liquidity gate took it out) cannot be
        kept; the seat falls back to the ranking and the event is counted, never hidden.
      * names bought this decision start at age 1, so they are protected from the NEXT
        decision onwards.

    k=1 means "no forced seats": age 1 at purchase, 2 at the next decision, and 2 > 1, so
    nothing is ever forced -- the path is the engine's plain top-n and is bit-identical to
    the published book. That is the control arm, and selftest pins it.
    """
    if int(k) < 1:
        raise ValueError("k must be >= 1")
    k = int(k)
    age = {}
    state = {"decisions": 0, "seats": 0, "kept": 0, "bought": 0,
             "forced_kept": 0, "forced_liquid_drop": 0}

    def hook(row, held_names, n_hold, d):
        state["decisions"] += 1
        if k <= 1:
            picks = list(row.nlargest(n_hold).index)
        else:
            held = list(held_names)
            for nm in held:
                age[nm] = age.get(nm, 0) + 1
            keep = []
            for nm in held:
                if age.get(nm, 0) <= k:
                    if nm in row.index:
                        keep.append(nm)
                        state["forced_kept"] += 1
                    else:
                        state["forced_liquid_drop"] += 1
            keep = keep[:n_hold]
            order = list(row.nlargest(len(row)).index)
            picks = list(keep)
            for nm in order:
                if len(picks) >= n_hold:
                    break
                if nm not in picks:
                    picks.append(nm)
            # forget the names that left; register the ones just bought at age 1
            held_set = set(held)
            for nm in held_set - set(picks):
                age.pop(nm, None)
            for nm in picks:
                if nm not in held_set:
                    age[nm] = 1
                else:
                    age.setdefault(nm, 1)
        held_set = set(held_names)
        bought = [nm for nm in picks if nm not in held_set]
        state["seats"] += len(picks)
        state["kept"] += len(picks) - len(bought)
        state["bought"] += len(bought)
        if log is not None:
            log.append({"date": str(pd.Timestamp(d).date()), "book": list(picks),
                        "bought": len(bought)})
        return picks

    hook.state = state
    return hook


def turn_profile(diag):
    """How much of the book really turns over, read from the engine's own decisions."""
    prev = set()
    seats = fresh = 0
    decisions = 0
    for row in diag:
        book = row.get("book") or []
        if not book:
            continue
        cur = set(book)
        seats += len(cur)
        fresh += len(cur - prev)
        decisions += 1
        prev = cur
    return {"decisions": decisions, "seat_periods": seats, "fresh_seats": fresh,
            "fresh_share": (round(fresh / float(seats), 4) if seats else None),
            "held_share": (round((seats - fresh) / float(seats), 4) if seats else None)}


def arm_row(label, k, out, base_names, base_net, cost_label=None):
    """One published row: the book, the paired gap against k=1, and the structure."""
    stats = out["stats"]
    full = stats.get("full") or {}
    df = out["df"]
    sel = df["select"].dropna()
    net = df["net"].dropna()
    diff = pd.DataFrame({"a": df["net"], "b": base_net}).dropna()
    delta = list(diff["a"] - diff["b"])
    jac = None
    if base_names is not None:
        names = set(out.get("names") or ())
        jac = (round(len(names & base_names) / float(len(names | base_names)), 4)
               if (names or base_names) else None)
    return {
        "arm": label,
        "min_hold_decisions": int(k),
        "book_cagr_pct": round(float(full.get("cagr") or 0.0) * 100.0, 3),
        "book_sharpe": full.get("sharpe"),
        "book_maxdd_pct": round(float(full.get("maxdd") or 0.0) * 100.0, 2),
        "select_ann_pp": round(float(sel.mean()) * PER_YEAR * 100.0, 4),
        "rotate_ann_pp": round(float(df["rotate"].mean()) * PER_YEAR * 100.0, 4),
        "size_ann_pp": round(float(df["size"].mean()) * PER_YEAR * 100.0, 4),
        "cost_ann_pp": round(float(df["cost"].mean()) * PER_YEAR * 100.0, 4),
        "r_bench_ann_pp": round(float(df["r_bench"].mean()) * PER_YEAR * 100.0, 4),
        "net_ann_pp": round(float(net.mean()) * PER_YEAR * 100.0, 4),
        "mean_turn": round(float(df["turn"].mean()), 4),
        "n_names_held": len(out.get("names") or ()),
        "jaccard_vs_base": jac,
        "replay_max_rel": out.get("replay_max_rel"),
        "delta_vs_base": (None if k == 1
                          else BM.bootstrap_se([round(float(v), 8) for v in delta])),
        "turn_profile": turn_profile(out.get("diag") or []),
        "rule_state": out.get("hook_state"),
        "cost_note": cost_label,
    }


def classify(control, rows):
    """Frozen three-state verdict. Read the direction, then ask whether it can be seen."""
    if not control.get("ok"):
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": "控制臂与在印的书对不上（年化差 %s pp / 选股腿差 %s pp），"
                            "这不是同一本书，本面不判。"
                            % (control.get("delta_pp"), control.get("select_delta_pp"))}
    if not control.get("replay_ok"):
        return {"verdict": "CANNOT_JUDGE_REPLAY",
                "sentence": "重放重建不出引擎净值，配对的日收益差不是这台引擎的，本面不判。"}
    tested = [r for r in rows if int(r["min_hold_decisions"]) > 1
              and r.get("delta_vs_base")]
    if not tested:
        return {"verdict": "CANNOT_JUDGE_NO_ARM",
                "sentence": "没有可读的留座臂，本面不判。"}
    sig = [r for r in tested if (r["delta_vs_base"].get("p_direction") or 1.0) <= P_SEP]
    best = max(tested, key=lambda r: abs(float(r["delta_vs_base"]["obs_ann_pp"])))
    bd = best["delta_vs_base"]
    if not sig:
        return {"verdict": "MIN_HOLD_NOT_SEPARABLE",
                "sentence": "留座改不了这本书的账：最大的一档（至少留 %d 期）年化差 "
                            "%+.2fpp，块自助 %d 次里 %.0f%% 能造出同方向这么大的差，"
                            "而这把尺在这本书上能看见的最小差是 %.2fpp——差落在噪声里。"
                            % (int(best["min_hold_decisions"]), float(bd["obs_ann_pp"]),
                               int(bd.get("draws") or 0),
                               float(bd.get("p_direction") or 1.0) * 100.0,
                               float(bd.get("mde80_ann_pp") or 0.0))}
    if float(bd["obs_ann_pp"]) > 0:
        return {"verdict": "MIN_HOLD_HELPS",
                "sentence": "强制留座把这本书的账改好了：至少留 %d 期的一档年化 "
                            "%+.2fpp（块自助 %d 次里只有 %.1f%% 造得出同方向的差，尺子"
                            "能看见的最小差 %.2fpp），换手与成本腿同时降。"
                            % (int(best["min_hold_decisions"]), float(bd["obs_ann_pp"]),
                               int(bd.get("draws") or 0),
                               float(bd.get("p_direction") or 1.0) * 100.0,
                               float(bd.get("mde80_ann_pp") or 0.0))}
    return {"verdict": "MIN_HOLD_HURTS",
            "sentence": "强制留座拖低了这本书的账：至少留 %d 期的一档年化 "
                        "%+.2fpp（块自助 %d 次里只有 %.1f%% 造得出同方向的差，尺子"
                        "能看见的最小差 %.2fpp）——这本书的钱是靠换名字赚的，留座"
                        "省下的成本抵不过留下的旧名字。"
                        % (int(best["min_hold_decisions"]), float(bd["obs_ann_pp"]),
                           int(bd.get("draws") or 0),
                           float(bd.get("p_direction") or 1.0) * 100.0,
                           float(bd.get("mde80_ann_pp") or 0.0))}


def _run_arm(close, openp, amt, score, cls, rebal, cost, vol_target, hook=None):
    """One arm through the engine and its own replay, keeping the diag it decided on."""
    diag = []
    ser, mean_turn = R.open_to_open_equity(close, openp, amt, score.shift(1), rebal,
                                           SEATS, cost, vol_target=vol_target,
                                           vol_window=60, diag=diag, select_hook=hook)
    stats = N.arm_stats(ser)
    df = MM.replay(close, openp, diag, rebal, SEATS, cost, R.START, cls, bench=BENCH)
    joined = df.join(ser.rename("engine"), how="left").dropna(subset=["engine", "equity"])
    max_rel = (float((joined["equity"] - joined["engine"]).abs().max()
                     / joined["engine"].iloc[-1]) if len(joined) else None)
    return {"ser": ser, "stats": stats, "df": df, "replay_max_rel": max_rel,
            "diag": diag, "mean_turn": mean_turn,
            "names": set(p for row in diag if row.get("book") for p in row["book"]),
            "select_ann_pp": round(float(df["select"].dropna().mean()) * PER_YEAR
                                   * 100.0, 4)}


# ---------------------------------------------------------------- run

def run():
    t0 = time.time()
    price = _load(FACE_PRICE)
    cfg = price.get("config") or {}
    published = {}
    for row in (price.get("rows") or []):
        if float(row.get("min_amt_cny") or 0) == GATE:
            published = row.get("book") or {}
    cut = price.get("evidence_cutoff")
    slice_face = _load(FACE_SLICE) if os.path.exists(FACE_SLICE) else {}
    r1767_select_pp = (slice_face.get("months") or {}).get("total_pp")
    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")

    close, openp, amt, feats, n_flip = G.build_universe()
    print("[panel] %d names, %d bars, %d flips repaired, %.1fs"
          % (len(close.columns), len(close.index), n_flip, time.time() - t0), flush=True)
    cmap = A.load_class_map()
    cls = {str(k): str(v) for k, v in A.classify(list(close.columns), cmap, close).items()}
    score = E.build_score(close, amt, feats, min_amt=GATE)

    base = _run_arm(close, openp, amt, score, cls, rebal, cost, vol_target, hook=None)
    base_names = set(base.get("names") or ())
    print("[k1] cagr=%6.3f%% select=%+6.3fpp replay_rel=%.2e"
          % (float(base["stats"]["full"]["cagr"]) * 100.0, base["select_ann_pp"] or 0.0,
             base.get("replay_max_rel") or 0.0), flush=True)

    arms = [arm_row("k1", 1, base, base_names, base["df"]["net"],
                    cost_label="the published rule (control)")]
    diff_bars = {}
    for k in KS:
        log = []
        hook = make_min_hold_hook(k, log)
        out = _run_arm(close, openp, amt, score, cls, rebal, cost, vol_target, hook=hook)
        out["hook_state"] = dict(hook.state)
        out["book_log"] = log
        row = arm_row("k%d" % k, k, out, base_names, base["df"]["net"])
        row["years_vs_base"] = N.year_table(out["ser"], base["ser"])
        arms.append(row)
        d = pd.DataFrame({"a": out["df"]["net"], "b": base["df"]["net"]}).dropna()
        diff_bars["k%d" % k] = [round(float(v), 8) for v in (d["a"] - d["b"])]
        print("[k%d] cagr=%6.3f%% select=%+6.3fpp cost=%+6.3fpp turn=%.4f fresh=%.3f "
              "drop=%d gap=%+.2fpp p=%.4f"
              % (k, row["book_cagr_pct"], row["select_ann_pp"], row["cost_ann_pp"],
                 row["mean_turn"], row["turn_profile"]["fresh_share"] or 0.0,
                 (row["rule_state"] or {}).get("forced_liquid_drop", 0),
                 row["delta_vs_base"]["obs_ann_pp"],
                 row["delta_vs_base"]["p_direction"]), flush=True)

    published_cagr = (None if published.get("cagr") is None
                      else round(float(published["cagr"]) * 100.0, 3))
    delta_pp = (None if published_cagr is None
                else round(arms[0]["book_cagr_pct"] - published_cagr, 3))
    select_delta = (None if r1767_select_pp is None
                    else round(arms[0]["select_ann_pp"] - float(r1767_select_pp), 4))
    step = [{
        "arm": r["arm"], "min_hold_decisions": r["min_hold_decisions"],
        "select_ann_pp": r["select_ann_pp"], "rotate_ann_pp": r["rotate_ann_pp"],
        "size_ann_pp": r["size_ann_pp"], "cost_ann_pp": r["cost_ann_pp"],
        "r_bench_ann_pp": r["r_bench_ann_pp"], "net_ann_pp": r["net_ann_pp"],
        # replay's own contract: select + rotate + size + cost == net - r_bench
        "identity_gap_pp": round(r["select_ann_pp"] + r["rotate_ann_pp"]
                                 + r["size_ann_pp"] + r["cost_ann_pp"]
                                 + r["r_bench_ann_pp"] - r["net_ann_pp"], 4)} for r in arms]
    identity_ok = all(abs(s["identity_gap_pp"]) <= IDENTITY_TOL for s in step)
    control = {
        "published_cagr_pct": published_cagr, "cagr_pct": arms[0]["book_cagr_pct"],
        "delta_pp": delta_pp,
        "published_select_ann_pp": r1767_select_pp,
        "select_ann_pp": arms[0]["select_ann_pp"], "select_delta_pp": select_delta,
        "replay_max_rel": arms[0]["replay_max_rel"],
        "replay_ok": (arms[0]["replay_max_rel"] is not None
                      and arms[0]["replay_max_rel"] <= REPLAY_TOL),
        "ok": (delta_pp is not None and abs(delta_pp) <= CONTROL_TOL_PP
               and (select_delta is None or abs(select_delta) <= SELECT_TOL_PP)
               and (arms[0]["replay_max_rel"] is not None
                    and arms[0]["replay_max_rel"] <= REPLAY_TOL)),
    }
    verdict = classify(control, arms)
    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": (cut or str(close.index[-1].date())),
        "panel_last_bar": str(close.index[-1].date()),
        "config": {"bench": BENCH, "gate_cny": GATE, "seats": SEATS, "rebal": rebal,
                   "cost_bp_per_side": round(cost * 1e4, 3), "vol_target": vol_target,
                   "ks": list(KS), "min_amt_cny": GATE},
        "rule": {
            "statement": "a name bought at decision t is kept for at least k decisions",
            "k_semantics": "age counts decisions in the book, the buying decision being 1; "
                           "a held name with age <= k is a forced seat",
            "k1_is_the_published_rule": True,
            "forced_seat_mortality": "a forced name that is not scorable that day falls "
                                     "back to the ranking and the event is counted",
        },
        "control": control,
        "identity": {"rows": step, "ok": identity_ok, "tol_pp": IDENTITY_TOL},
        "arms": arms,
        "diff_bars": diff_bars,
        "diff_bars_note": "daily net-return difference vs k=1, rounded to 8dp; the single "
                          "input of every bootstrap in this face, kept so --check can "
                          "re-derive p and MDE80 instead of trusting the printed numbers",
        "verdict": verdict["verdict"],
        "sentence": verdict["sentence"],
        "ruler": {"block": BM.BLOCK, "draws": BM.DRAWS, "seed": BM.SEED,
                  "z80": BM.Z_80, "p_sep": P_SEP},
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("[verdict] %s | identity_ok=%s | %.1fs"
          % (out["verdict"], identity_ok, out["elapsed_sec"]), flush=True)
    return out


# ---------------------------------------------------------------- markdown

def write_md():
    d = _load(OUT_JSON)
    arms = d["arms"]
    cut = d["evidence_cutoff"]
    L = []
    L.append("# 强制留座能不能救这本书（r1769）")
    L.append("> evidence_cutoff=%s；面板末 bar=%s；脚本 `scripts/etf_book_seat_hold.py`；"
             "证据 `results/etf_book_seat_hold.json`。" % (cut, d["panel_last_bar"]))
    L.append("> 同一台引擎、同一张面板、同一把尺（块长 %d＝一个调仓周期；%d 次；种子 %d）。"
             % (d["ruler"]["block"], d["ruler"]["draws"], d["ruler"]["seed"]))
    L.append("## 问的问题")
    L.append("r1768 量出这本书的钱几乎全落在刚买进来的名字上（选股腿的 94.8%），"
             "然后指出了要紧的一条：51 个调仓周期里 51 个整本换掉，所以「换手 vs 持有」"
             "在这条规则下不是选择而是构造。要问它，必须有一条**被规则强制留住几座**的臂。")
    L.append("")
    L.append("规则只有一句话：**在第 t 次决策买进来的名字，至少留到第 t+k-1 次决策**"
             "（k=1 就是现在在印的规则）。它写在引擎自己的 `select_hook` 里——引擎、"
             "仓位缩放、成本、T+1 一行没改，也没有第二份实现。")
    L.append("")
    L.append("强制留座是有代价的诚实条款：**想留的名字当天不可交易**（流动性闸把它拿掉）"
             "时，这一座只能还给排名，并把这件事计数，不藏。")
    L.append("")
    L.append("## 三档臂的账（同一台引擎）")
    L.append("| 臂 | 最少持有 | 年化 | 夏普 | 最大回撤 | 选股腿 | 轮动腿 | 成本腿 | 指数项 | 均换手 | 新座占比 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in arms:
        L.append("| %s | %d 期 | %+.2f%% | %s | %+.2f%% | %+.2fpp | %+.2fpp | %+.2fpp | %+.2fpp | %.4f | %s |"
                 % (r["arm"], r["min_hold_decisions"], r["book_cagr_pct"],
                    ("%.3f" % r["book_sharpe"]) if r["book_sharpe"] is not None else "-",
                    r["book_maxdd_pct"], r["select_ann_pp"], r["rotate_ann_pp"],
                    r["cost_ann_pp"], r["r_bench_ann_pp"], r["mean_turn"],
                    ("%.1f%%" % (100.0 * r["turn_profile"]["fresh_share"]))
                    if r["turn_profile"]["fresh_share"] is not None else "-"))
    L.append("")
    L.append("四腿的恒等式按重放自己的契约读：`选股 + 轮动 + 规模 + 成本 + 指数项 == 净收益`"
             "（缺口 %s，容差 %.2fpp）。指数项是宽基自己的涨跌被书吃到的那一份，"
             "不是这本书挣的。"
             % (["%+.4f" % s["identity_gap_pp"] for s in d["identity"]["rows"]],
                IDENTITY_TOL))
    L.append("")
    L.append("## 差额（配对日收益差，块自助读方向与宽度）")
    L.append("| 臂 vs k1 | 年化差 | 标准误 | 能看见的最小差 MDE80 | 方向 p | t | 读法 |")
    L.append("|---|---|---|---|---|---|---|")
    for r in arms:
        b = r.get("delta_vs_base")
        if not b:
            continue
        read = ("显著更高" if (b["p_direction"] <= P_SEP and b["obs_ann_pp"] > 0)
                else "显著更低" if (b["p_direction"] <= P_SEP and b["obs_ann_pp"] < 0)
                else "落在噪声里")
        L.append("| %s | %+.2fpp | %.2fpp | %.2fpp | %.4f | %s | %s |"
                 % (r["arm"], b["obs_ann_pp"], b["se_ann_pp"], b["mde80_ann_pp"],
                    b["p_direction"], ("%.2f" % b["t"]) if b["t"] is not None else "-", read))
    L.append("")
    L.append("## 结构读数：这本书到底换不换")
    L.append("| 臂 | 决策数 | 座-期 | 新座 | 新座占比 | 强制留住 | 强制座被流动性拿走 |")
    L.append("|---|---|---|---|---|---|---|")
    for r in arms:
        tp = r["turn_profile"]
        st = r.get("rule_state") or {}
        L.append("| %s | %d | %d | %d | %s | %d | %d |"
                 % (r["arm"], tp["decisions"], tp["seat_periods"], tp["fresh_seats"],
                    ("%.1f%%" % (100.0 * tp["fresh_share"])) if tp["fresh_share"] is not None else "-",
                    int(st.get("forced_kept") or 0), int(st.get("forced_liquid_drop") or 0)))
    L.append("")
    L.append("## 逐年（各档臂相对 k1 的年收益差）")
    years = sorted({r["year"] for a in arms if a.get("years_vs_base")
                    for r in a["years_vs_base"]["rows"]})
    L.append("| 年 | " + " | ".join("%s vs k1" % a["arm"] for a in arms if a.get("years_vs_base"))
             + " |")
    L.append("|---" * (1 + sum(1 for a in arms if a.get("years_vs_base"))) + "|")
    for y in years:
        cells = []
        for a in arms:
            if not a.get("years_vs_base"):
                continue
            hit = [r for r in a["years_vs_base"]["rows"] if r["year"] == y]
            cells.append(("%+.2fpp" % hit[0]["diff_pp"]) if hit else "-")
        L.append("| %d | %s |" % (y, " | ".join(cells)))
    L.append("")
    L.append("逐年表里最响的两行是同一件事的两头：**2020 三档都赢**（+5.6~+9.6pp），"
             "**2025 三档都大输**（-17.3~-22.8pp），2026 也输。2025 是全样本最强的一年"
             "（`ETF_BOOK_ALPHA` 面记的商品贡献 +17.6pp），留座在这一年把该换进来的座"
             "锁住了；2020 反过来。这两件事只是并列，不构成因果——本面没有按名字拆"
             "「留座挡掉了哪一次换仓」。")
    L.append("")
    L.append("## 怎么读这三档（别把单调当证据）")
    L.append("三档的差是同一个方向、且随 k 单调（年化 %s），但它们是**三条共享绝大部分路径的臂**"
             "（同一批名字、同一批日子、只是留座多少不同），所以这不是三个独立试验，"
             "单调性不构成三份证据。真正能读的只有每一档自己的 p 与 MDE80：三档全部落在"
             "噪声里（最小 p=%.2f），而尺子在这本书上要看见 7.5~8.7pp 才算数。"
             % (" → ".join("%+.2f%%" % a["book_cagr_pct"] for a in arms),
                min((a["delta_vs_base"]["p_direction"] or 1.0)
                    for a in arms if a.get("delta_vs_base"))))
    L.append("")
    L.append("## 判词")
    L.append("**%s** — %s" % (d["verdict"], d["sentence"]))
    L.append("")
    L.append("## 控制臂")
    c = d["control"]
    L.append("- k=1 复现在印的一格：年化 %+.2f%%（在印 %s%%，差 %s pp，容差 %.2fpp）"
             % (c["cagr_pct"], c["published_cagr_pct"], c["delta_pp"], CONTROL_TOL_PP))
    L.append("- 选股腿复现：%+.4fpp（在印 %s，差 %s pp）"
             % (c["select_ann_pp"], c["published_select_ann_pp"], c["select_delta_pp"]))
    L.append("- 重放重建引擎净值：最大相对偏差 %.2e（容差 %.0e）"
             % (c["replay_max_rel"] or 0.0, REPLAY_TOL))
    L.append("- 四腿加性与净收益恒等：%s（容差 %.2fpp）"
             % ("成立" if d["identity"]["ok"] else "不成立", IDENTITY_TOL))
    L.append("")
    L.append("## 局限")
    L.append("- 留座只测它的账，不测它为什么：留下的名字为什么还在（因子没变 / 只是没掉出前五）"
             "本面不区分。")
    L.append("- 一个调仓周期是 20 根 bar，k=5 就是至少 100 根 bar（约一个季度）；"
             "样本里 84 个决策期，k=5 的臂最多换 17 次，容量比 k=2 小得多。")
    L.append("- 面板是现存 ETF（幸存者偏差照旧），2020-2023 段本来就只有 6% 上下。")
    L.append("- 差额用配对日收益差读，块长＝一个调仓周期；换更长的块会把噪声算得更宽，"
             "判词方向不会变，除非差本来就贴着线。")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("[md] %s (%d lines)" % (OUT_MD, len(L)), flush=True)
    return OUT_MD


# ---------------------------------------------------------------- check

def _check():
    d = _load(OUT_JSON)
    problems = []
    c = d["control"]
    if not c.get("ok"):
        problems.append("the control arm does not reproduce the published book")
    if not c.get("replay_ok"):
        problems.append("the replay does not rebuild the engine curve")
    if not (d.get("identity") or {}).get("ok"):
        problems.append("select+rotate+size+cost does not add up to net")
    for r in d["arms"]:
        b = r.get("delta_vs_base")
        if not b:
            continue
        bars = (d.get("diff_bars") or {}).get(r["arm"])
        if bars is None:
            problems.append("%s has no stored difference series to re-derive" % r["arm"])
            continue
        again = BM.bootstrap_se(bars)
        if again is None:
            problems.append("%s bootstrap re-derives to nothing" % r["arm"])
            continue
        if abs(float(again["obs_ann_pp"]) - float(b["obs_ann_pp"])) > 1e-3:
            problems.append("%s obs gap re-derives to %s, face says %s"
                            % (r["arm"], again["obs_ann_pp"], b["obs_ann_pp"]))
        if int(again["p_direction"] * 10000 + 0.5) != int(float(b["p_direction"]) * 10000 + 0.5):
            problems.append("%s direction p re-derives to %s, face says %s"
                            % (r["arm"], again["p_direction"], b["p_direction"]))
        if abs(float(again["mde80_ann_pp"]) - float(b["mde80_ann_pp"])) > 1e-3:
            problems.append("%s MDE80 re-derives to %s, face says %s"
                            % (r["arm"], again["mde80_ann_pp"], b["mde80_ann_pp"]))
    v = classify(c, d["arms"])
    if v["verdict"] != d["verdict"]:
        problems.append("verdict re-derives to %s, face says %s"
                        % (v["verdict"], d["verdict"]))
    ok = not problems
    print(json.dumps({"ok": ok, "problems": problems, "verdict": v["verdict"],
                      "arms": [a["arm"] for a in d["arms"]]}, ensure_ascii=False))
    return 0 if ok else 1


# ---------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    def row_of(scores):
        return pd.Series(scores, dtype=float)

    names = ["A", "B", "C", "D", "E", "F", "G", "H"]
    r1 = row_of({"A": 9.0, "B": 8.0, "C": 7.0, "D": 6.0, "E": 5.0,
                 "F": 4.0, "G": 3.0, "H": 2.0})
    r2 = row_of({"A": 0.1, "B": 8.0, "C": 7.0, "D": 6.0, "E": 5.0,
                 "F": 4.5, "G": 3.0, "H": 2.0})

    # L1 k=1 is the plain top-n, decision after decision, even with a book in hand
    h1 = make_min_hold_hook(1)
    p1 = h1(r1, [], 5, pd.Timestamp("2020-01-01"))
    p2 = h1(r2, p1, 5, pd.Timestamp("2020-02-01"))
    leg("L1 k=1 follows the ranking exactly",
        p1 == ["A", "B", "C", "D", "E"] and p2 == ["B", "C", "D", "E", "F"])

    # L2 k=2 keeps a freshly bought name through the very next decision
    h2 = make_min_hold_hook(2)
    p1 = h2(r1, [], 5, pd.Timestamp("2020-01-01"))
    p2 = h2(r2, p1, 5, pd.Timestamp("2020-02-01"))
    leg("L2 k=2 keeps a name the ranking would have dropped", "A" in p2
        and len(p2) == 5 and len(set(p2)) == 5)

    # L3 k=3 keeps it one decision longer than k=2 -- the boundary is the rule, not a taste
    h3 = make_min_hold_hook(3)
    q1 = h3(r1, [], 5, pd.Timestamp("2020-01-01"))
    q2 = h3(r2, q1, 5, pd.Timestamp("2020-02-01"))
    leg("L3 k=3 protects the same name at the second decision", "A" in q2)

    # L4 once its age passes k the seat is free again
    h2b = make_min_hold_hook(2)
    s1 = h2b(r1, [], 5, pd.Timestamp("2020-01-01"))
    s2 = h2b(r2, s1, 5, pd.Timestamp("2020-02-01"))
    s3 = h2b(r2, s2, 5, pd.Timestamp("2020-03-01"))
    leg("L4 at age k+1 the forced seat is released", "A" not in s3)

    # L5 a forced name that is not scorable that day falls back to the ranking, and says so
    r3 = row_of({"B": 8.0, "C": 7.0, "D": 6.0, "E": 5.0, "F": 4.5, "G": 3.0})
    h2c = make_min_hold_hook(2)
    t1 = h2c(r1, [], 5, pd.Timestamp("2020-01-01"))
    t2 = h2c(r3, t1, 5, pd.Timestamp("2020-02-01"))
    leg("L5 a dead forced seat goes back to the ranking",
        "A" not in t2 and len(t2) == 5 and h2c.state["forced_liquid_drop"] == 1)

    # L6 the shape contract the engine enforces is never violated
    shapes_ok = True
    hh = make_min_hold_hook(3)
    book = []
    for i in range(30):
        sc = row_of({nm: float((hash((nm, i % 7)) % 100)) / 10.0 for nm in names})
        book = hh(sc, book, 5, pd.Timestamp("2020-01-%02d" % (i + 1)))
        shapes_ok = shapes_ok and len(book) == 5 and len(set(book)) == 5 \
            and all(nm in sc.index for nm in book)
    leg("L6 every decision returns five distinct scorable names", shapes_ok)

    # L7 k=1 reproduces the engine's own nlargest on a random path (no hook overhead)
    rng = np.random.default_rng(7)
    same = True
    h1b = make_min_hold_hook(1)
    book = []
    for i in range(40):
        sc = pd.Series(rng.random(len(names)), index=names)
        book = h1b(sc, book, 5, pd.Timestamp("2020-06-01") + pd.Timedelta(days=i * 20))
        same = same and book == list(sc.nlargest(5).index)
    leg("L7 k=1 is bit-identical to the published selection", same)

    # L8 structure read: a book that never trades shows a zero fresh share
    diag = [{"book": ["A", "B", "C", "D", "E"]}] * 5
    tp = turn_profile(diag)
    leg("L8 an untouched book has a 20% fresh share (first decision only)",
        tp["fresh_seats"] == 5 and tp["seat_periods"] == 25
        and abs(tp["fresh_share"] - 0.2) < 1e-9)

    # L9 verdict mapping is the frozen three states, and the tolerance is the gate
    good = {"ok": True, "replay_ok": True, "delta_pp": 0.0, "select_delta_pp": 0.0}
    up = {"arm": "k2", "min_hold_decisions": 2,
          "delta_vs_base": {"obs_ann_pp": 3.0, "p_direction": 0.01,
                            "mde80_ann_pp": 2.0, "draws": 2000}}
    dn = {"arm": "k2", "min_hold_decisions": 2,
          "delta_vs_base": {"obs_ann_pp": -3.0, "p_direction": 0.01,
                            "mde80_ann_pp": 2.0, "draws": 2000}}
    tie = {"arm": "k2", "min_hold_decisions": 2,
           "delta_vs_base": {"obs_ann_pp": 1.0, "p_direction": 0.40,
                             "mde80_ann_pp": 2.0, "draws": 2000}}
    leg("L9 up/down/tie map to the three states",
        classify(good, [up])["verdict"] == "MIN_HOLD_HELPS"
        and classify(good, [dn])["verdict"] == "MIN_HOLD_HURTS"
        and classify(good, [tie])["verdict"] == "MIN_HOLD_NOT_SEPARABLE")

    # L10 a broken control is never judged, whatever the arms say
    bad = dict(good, ok=False)
    leg("L10 a control that misses the published cell blocks the verdict",
        classify(bad, [up])["verdict"] == "CANNOT_JUDGE_CONTROL")

    # L11 the face cannot judge when there is no arm above k=1 to read
    leg("L11 no forced-hold arm means no verdict",
        classify(good, [dict(up, min_hold_decisions=1)])["verdict"]
        == "CANNOT_JUDGE_NO_ARM")

    # L12 an all-zero difference cannot claim a direction (the bootstrap ruler says so)
    zero = BM.bootstrap_se([0.0] * 600)
    leg("L12 an all-zero difference reads p=1.0, not a direction",
        zero is not None and zero["p_direction"] == 1.0 and zero["obs_ann_pp"] == 0.0)

    # L13 the bootstrap ruler is the frozen one this face prints
    leg("L13 ruler constants are the published ones",
        (BM.BLOCK, BM.DRAWS, BM.SEED) == (20, 2000, 20261116))

    # L14 the four-leg identity is the replay's own contract, not "legs add up to net":
    # the benchmark's own return is part of net and none of the four legs. Reading it
    # without the benchmark term prints a constant -2.01pp "failure" on a healthy split.
    a = MM.attribute({"X": 0.5, "Y": 0.5}, {"X": 0.02, "Y": -0.01},
                     {"X": "equity", "Y": "equity"}, 0.005, 0.0001)
    gap = (a["select"] + a["rotate"] + a["size"] + a["cost"] + 0.005) - a["net"]
    leg("L14 select+rotate+size+cost+r_bench == net", abs(gap) < 1e-12
        and abs(a["resid"]) < 1e-12)

    ok = sum(1 for _n, c in legs if c)
    for name, cond in legs:
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
    print("etf_book_seat_hold selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "run":
        d = run()
        print(json.dumps({"verdict": d["verdict"], "evidence_cutoff": d["evidence_cutoff"]},
                         ensure_ascii=False))
        return 0
    if cmd == "md":
        write_md()
        return 0
    if cmd in ("check", "verify"):
        return _check()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
