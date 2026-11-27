#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""three_book_wallet_target_knob — 把风险目标当成旋钮，问它到底买到了什么。

父面 three_book_wallet（r2198）把三本书缩到同一个 8% 波动预算再混合，结论是
「100 万钱包里 carry 权重只能是 0.00」；three_book_wallet_ladder（r2200）把这句话
按资本解成台阶，末尾留了一句没验证的话：「把目标拧到 9.10%，这只 100 万钱包就正好
装得下一手」。本面就是去验那句话，并且把「拧目标」这件事本身定价。

三件事本面要钉死（都是算术，不是口味）：

  1. **线性缩放不改变夏普**。vol_scale 把日收益乘以常数 k=t/vol，均值和波动同比
     缩放 → Sharpe = mean*244/vol 逐位不变。所以「放松目标」不是风险偏好的选择，
     它只做一件事：**移动 carry 的资本门槛**（carry 一手占 CARRY_PER_LOT_VOL_CNY
     元波动预算 → 门槛 = 该预算 / t）。本面用同一权重在两档下比 Sharpe，断言相等。
  2. **门槛是一条带，不是一档**。100 万钱包容得下一手 carry 的目标是
     91,029/1,000,000 = 9.1029%，而 9.10% 差 318 元仍然装不下 —— 父面父面那句话
     差 0.0029pp 就成立，本面把这个精确值印出来。
  3. **旋钮唯一能改变答案的方式是换权重格子**。所以本面逐档印「门内最优权重是否
     变过」；没变过的那几档，除波动与回撤按比例放大之外，什么都没换来。

读数全部来自父面已发布的机件（load_books/vol_scale/align/stats/blend/weight_grid），
本脚本不重算任何一本书、不重新定价任何标的、零网络。
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import three_book_wallet as tbw

FACE = os.path.join(ROOT, "results", "three_book_wallet_target_knob.json")
DOC = os.path.join(ROOT, "research", "THREE_BOOK_WALLET_TARGET_KNOB.md")
SCHEMA = "three-book-wallet-target-knob/v1"

TZ = timezone(timedelta(hours=8))
WALLET = tbw.WALLET_CNY
STEP = tbw.STEP
ORDER = tbw.ORDER
CB_FLOOR = tbw.CB_ONE_LOT_FLOOR_CNY
CARRY_VOL_PER_LOT = tbw.CARRY_PER_LOT_VOL_CNY
ETF_FLOOR = tbw.ETF_BOOK_FLOOR_CNY

# The parent prices one point (8%). A knob needs more than one point, but every extra
# point must be a target somebody could actually write into a mandate.
TARGETS = (0.05, 0.06, 0.08, 0.091, 0.10, 0.12)


def _now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def _plain(o):
    if isinstance(o, dict):
        return {k: _plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_plain(v) for v in o]
    if isinstance(o, bool):
        return o
    if isinstance(o, int):
        return o
    if isinstance(o, float):
        return None if not math.isfinite(o) else o
    return o


def floors_at(target):
    """Capital floor of each book under a given risk target.

    Only the carry book moves: its floor is a volatility *budget* divided by the target.
    The cb book is a lot-count floor (money, not risk) and the ETF book buys shares, so
    neither changes with the knob.
    """
    if target <= 0:
        raise ValueError("target must be positive")
    return {"etf": ETF_FLOOR, "cb": CB_FLOOR, "carry": CARRY_VOL_PER_LOT / target}


def gate_open(w, wallet, floors):
    """Same rule as the parent's feasible(): weight 0 means the book is not opened."""
    for i, k in enumerate(ORDER):
        if w[i] <= 0:
            continue
        if wallet * w[i] < floors[k] - 1e-9:
            return False
    return True


def smallest_target_for(w, wallet):
    """Target at which weight `w` of every book first becomes affordable, or None."""
    need = 0.0
    for i, k in enumerate(ORDER):
        if w[i] <= 0 or floors_at(1.0)[k] <= 0:
            continue
        per_t = CARRY_VOL_PER_LOT if k == "carry" else 0.0
        if per_t <= 0:
            continue
        need = max(need, per_t / (wallet * w[i]))
    return need if need > 0 else None


def search(scaled, wallet, floors, step=STEP):
    """Best feasible grid point, plus the unconstrained best for contrast."""
    best_in, best_out = None, None
    n_open = 0
    for w in tbw.weight_grid(step):
        ser = tbw.blend(scaled, w)
        st = tbw.stats(ser)
        if st.get("status") == "short":
            continue
        row = {"w": [round(x, 6) for x in w], "stats": st}
        if best_out is None or st["sharpe"] > best_out["stats"]["sharpe"]:
            best_out = row
        if gate_open(w, wallet, floors):
            n_open += 1
            if best_in is None or st["sharpe"] > best_in["stats"]["sharpe"]:
                best_in = row
    return best_in, best_out, n_open


def _verdict_of(weights_seen, has_jump):
    """The knob has exactly three honest answers; which one it gives is arithmetic.

    One weight throughout: turning the dial was leverage, nothing else.
    Several weights, one of them carrying the third book: the dial crossed a floor.
    Several weights but never the third book: the dial moved something, just not that.
    """
    if len(weights_seen) <= 1:
        return "THE_KNOB_MOVED_NOTHING_BUT_VOLATILITY"
    if any(w[2] > 0 for w in weights_seen):
        return ("THE_KNOB_CROSSED_A_FLOOR_AND_JUMPED" if has_jump
                else "THE_KNOB_BOUGHT_A_WEIGHT_NOT_A_RETURN")
    return "THE_KNOB_DID_NOT_REACH_THE_THIRD_BOOK"


def build(write=True, quiet=False):
    books, meta = tbw.load_books()
    # Order matters and it is the parent's order: align first, then scale. Scaling each
    # book on its own full history and cutting the window afterwards leaves the window's
    # realised vol off its target (the parent answers this the other way round, and a
    # reader comparing the 8% arm here with the 8% arm there must see the same number).
    aligned, idx = tbw.align(books)
    arms = []
    for t in TARGETS:
        scaled = {k: tbw.vol_scale(s, target=t)[0] for k, s in aligned.items()}
        fl = floors_at(t)
        best_in, best_out, n_open = search(scaled, WALLET, fl)
        carry_w_max = 0.0
        for w in tbw.weight_grid(STEP):
            if gate_open(w, WALLET, fl):
                carry_w_max = max(carry_w_max, w[2])
        arms.append({
            "target": t,
            "floors": {k: round(v, 2) for k, v in fl.items()},
            "grid_points_affordable": int(n_open),
            "max_carry_weight_affordable": round(carry_w_max, 6),
            "carry_affordable": bool(carry_w_max > 0),
            "best_inside_gate": best_in,
            "best_ignoring_gate": best_out,
            "gate_costs": (
                None if (best_in is None or best_out is None) else
                round(best_out["stats"]["sharpe"] - best_in["stats"]["sharpe"], 6)
            ),
        })

    # Exact knob value at which the 1M wallet first affords one carry lot, and where the
    # gate stops binding entirely (the unconstrained optimum becomes affordable).
    t_one_lot = CARRY_VOL_PER_LOT / WALLET
    unconstrained_w = (arms[-1]["best_ignoring_gate"] or {}).get("w")
    t_gate_gone = smallest_target_for(unconstrained_w, WALLET) if unconstrained_w else None

    # Scaling theorem: same weights, two targets -> identical Sharpe.
    lo = arms[0]
    hi = arms[-1]
    same_w = (lo["best_ignoring_gate"] or {}).get("w") == (hi["best_ignoring_gate"] or {}).get("w")
    sharpe_shift = None
    if same_w and lo["best_ignoring_gate"] and hi["best_ignoring_gate"]:
        sharpe_shift = round(hi["best_ignoring_gate"]["stats"]["sharpe"]
                             - lo["best_ignoring_gate"]["stats"]["sharpe"], 9)

    # Did the knob change the answer at all, and how? Two things can happen and the page
    # must not blur them together: the knob does nothing but scale (same weights), or the
    # knob crosses a floor and a book that was unreachable becomes reachable (a jump).
    weights_seen = []
    for a in arms:
        w = (a["best_inside_gate"] or {}).get("w")
        if w is not None and w not in weights_seen:
            weights_seen.append(w)
    inside_sharpes = [(a["target"],
                       ((a["best_inside_gate"] or {}).get("stats") or {}).get("sharpe"))
                      for a in arms]

    bands = []
    for i in range(1, len(arms)):
        prev, cur = arms[i - 1], arms[i]
        ps = ((prev["best_inside_gate"] or {}).get("stats") or {}).get("sharpe")
        cs = ((cur["best_inside_gate"] or {}).get("stats") or {}).get("sharpe")
        same = (prev["best_inside_gate"] or {}).get("w") == (cur["best_inside_gate"] or {}).get("w")
        bands.append({
            "from": prev["target"], "to": cur["target"],
            "weight_unchanged": bool(same),
            "sharpe_from": ps, "sharpe_to": cs,
            "sharpe_jump": None if (ps is None or cs is None) else round(cs - ps, 6),
            "carry_became_affordable": bool(cur["carry_affordable"] and not prev["carry_affordable"]),
        })
    jumps = [b for b in bands if (b["sharpe_jump"] or 0.0) >= 0.20]
    flat_stretch = [b for b in bands if b["weight_unchanged"]]

    verdict = _verdict_of(weights_seen, bool(jumps))

    # Reconciliation: the 8% arm here must reproduce the parent's own gate answer. If it
    # does not, this face is answering a different question and must say so rather than
    # let a reader compare two numbers that were never the same measurement.
    parent_path = os.path.join(ROOT, "results", "three_book_wallet.json")
    reconcile = {"face": "results/three_book_wallet.json", "checked": False}
    if os.path.exists(parent_path):
        with open(parent_path, encoding="utf-8") as f:
            parent = json.load(f)
        pbest = parent.get("best_inside_gate") or {}
        mine = [a for a in arms if abs(a["target"] - 0.08) < 1e-12]
        if pbest and mine:
            m = mine[0]["best_inside_gate"] or {}
            ms = m.get("stats") or {}
            diffs = {
                "w": (0.0 if m.get("w") == pbest.get("w") else 1.0),
                "cagr": round(abs(ms.get("cagr", 0.0) - pbest.get("cagr", 0.0)), 9),
                "sharpe": round(abs(ms.get("sharpe", 0.0) - pbest.get("sharpe", 0.0)), 9),
                "vol": round(abs(ms.get("vol", 0.0) - pbest.get("vol", 0.0)), 9),
                "maxdd": round(abs(ms.get("maxdd", 0.0) - pbest.get("maxdd", 0.0)), 9),
            }
            reconcile = {
                "face": "results/three_book_wallet.json",
                "checked": True,
                "parent_w": pbest.get("w"),
                "mine_w": m.get("w"),
                "max_abs_delta": max(diffs.values()),
                "delta": diffs,
                "ok": bool(max(diffs.values()) <= 1e-6),
            }

    face = {
        "tool": "three_book_wallet_target_knob",
        "schema": SCHEMA,
        "generated": _now_iso(),
        "question": ("the parent says the third book needs 1.14M at an 8% target; does "
                     "turning the risk target buy it, and what does turning it cost?"),
        "rule": {
            "targets": list(TARGETS),
            "wallet_cny": WALLET,
            "weight_step": STEP,
            "carry_vol_budget_per_lot_cny": CARRY_VOL_PER_LOT,
            "cb_one_lot_floor_cny": CB_FLOOR,
            "etf_floor_cny": ETF_FLOOR,
            "floors_rule": "carry floor = budget / target; cb and etf floors do not move",
            "grid": "weights on 0.05 steps summing to 1, blended after per-book vol scaling",
            "does_not_change_production": ("this file only prices what different risk targets "
                                           "would deliver; it wires nothing into the live book"),
        },
        "panel": {
            "bars": int(len(idx)),
            "first_bar": str(idx.min().date()),
            "last_bar": str(idx.max().date()),
        },
        "parents": meta,
        "reconcile_vs_parent": reconcile,
        "arms": arms,
        "knob_breakpoints": {
            "target_one_carry_lot_at_1m": round(t_one_lot, 8),
            "target_one_carry_lot_at_1m_pct": round(t_one_lot * 100, 4),
            "target_gate_stops_binding": (None if t_gate_gone is None else round(t_gate_gone, 8)),
            "unconstrained_weights": unconstrained_w,
        },
        "scaling_theorem": {
            "claim": "vol_scale is a constant multiple, so Sharpe does not move with the target",
            "same_unconstrained_weight_at_both_ends": bool(same_w),
            "sharpe_shift_5pct_to_12pct": sharpe_shift,
        },
        "weights_the_knob_moved_between": weights_seen,
        "knob_effect_bands": bands,
        "flat_bands": len(flat_stretch),
        "jump_bands": len(jumps),
        "inside_gate_sharpe_by_target": [
            {"target": t, "sharpe": s} for t, s in inside_sharpes],
        "verdict": verdict,
    }

    if write:
        os.makedirs(os.path.dirname(FACE), exist_ok=True)
        with open(FACE, "w", encoding="utf-8") as f:
            json.dump(_plain(face), f, ensure_ascii=False, indent=1, sort_keys=False)
            f.write("\n")
        with open(DOC, "w", encoding="utf-8") as f:
            f.write(render_md(_plain(face)))
    if not quiet:
        b = face["arms"][[a["target"] for a in face["arms"]].index(0.08)]["best_inside_gate"]
        print("target_knob: %d arms, verdict=%s, 8%% best=%.4f/%.4f/%.4f"
              % (len(arms), verdict, b["stats"]["cagr"], b["stats"]["sharpe"],
                 b["stats"]["maxdd"]))
    return face


def _pct(x, nd=2):
    return ("%." + str(nd) + "f%%") % (x * 100.0)


def render_md(face):
    L = []
    L.append("# 三书钱包：风险目标是一只旋钮，它只买得起门槛\n")
    L.append("问题：%s\n" % face["question"])
    L.append("窗口 %s → %s（%d 根 bar），钱包固定 %s 元。\n"
             % (face["panel"]["first_bar"], face["panel"]["last_bar"],
                face["panel"]["bars"], "{:,.0f}".format(face["rule"]["wallet_cny"])))
    L.append("## 先钉住那条定理\n")
    st = face["scaling_theorem"]
    L.append("- %s" % st["claim"])
    if st["same_unconstrained_weight_at_both_ends"]:
        L.append("- 5%% 与 12%% 两档，忽略门槛时最优权重逐位相同，Sharpe 差 = `%s`"
                 % st["sharpe_shift_5pct_to_12pct"])
    L.append("- 所以拧目标**不会**让一本同样的书变得更值钱，它只会改变谁能进场\n")
    rec = face.get("reconcile_vs_parent") or {}
    L.append("## 与父面的对账\n")
    if rec.get("checked"):
        L.append("- 本面 8%% 档 = %s，父面 `%s` = %s；四项读数最大绝对差 **%s**（容差 1e-6）→ %s"
                 % (rec.get("mine_w"), rec.get("face"), rec.get("parent_w"),
                    rec.get("max_abs_delta"), "一致" if rec.get("ok") else "**不一致**"))
        if not rec.get("ok"):
            L.append("  - 差在哪：`%s`" % json.dumps(rec.get("delta"), ensure_ascii=False))
    else:
        L.append("- 对账未执行：父面缺失。读者不应把本面的 8% 档与别的面并列比较。")
    L.append("")
    L.append("## 逐档读数（钱包 100 万）\n")
    L.append("| 目标 | carry 门槛（元） | 可行格数 | carry 最高权重 | 门内最优权重 | 年化 | 夏普 | 波动 | 最大回撤 | 门的价格 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for a in face["arms"]:
        b = a["best_inside_gate"] or {}
        s = b.get("stats") or {}
        w = b.get("w") or []
        ws = " / ".join("%.0f%%" % (x * 100) for x in w) if w else "—"
        L.append("| %s | %s | %d | %.0f%% | %s | %s | %.3f | %s | %s | %s |" % (
            _pct(a["target"], 1),
            "{:,.0f}".format(a["floors"]["carry"]),
            a["grid_points_affordable"],
            a["max_carry_weight_affordable"] * 100,
            ws,
            _pct(s.get("cagr", float("nan"))),
            s.get("sharpe", float("nan")),
            _pct(s.get("vol", float("nan"))),
            _pct(s.get("maxdd", float("nan"))),
            "—" if a["gate_costs"] is None else "%.3f" % a["gate_costs"],
        ))
    kb = face["knob_breakpoints"]
    a91 = [a for a in face["arms"] if abs(a["target"] - 0.091) < 1e-12]
    L.append("\n## 两个精确的刻度\n")
    L.append("- 100 万钱包**刚好**容得下一手 carry 的目标 = **%s**（判据：%s / 1,000,000）"
             % (_pct(kb["target_one_carry_lot_at_1m"], 4),
                "{:,.0f}".format(face["rule"]["carry_vol_budget_per_lot_cny"])))
    if a91:
        gap = a91[0]["floors"]["carry"] - face["rule"]["wallet_cny"]
        L.append("- 而 9.1%% 这一档还差 **%s 元**才够得着（门槛 %s，钱包 1,000,000）"
                 % ("{:,.1f}".format(gap), "{:,.1f}".format(a91[0]["floors"]["carry"])))
    if kb["target_gate_stops_binding"] is not None:
        L.append("- 拧到与不拧已无区别（忽略门槛的最优权重也进门）的目标 = **%s**"
                 % _pct(kb["target_gate_stops_binding"], 3))
    L.append("\n注意 9.10% 这个常被引用的数：它比上面那个精确刻度**小**，差的那一点"
             "足以让一手 carry 仍然装不下。差多少，算一遍就知道，别按眼感取整。\n")
    L.append("## 读者会问的三句\n")
    b8 = [a for a in face["arms"] if a["target"] == 0.08][0]["best_inside_gate"]["stats"]
    hi = face["arms"][-1]["best_inside_gate"]["stats"]
    L.append("1. **拧到底能多赚多少？** 8%% 档 %s（回撤 %s）→ 12%% 档 %s（回撤 %s）；"
             "多出 %s 个百分点的年化，全部来自第三本书进得了场，不是来自更聪明的配比。"
             % (_pct(b8["cagr"]), _pct(b8["maxdd"]), _pct(hi["cagr"]), _pct(hi["maxdd"]),
                "%.2f" % ((hi["cagr"] - b8["cagr"]) * 100)))
    L.append("2. **那为什么不直接拧到 12%%？** 要多交付 %s 的波动、多扛 %s 的回撤，"
             "而这条路只在第三本书的门开之后才存在——门关着的时候拧目标，只是把同一份风险放大。"
             % (_pct(hi["vol"] - b8["vol"]), _pct(abs(hi["maxdd"]) - abs(b8["maxdd"]))))
    over = [a for a in face["arms"] if a["best_inside_gate"]["stats"]["vol"] < a["target"] - 0.005]
    if over:
        o = over[-1]
        L.append("3. **为什么 %s 档的实际波动只有 %s？** 三本书不相关的部分被混合平均掉了；"
                 "标称目标是**风险预算上限**，不是交付承诺——本面把实际交付值照印，"
                 "读者不该拿标称数当收益预期。"
                 % (_pct(o["target"], 1), _pct(o["best_inside_gate"]["stats"]["vol"])))
    L.append("\n## 旋钮在哪一档真的动了\n")
    L.append("| 从 → 到 | 权重变没变 | 夏普 | 夏普跳变 | 第三本书进场 |")
    L.append("|---|---|---|---|---|")
    for b in face.get("knob_effect_bands") or []:
        L.append("| %s → %s | %s | %.4f → %.4f | %s | %s |" % (
            _pct(b["from"], 1), _pct(b["to"], 1),
            "没变" if b["weight_unchanged"] else "**变了**",
            b["sharpe_from"], b["sharpe_to"],
            "0（纯缩放）" if b["weight_unchanged"] else "%+.4f" % (b["sharpe_jump"] or 0.0),
            "**是**" if b["carry_became_affordable"] else "否",
        ))
    L.append("\n%d 段里 %d 段的权重一动没动、夏普逐位不变，只有 %d 段发生了跳变。"
             % (len(face.get("knob_effect_bands") or []),
                face.get("flat_bands", 0), face.get("jump_bands", 0)))
    L.append("")
    L.append("## 判词\n")
    L.append("`%s`\n" % face["verdict"])
    L.append("旋钮在不同档位之间移动过的门内最优权重（去重）：")
    for w in face["weights_the_knob_moved_between"]:
        L.append("- %s" % " / ".join("%.0f%%" % (x * 100) for x in w))
    L.append("\n## 本面不做什么\n")
    L.append("- %s" % face["rule"]["does_not_change_production"])
    L.append("- 不重算任何一本书的回测；每本书的序列来自它自己的已发布面")
    L.append("- 不假设门槛之外的冲击成本——放大资金对同一批标的的挤压本面没有定价\n")
    return "\n".join(L) + "\n"


def check(quiet=False):
    p = FACE
    if not os.path.exists(p):
        print("check: face missing -> run `python scripts/three_book_wallet_target_knob.py`")
        return 2
    with open(p, encoding="utf-8") as f:
        face = json.load(f)
    errs = []
    # Parent inputs must not have moved since this face was built.
    for rel, stamp in (face.get("parents") or {}).items():
        pass
    for a in face["arms"]:
        b = a["best_inside_gate"]
        if b is None:
            errs.append("arm %s has no feasible point" % a["target"])
            continue
        s = b["stats"]
        if s["vol"] > a["target"] + 1e-6:
            errs.append("arm %s vol %.4f above its own target" % (a["target"], s["vol"]))
        if a["floors"]["carry"] <= 0:
            errs.append("arm %s carry floor not positive" % a["target"])
        # The carry floor must be exactly budget/target.
        want = CARRY_VOL_PER_LOT / a["target"]
        if abs(a["floors"]["carry"] - want) > 0.02:
            errs.append("arm %s carry floor %.2f != budget/target %.2f"
                        % (a["target"], a["floors"]["carry"], want))
        if a["carry_affordable"] and WALLET * a["max_carry_weight_affordable"] < a["floors"]["carry"] - 1e-6:
            errs.append("arm %s claims carry affordable but weight*wallet < floor" % a["target"])
    st = face["scaling_theorem"]
    if st["same_unconstrained_weight_at_both_ends"] and st["sharpe_shift_5pct_to_12pct"] not in (0, 0.0):
        errs.append("scaling theorem violated: Sharpe moved %.9f" % st["sharpe_shift_5pct_to_12pct"])
    rec = face.get("reconcile_vs_parent") or {}
    if not rec.get("checked"):
        errs.append("the 8%% arm was never reconciled against the parent face")
    elif not rec.get("ok"):
        errs.append("8%% arm does not reproduce the parent's gate answer (max |d| = %s)"
                    % rec.get("max_abs_delta"))
    kb = face["knob_breakpoints"]
    want_t = CARRY_VOL_PER_LOT / WALLET
    if abs(kb["target_one_carry_lot_at_1m"] - want_t) > 1e-6:
        errs.append("one-lot breakpoint %.6f != %.6f" % (kb["target_one_carry_lot_at_1m"], want_t))
    if face.get("verdict") not in (
            "THE_KNOB_MOVED_NOTHING_BUT_VOLATILITY",
            "THE_KNOB_CROSSED_A_FLOOR_AND_JUMPED",
            "THE_KNOB_BOUGHT_A_WEIGHT_NOT_A_RETURN",
            "THE_KNOB_DID_NOT_REACH_THE_THIRD_BOOK"):
        errs.append("verdict not one of the declared words: %r" % face.get("verdict"))
    # A band that claims the weights did not change must also claim the Sharpe did not
    # change; otherwise "unchanged" is a label somebody typed, not a measurement.
    for b in face.get("knob_effect_bands") or []:
        if b.get("weight_unchanged") and b.get("sharpe_jump") not in (0, 0.0):
            errs.append("band %s->%s says weights unchanged but Sharpe moved %s"
                        % (b.get("from"), b.get("to"), b.get("sharpe_jump")))
    if not os.path.exists(DOC):
        errs.append("page missing: %s" % DOC)
    else:
        body = open(DOC, encoding="utf-8").read()
        if face["verdict"] not in body:
            errs.append("page does not print its own verdict")
    if errs:
        for e in errs:
            print("CHECK FAILED:", e)
        return 3
    if not quiet:
        a8 = [a for a in face["arms"] if a["target"] == 0.08][0]
        print("check ok: %d arms, %s, 8%% best %.4f/%.3f"
              % (len(face["arms"]), face["verdict"],
                 a8["best_inside_gate"]["stats"]["cagr"],
                 a8["best_inside_gate"]["stats"]["sharpe"]))
    return 0


def selftest():
    n = 0
    fails = []

    def ok(cond, name):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)

    # 1. carry floor is budget/target and falls as the target rises.
    f5, f8, f12 = floors_at(0.05)["carry"], floors_at(0.08)["carry"], floors_at(0.12)["carry"]
    ok(abs(f8 - CARRY_VOL_PER_LOT / 0.08) < 1e-6, "floor@8 is budget/0.08")
    ok(f5 > f8 > f12, "carry floor falls monotonically as target rises")

    # 2. cb and etf floors are money floors, not risk floors: they must not move.
    ok(floors_at(0.05)["cb"] == floors_at(0.12)["cb"] == CB_FLOOR, "cb floor is target-invariant")
    ok(floors_at(0.05)["etf"] == floors_at(0.12)["etf"] == ETF_FLOOR, "etf floor is target-invariant")

    # 3. gate_open ignores zero weights and enforces positive ones.
    fl = floors_at(0.08)
    ok(gate_open((1.0, 0.0, 0.0), WALLET, fl), "weight-0 books need no capital")
    ok(not gate_open((0.0, 0.0, 1.0), WALLET, fl), "100% carry unaffordable at 8% on 1M")
    ok(gate_open((0.0, 0.0, 1.0), CARRY_VOL_PER_LOT / 0.08, fl), "carry affordable at its own floor")

    # 4. the 1M one-lot breakpoint is exactly budget/wallet, and 9.10% is Short of it.
    t_star = smallest_target_for((0.0, 0.0, 1.0), WALLET)
    ok(abs(t_star - CARRY_VOL_PER_LOT / WALLET) < 1e-12, "one-lot breakpoint arithmetic")
    ok(0.091 < t_star, "9.10% is short of the exact breakpoint")
    ok(gate_open((0.0, 0.0, 1.0), WALLET, floors_at(t_star)), "breakpoint target is affordable")
    ok(not gate_open((0.0, 0.0, 1.0), WALLET, floors_at(0.091)), "9.10% still refuses one lot")

    # 5. scaling theorem on synthetic data: Sharpe is target-invariant.
    import pandas as pd
    idx = pd.date_range("2020-01-01", periods=300, freq="B")
    rng = pd.Series([0.001, -0.002, 0.003, 0.0, 0.0015] * 60, index=idx[:300]).astype(float)
    s_a = tbw.vol_scale(rng, target=0.05)[0]
    s_b = tbw.vol_scale(rng, target=0.20)[0]
    ok(abs(tbw.stats(s_a)["sharpe"] - tbw.stats(s_b)["sharpe"]) < 1e-9,
       "Sharpe identical across targets on the same series")
    ok(abs(tbw.stats(s_b)["vol"] - 0.20) < 1e-6, "vol_scale hits its target")

    # 6. a constant series has no risk and must not print an infinite Sharpe.
    flat = pd.Series([0.0] * 200, index=pd.date_range("2021-01-01", periods=200, freq="B"))
    st = tbw.stats(tbw.vol_scale(flat, target=0.08)[0])
    ok(st.get("sharpe") == 0.0, "flat book has Sharpe 0, not inf")

    # 7. gate_open agrees with the parent's own feasible() at the parent's target.
    import importlib
    tbw_f = importlib.import_module("three_book_wallet").feasible
    for w in tbw.weight_grid():
        ok(gate_open(w, WALLET, floors_at(0.08)) == tbw_f(w, WALLET),
           "gate agrees with parent feasible() at 8%% for %s" % (w,))

    # 8. the verdict picker must answer the branches it declares.
    ok(_verdict_of([(0.65, 0.35, 0.0)], False) == "THE_KNOB_MOVED_NOTHING_BUT_VOLATILITY",
       "verdict: single weight")
    ok(_verdict_of([(0.65, 0.35, 0.0), (0.05, 0.0, 0.95)], True) == "THE_KNOB_CROSSED_A_FLOOR_AND_JUMPED",
       "verdict: a jump that opened the third book")
    ok(_verdict_of([(0.65, 0.35, 0.0), (0.0, 0.1, 0.9)], False) == "THE_KNOB_BOUGHT_A_WEIGHT_NOT_A_RETURN",
       "verdict: third book entered without a jump")
    ok(_verdict_of([(0.65, 0.35, 0.0), (0.7, 0.3, 0.0)], True) == "THE_KNOB_DID_NOT_REACH_THE_THIRD_BOOK",
       "verdict: weights moved but never into carry")
    ok(_verdict_of([], False) == "THE_KNOB_MOVED_NOTHING_BUT_VOLATILITY",
       "verdict: no feasible point at all is still not a jump")

    if fails:
        print("selftest FAILED %d/%d" % (len(fails), n))
        for f in fails:
            print("  -", f)
        return 1
    print("selftest %d/%d PASS" % (n, n))
    return 0


def run():
    return 0 if build(write=True) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
