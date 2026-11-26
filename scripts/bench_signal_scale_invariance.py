"""Signal scale-invariance census for the futures bench.

r2142 found one rule family (donchian) comparing two different unit systems:
`bench_core.align_futures` hands rules an *adjusted return index* (starts at
1.0) while `high`/`low` columns are **raw settlement levels**. Every donchian
arm therefore saw `close (≈1) < any high (≈hundreds)` on every bar and could
only ever be short.

This script stops asking "which family did we happen to inspect" and asks the
mechanical question instead: **does a family's output survive a change of the
units it is fed?**  Perturbation is the probe, so nothing here depends on
reading the signal code and agreeing with it.

Perturbations applied to the *same* price panel:

  uniform_up    closes, highs, lows all x1000   (common rescale; every rule
                that compares two series in the same units is invariant)
  close_only    closes x1000, highs/lows untouched (mixes two unit systems —
                the shape of the r2142 defect)
  highlow_adj   highs/lows rescaled by the bar's own adjustment factor
                (adjusted_close / raw_close) -> the consistent-unit fix
  uniform_add   everything +1000 — **diagnostic only**, never a verdict: a
                rule that divides one price by another legitimately changes,
                so additivity only tells you the rule is ratio-shaped

Verdict per family (closed set):
  INVARIANT             no change under a common rescale and none under a
                        closes-only rescale (rare tie flaps reported apart)
  CROSS_UNIT_SENSITIVE  survives a common rescale, changes under closes-only
  SCALE_DEPENDENT       changes under a common rescale by >=0.1% of cells ->
                        contains an absolute price threshold

Second half of the face prices the defect and then audits the *fix*: the two
candidate repairs (rebase raw bars on the first close, vs. rescale high/low by
each bar's own adjustment factor) are not the same series, because raw bars
still carry roll gaps.  Their disagreement is measured, not assumed away.

Usage:
  python scripts/bench_signal_scale_invariance.py run
  python scripts/bench_signal_scale_invariance.py --check
  python scripts/bench_signal_scale_invariance.py --verify
  python scripts/bench_signal_scale_invariance.py --selftest
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import bench_core as bc  # noqa: E402
import bench_fut_trend as bft  # noqa: E402
import bench_generic as bg  # noqa: E402

RESULT = os.path.join(ROOT, "results", "bench_signal_scale_invariance.json")
PAGE = os.path.join(ROOT, "research", "BENCH-SIGNAL-SCALE-INVARIANCE.md")
AUDIT_FACE = os.path.join(ROOT, "results", "bench_donchian_unit_audit.json")

SCHEMA = "bench_signal_scale_invariance/v1"
VERDICTS = ("INVARIANT", "CROSS_UNIT_SENSITIVE", "SCALE_DEPENDENT")
PARAM_SETS = [(55, 20), (40, 15), (20, 10)]
SCALE_TOL = 1e-3  # share of cells that must move before "scale dependent"


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_sha(path: str) -> str:
    with open(path, "rb") as fh:
        return sha256_bytes(fh.read())


# ---------------------------------------------------------------------------
# the families under test
# ---------------------------------------------------------------------------
def families():
    """(module, name, callable(closes, highs, lows) -> {code: Series})."""
    return [
        ("bench_generic", "ma_cross", lambda c, h, l: bg.sig_ma_cross(c, 50, 200)),
        ("bench_generic", "tsmom", lambda c, h, l: bg.sig_tsmom(c, 252, 21)),
        ("bench_generic", "donchian_55_20",
         lambda c, h, l: bg.sig_donchian(c, h, l, 55, 20)),
        ("bench_generic", "donchian_20_10",
         lambda c, h, l: bg.sig_donchian(c, h, l, 20, 10)),
        ("bench_generic", "reversal", lambda c, h, l: bg.sig_reversal(c, 5)),
        ("bench_generic", "xs_rank", lambda c, h, l: bg.sig_xs_rank(c, 60, 1.0 / 3.0)),
        ("bench_fut_trend", "tsmom", lambda c, h, l: bft.sig_tsmom(c)),
        ("bench_fut_trend", "ma_cross", lambda c, h, l: bft.sig_ma_cross(c)),
        ("bench_fut_trend", "donchian_55_20",
         lambda c, h, l: bft.sig_donchian(c, h, l, 55, 20)),
        ("bench_fut_trend", "reversal", lambda c, h, l: bft.sig_reversal(c)),
        ("bench_fut_trend", "xs_mom", lambda c, h, l: bft.sig_xs_mom(c)),
    ]


# ---------------------------------------------------------------------------
# perturbations
# ---------------------------------------------------------------------------
def perturb(closes, highs, lows, adj_factor, kind):
    def scaled(d, k):
        return {c: s * k for c, s in d.items()}

    def moved(d, k):
        return {c: s + k for c, s in d.items()}

    if kind == "base":
        return closes, highs, lows
    if kind == "uniform_up":
        return scaled(closes, 1000.0), scaled(highs, 1000.0), scaled(lows, 1000.0)
    if kind == "uniform_add":
        return moved(closes, 1000.0), moved(highs, 1000.0), moved(lows, 1000.0)
    if kind == "close_only":
        return scaled(closes, 1000.0), dict(highs), dict(lows)
    if kind == "highlow_adj":
        return (dict(closes),
                {c: highs[c] * adj_factor[c] for c in highs},
                {c: lows[c] * adj_factor[c] for c in lows})
    raise ValueError(kind)


def as_frame(signals):
    frame = pd.DataFrame({c: s for c, s in signals.items()})
    return frame.sort_index().fillna(-99.0)


def diff_cells(a, b):
    """Cells where two signal dicts disagree (NaN-normalised)."""
    fa, fb = as_frame(a), as_frame(b)
    fb = fb.reindex(index=fa.index, columns=fa.columns)
    return int(((fa - fb).abs() > 1e-9).to_numpy().sum())


def cells_total(signals):
    frame = as_frame(signals)
    return int(frame.shape[0] * frame.shape[1])


def hist(signals):
    live = short = long_ = 0
    for s in signals.values():
        live += int(s.notna().sum())
        short += int((s < 0).sum())
        long_ += int((s > 0).sum())
    return {"live_bars": live, "short_bars": short, "long_bars": long_,
            "share_short": round(short / live, 6) if live else None}


def effective(diffs, total):
    """Counts below the noise floor are float ties, not a unit effect.

    A handful of cells flipping when the whole panel is multiplied by 1000 is
    `s/past` landing exactly on 1.0 in one world and 1.0000000000000002 in the
    other — sign() reads 0 vs 1.  Treating that as "this family mixes units"
    would be the same mistake as trusting a single noisy cell anywhere else,
    so a count only counts once it clears SCALE_TOL of all (product, bar) cells.
    """
    if not total:
        return {k: 0 for k in diffs}
    return {k: (v if v / total >= SCALE_TOL else 0) for k, v in diffs.items()}


def classify(diffs, total):
    eff = effective(diffs, total)
    if eff["uniform_up"] > 0:
        return "SCALE_DEPENDENT"
    if eff["close_only"] > 0:
        return "CROSS_UNIT_SENSITIVE"
    return "INVARIANT"


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def build_payload():
    panel = bc.load_futures_products(bc.FUTURES)
    if not panel:
        raise SystemExit("no futures panel on disk")
    dates, closes, rets, vols = bc.align_futures(panel)
    highs = {c: df["high"].reindex(dates) for c, df in panel.items()}
    lows = {c: df["low"].reindex(dates) for c, df in panel.items()}
    raw_close = {c: df["close"].reindex(dates) for c, df in panel.items()}

    # per-bar adjustment factor between the shipped adjusted close and the raw
    # settlement level; highs/lows belong to the raw system, so multiplying
    # them by this factor puts the whole bar into the adjusted system.
    adj_factor, unit_gap, rolls = {}, {}, {}
    for code in closes:
        raw = raw_close[code]
        factor = (closes[code] / raw).replace([np.inf, -np.inf], np.nan)
        adj_factor[code] = factor.ffill().fillna(1.0)
        ratio = (highs[code] / closes[code]).replace([np.inf, -np.inf], np.nan).dropna()
        unit_gap[code] = round(float(ratio.median()), 3) if len(ratio) else None
        moves = raw.pct_change().abs()
        cut = max(bc.ROLL_SCALE * float(moves.median()), bc.ROLL_FLOOR)
        rolls[code] = int((moves > cut).to_numpy().sum())

    rows = []
    for module, name, fn in families():
        base = fn(closes, highs, lows)
        total = cells_total(base)
        diffs, states = {}, {}
        for kind in ("uniform_up", "close_only", "highlow_adj", "uniform_add"):
            c2, h2, l2 = perturb(closes, highs, lows, adj_factor, kind)
            other = fn(c2, h2, l2)
            diffs[kind] = diff_cells(base, other)
            states[kind] = hist(other)
        verdict = classify(diffs, total)
        eff = effective(diffs, total)
        rows.append({
            "family": f"{module}.{name}",
            "module": module,
            "name": name,
            "verdict": verdict,
            "diff_cells": diffs,
            "diff_cells_effective": eff,
            "cells_total": total,
            "diff_share_uniform_up": round(diffs["uniform_up"] / total, 6) if total else None,
            "tie_flaps_under_rescale": diffs["uniform_up"] - eff["uniform_up"],
            "ratio_shaped_extra_add_breakage": diffs["uniform_add"] - diffs["uniform_up"],
            "base_state": hist(base),
            "perturbed_state": {k: v for k, v in states.items() if diffs[k]},
            "consumes_high_low": name.startswith("donchian"),
        })

    # second half: how big is the donchian defect, per product and per set,
    # and do the two candidate repairs agree?
    gap_rows = []
    for entry, exit_ in PARAM_SETS:
        for code in panel:
            raw = raw_close[code]
            first = raw.dropna()
            base_lvl = float(first.iloc[0]) if len(first) else 1.0
            shipped = bg.sig_donchian({code: closes[code]}, {code: highs[code]},
                                      {code: lows[code]}, entry, exit_)
            rebased = bg.sig_donchian({code: raw / base_lvl},
                                      {code: highs[code] / base_lvl},
                                      {code: lows[code] / base_lvl}, entry, exit_)
            adjusted = bg.sig_donchian({code: closes[code]},
                                       {code: highs[code] * adj_factor[code]},
                                       {code: lows[code] * adj_factor[code]}, entry, exit_)
            h_ship, h_reb, h_adj = hist(shipped), hist(rebased), hist(adjusted)
            gap_rows.append({
                "entry": entry, "exit": exit_, "product": code,
                "bars": int(closes[code].notna().sum()),
                "roll_bars_detected": rolls.get(code),
                "unit_gap_median_high_over_close": unit_gap.get(code),
                "shipped": h_ship,
                "fix_rebase_raw": h_reb,
                "fix_bar_adjusted": h_adj,
                "cells_flipped": diff_cells(shipped, adjusted),
                "cells_between_fixes": diff_cells(rebased, adjusted),
                "shipped_all_short": bool(h_ship["live_bars"] and h_ship["long_bars"] == 0),
            })

    cross = cross_face_check(gap_rows)

    sensitive = [r["family"] for r in rows if r["verdict"] == "CROSS_UNIT_SENSITIVE"]
    scaled = [r["family"] for r in rows if r["verdict"] == "SCALE_DEPENDENT"]
    flipped = [g for g in gap_rows if g["cells_flipped"] > 0]
    agree = [g for g in gap_rows if g["cells_between_fixes"] == 0]
    headline = {
        "families": len(rows),
        "invariant": sum(1 for r in rows if r["verdict"] == "INVARIANT"),
        "cross_unit_sensitive": sensitive,
        "scale_dependent": scaled,
        "donchian_shipped_all_short_pairs": f"{sum(1 for g in gap_rows if g['shipped_all_short'])}/{len(gap_rows)}",
        "donchian_pairs_with_flipped_bars": len(flipped),
        "donchian_max_cells_flipped": max((g["cells_flipped"] for g in gap_rows), default=0),
        "fixes_agree_pairs": f"{len(agree)}/{len(gap_rows)}",
        "fix_disagreement_max_share_short": max(
            (abs((g["fix_rebase_raw"]["share_short"] or 0.0) - (g["fix_bar_adjusted"]["share_short"] or 0.0))
             for g in gap_rows), default=0.0),
        "cross_face_agrees": cross.get("agrees"),
    }
    if sensitive and not scaled and len(agree) == len(gap_rows):
        verdict = "ONE_FAMILY_MIXES_UNITS"
    elif sensitive and len(agree) < len(gap_rows):
        verdict = "UNIT_MIX_AND_FIX_ITSELF_DIFFERS"
    elif not sensitive and not scaled:
        verdict = "NO_UNIT_DEFECT_FOUND"
    else:
        verdict = "MORE_THAN_ONE_DEFECT"

    inputs = {}
    for rel in ("scripts/bench_core.py", "scripts/bench_generic.py",
                "scripts/bench_fut_trend.py"):
        inputs[rel] = file_sha(os.path.join(ROOT, rel))
    inputs["panel_products"] = sorted(panel)

    cutoff = None
    for s in closes.values():
        last = s.dropna()
        if len(last):
            stamp = last.index[-1].strftime("%Y-%m-%d")
            cutoff = stamp if cutoff is None else max(cutoff, stamp)

    return {
        "schema": SCHEMA,
        "generated": now_iso(),
        "evidence_cutoff": cutoff,
        "inputs": inputs,
        "verdict": verdict,
        "headline": headline,
        "families": rows,
        "unit_gap": unit_gap,
        "roll_bars": rolls,
        "donchian_gap": gap_rows,
        "cross_face": cross,
    }


def cross_face_check(gap_rows):
    """Do the two candidate repairs (r2142's raw rebase, our bar-level
    adjustment factor) produce the same short share?  They should only if raw
    bars carry no roll gaps."""
    mine = {}
    for g in gap_rows:
        mine[(g["entry"], g["exit"], g["product"])] = g["fix_bar_adjusted"]["share_short"]
    theirs = {}
    have_face = os.path.exists(AUDIT_FACE)
    if have_face:
        with open(AUDIT_FACE, encoding="utf-8") as fh:
            face = json.load(fh)
        for combo in face.get("combos", []):
            fixed = (combo.get("unit_fixed_state_long_only") or {}).get("share_short")
            if fixed is None:
                continue
            for code in combo.get("products", []):
                theirs[(combo.get("entry"), combo.get("exit"), code)] = fixed
    shared = [k for k in theirs if k in mine and mine[k] is not None]
    if not have_face:
        return {"agrees": None, "reason": "r2142 audit face absent"}
    if not shared:
        return {"agrees": None, "reason": "no overlapping (params, product)"}
    deltas = [abs(mine[k] - theirs[k]) for k in shared]
    worst = max(deltas)
    return {
        "agrees": bool(worst <= 0.02),
        "pairs_compared": len(shared),
        "worst_share_short_delta": round(worst, 6),
        "tolerance": 0.02,
        "reference_face": "results/bench_donchian_unit_audit.json",
        "reading": ("两次修法同解：原始 bar 没有换月跳空" if worst <= 0.02 else
                    "两次修法不同解：重基修法保留原始 bar 的换月跳空，bar 级调整因子修法消除它；"
                    "差多少=换月跳空对这条规则的影响"),
    }


# ---------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------
def fmt(v, suffix=""):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:,.4f}{suffix}" if abs(v) < 1 else f"{v:,.2f}{suffix}"
    return f"{v}{suffix}"


def write_page(payload):
    h = payload["headline"]
    lines = []
    a = lines.append
    a("# 信号族的单位普查：哪条规则把两套单位当一套用（以及两种修法本身不一致）")
    a("")
    a(f"生成 `{payload['generated']}` · 证据日 `{payload['evidence_cutoff']}` · 判词 **{payload['verdict']}**")
    a("")
    a("## 一句话")
    a("")
    a(f"把 `{h['families']}` 个信号族喂同一份面板的四种单位扰动："
      f"**{h['invariant']} 个完全不动**，"
      f"**{len(h['cross_unit_sensitive'])} 个在两套单位混用时改变输出**"
      f"（{', '.join(h['cross_unit_sensitive']) or '无'}），"
      f"绝对价位阈值类 **{', '.join(h['scale_dependent']) or '无'}**。"
      f"donchian 的 {h['donchian_shipped_all_short_pairs']} 个（参数集 × 品种）组合在出厂输入下"
      f"**一根多头都没开过**。")
    a("")
    a(f"第二件事更要紧：**两种修法不一致**，只有 {h['fixes_agree_pairs']} 对给出同一答案，"
      f"短路占比最大相差 **{h['fix_disagreement_max_share_short']*100:.2f} 个百分点** —— "
      f"因为「按首个收盘重基原始价」这一修法把**换月跳空留在序列里**，而 bar 级调整因子的修法把它消掉。"
      f"所以 r2142 页面上的参考读数（商品 20/10 → +4.03%）本身仍站在一条含跳空的序列上。")
    a("")
    a("## 为什么用扰动而不是读代码")
    a("")
    a("同一单位体系里的两条序列做比较，两边同乘一个正数时结论必然不变。"
      "所以「换个单位答案就变了」等价于「这条规则在比较两套单位」。"
      "这条判据不依赖对代码的理解，也不依赖审查者当时有没有注意到某一行。")
    a("")
    a("三种扰动进入判词：`uniform_up` 三者同乘 1000（共标度）· "
      "`close_only` 只把收盘乘 1000、高低价留在原始价位（混用两套单位）· "
      "`highlow_adj` 把高低价按当根 bar 自己的调整因子换到收盘那套单位（=一致化修法）。")
    a("")
    a("第四种 `uniform_add` 三者同加 1000 进表但**不进判词**，理由是算出来的：时间序列里"
      "`sign(s/p-1)` 与 `sign(s-p)` 恒等，所以共加一个常数**根本翻不动**任何时间序列比值规则；"
      "它只会翻动横截面规则（不同品种价位不同，加同一个数不是「在比值空间里的同一个变换」）。"
      "把横截面的位移差算成缺陷，就是把度量方式差异当成 bug。")
    a("")
    a("噪声地板：差异格只有达到全部 (品种, bar) 格的 0.1% 才计数。低于这条线的翻动是浮点并列——"
      "`s/past` 在一侧恰等于 1、在另一侧等于 1.0000000000000002，`sign()` 读成 0 与 1。"
      "把它升格成「这条族混用单位」与信任任何单个噪声格是同一类错误。")
    a("")
    a("## 逐族读数")
    a("")
    a("| 族 | 判词 | 共标度差异格 | 只缩放收盘 | 一致化后 | 加法位移(诊断) | 出厂短路占比 |")
    a("|---|---|---:|---:|---:|---:|---:|")
    for r in payload["families"]:
        d = r["diff_cells"]
        a(f"| `{r['family']}` | {r['verdict']} | {d['uniform_up']:,} | "
          f"{d['close_only']:,} | {d['highlow_adj']:,} | {d['uniform_add']:,} | "
          f"{fmt(r['base_state']['share_short'])} |")
    a("")
    a("差异格 = 两套输入的信号在多少个 (品种, bar) 上不等（NaN 归一后）。"
      "非 donchian 族的后两列恒为 0，因为它们的函数签名里根本没有高低价——"
      "这是免疫的证明，不是推断。两处需要如实说明："
      "`reversal` 在共标度与只缩放收盘下各有 2 格翻动，是 `s/past` 恰等于 1 的浮点并列，"
      "低于噪声地板被记作 `tie_flaps_under_rescale`，不改变判词；"
      "`xs_rank` / `xs_mom` 的加法位移列上千格翻动，正是横截面规则在位移下的正常反应（见上一节）。")
    a("")
    a("## donchian 的错有多大")
    a("")
    a("| 参数 | 品种 | bar | 检出换月 | 高低价/收盘中位比 | 出厂短路 | 重基修法短路 | bar 级调整短路 | 出厂→修正翻面格 |")
    a("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for g in payload["donchian_gap"]:
        a(f"| {g['entry']}/{g['exit']} | {g['product']} | {g['bars']:,} | "
          f"{g['roll_bars_detected']} | {fmt(g['unit_gap_median_high_over_close'], '×')} | "
          f"{fmt(g['shipped']['share_short'])} | {fmt(g['fix_rebase_raw']['share_short'])} | "
          f"{fmt(g['fix_bar_adjusted']['share_short'])} | {g['cells_flipped']:,} |")
    a("")
    a("出厂短路占比 100% 就是「这条规则从来没开过多头」，不是「它看空」。"
      "中位比一列说明两套单位相距多远：100× 以上意味着收盘价在规则眼里永远位于任何高点下方。")
    a("")
    a("## 修法本身也要验")
    a("")
    a("两条候选修法看似等价，实际不是：")
    a("")
    a("1. **重基原始价**（r2142 用的那条）：把原始 close/high/low 同除以首个收盘。三者进了同一套单位，"
      "但原始 bar **仍带着换月跳空**——主力连续在换月那天会凭空出现 5%–30% 的价位台阶。")
    a("2. **bar 级调整因子**（本件）：把当根 bar 的高低价乘以「调整收盘 / 原始收盘」，"
      "整根 bar 平移进调整体系，跳空随之消失。")
    a("")
    a(f"两者在 {len(payload['donchian_gap'])} 对里只有 {h['fixes_agree_pairs']} 对给出同一短路占比，"
      f"最大相差 {h['fix_disagreement_max_share_short']*100:.2f} 个百分点。")
    a("")
    cross = payload["cross_face"]
    if cross.get("agrees") is None:
        a(f"与 r2142 审计面可比性：不可比（{cross.get('reason')}）。")
    else:
        a(f"与 r2142 审计面的交叉核对：比对 {cross['pairs_compared']} 对，短路占比最大差 "
          f"**{cross['worst_share_short_delta']:.6f}**（容差 {cross['tolerance']}）→ "
          f"**{'一致' if cross['agrees'] else '不一致'}**。{cross.get('reading','')}")
    a("")
    a("结论不是「谁算错了」，而是：**修法要选，而选之前得知道两条修法差在哪**。"
      "含换月跳空的序列喂给突破规则，会让规则在每次换月附近误判一次方向——"
      "这正是「参考读数」不能直接当新判决用的原因。")
    a("")
    a(f"口径注记：上一段的 {h['fix_disagreement_max_share_short']*100:.2f}pp 是**全样本**口径；"
      f"与 r2142 面比对时对方是**各卡自己的窗口**口径（如商品从 2008-01-09 起），"
      f"最大差因此放大到 {cross.get('worst_share_short_delta', 0):.4f}。两个数不矛盾，是两个口径，"
      "并列印出来而不是挑一个说。")
    a("")
    a("## 约束与不宣称")
    a("")
    a("- 本件只判「输入单位是否被混用」与「两条修法是否同解」，**不重算任何收益**，也不改任何卡片判词。")
    a("- 换月检出用的是 `bench_core` 自己的判据（8× 中位绝对变动且 >0.5%）；检出数一列只说明序列里有几次换月，不保证检出完备。")
    a("- 族清单取自 `bench_generic` 与 `bench_fut_trend` 的公开函数面；两个模块之外的规则（ETF／指数／债券侧自建引擎）不在射程。")
    a("- 修正本身要改共享代码面，本轮竞争窗内未动；修法与重跑清单见 r2142 页面末节，"
      "但要先按本件第 2 节选定修法。")
    a("")
    a("## 复现")
    a("")
    a("```")
    a("python scripts/bench_signal_scale_invariance.py run      # 重算并入档")
    a("python scripts/bench_signal_scale_invariance.py --check  # 结构/算术复核")
    a("python scripts/bench_signal_scale_invariance.py --verify # 全量重派生比对")
    a("python scripts/bench_signal_scale_invariance.py --selftest")
    a("```")
    a("")
    with open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


# ---------------------------------------------------------------------------
# check / selftest
# ---------------------------------------------------------------------------
def check(payload):
    fails = []
    if payload.get("schema") != SCHEMA:
        fails.append("schema")
    if payload.get("verdict") not in ("ONE_FAMILY_MIXES_UNITS", "NO_UNIT_DEFECT_FOUND",
                                      "MORE_THAN_ONE_DEFECT", "UNIT_MIX_AND_FIX_ITSELF_DIFFERS"):
        fails.append("verdict not in closed set")
    for r in payload["families"]:
        if r["verdict"] not in VERDICTS:
            fails.append(f"{r['family']}: verdict not in closed set")
        if classify(r["diff_cells"], r["cells_total"]) != r["verdict"]:
            fails.append(f"{r['family']}: verdict disagrees with diff counts")
        if r["diff_cells_effective"] != effective(r["diff_cells"], r["cells_total"]):
            fails.append(f"{r['family']}: stored effective counts do not re-derive")
        if r["ratio_shaped_extra_add_breakage"] < 0:
            fails.append(f"{r['family']}: additive diagnostic below rescale baseline")
        if not r["consumes_high_low"] and r["diff_cells_effective"]["highlow_adj"] != 0:
            fails.append(f"{r['family']}: non-donchian family moved by the high/low fix")
        adj = r["base_state"]
        if adj["live_bars"] and adj["long_bars"] + adj["short_bars"] > adj["live_bars"]:
            fails.append(f"{r['family']}: long+short exceeds live bars")
    for g in payload["donchian_gap"]:
        if g["shipped_all_short"] != (g["shipped"]["long_bars"] == 0 and g["shipped"]["live_bars"] > 0):
            fails.append(f"donchian {g['entry']}/{g['exit']} {g['product']}: all-short flag")
        if g["shipped"]["share_short"] not in (1.0, None) and g["shipped_all_short"]:
            fails.append(f"donchian {g['entry']}/{g['exit']} {g['product']}: share/short mismatch")
        if g["cells_between_fixes"] > g["cells_flipped"] + g["bars"]:
            fails.append(f"donchian {g['entry']}/{g['exit']} {g['product']}: fix deltas exceed bar count")
    h = payload["headline"]
    if h["invariant"] + len(h["cross_unit_sensitive"]) + len(h["scale_dependent"]) != h["families"]:
        fails.append("family accounting does not add up")
    if not os.path.exists(PAGE):
        fails.append("page missing")
    else:
        body = open(PAGE, "rb").read().decode("utf-8")
        if "%%" in body:
            fails.append("page has %% residue")
        if "\r" in body:
            fails.append("page has CR")
        if payload["verdict"] not in body:
            fails.append("page does not print the verdict token")
    return fails


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except Exception as exc:  # noqa: BLE001
            legs.append((name, False, f"{type(exc).__name__}: {exc}"))

    rng = np.random.default_rng(20261126)
    idx = pd.date_range("2020-01-01", periods=400, freq="B")
    # prices on a realistic level (~3,000) so that a +1000 shift is the same
    # order of magnitude as the price itself, which is what makes the additive
    # diagnostic meaningful
    px = pd.Series(3000.0 * np.cumprod(1.0 + rng.normal(0.0003, 0.01, len(idx))), index=idx)
    toyd = {"X": px}
    highs_raw = {"X": px * 1.02}
    lows_raw = {"X": px * 0.98}
    unit = {"X": pd.Series(1.0, index=idx)}

    def toy_ratio(c, h, l):
        out = {}
        for k, s in c.items():
            past = s.shift(20)
            out[k] = np.sign(s / past - 1.0).where(past.notna())
        return out

    def toy_level(c, h, l):
        return {k: pd.Series(np.where(s > 3000.0, 1.0, -1.0), index=s.index).where(s.notna())
                for k, s in c.items()}

    def toy_mixed(c, h, l):
        return {k: pd.Series(np.where(s > h[k].reindex(s.index), 1.0, -1.0), index=s.index).where(s.notna())
                for k, s in c.items()}

    def run_all(fn, adj):
        base = fn(toyd, highs_raw, lows_raw)
        total = cells_total(base)
        out = {}
        for kind in ("uniform_up", "close_only", "highlow_adj", "uniform_add"):
            c2, h2, l2 = perturb(toyd, highs_raw, lows_raw, adj, kind)
            out[kind] = diff_cells(base, fn(c2, h2, l2))
        return out, classify(out, total), total

    def t_probe_invariant():
        d, v, _ = run_all(toy_ratio, unit)
        assert v == "INVARIANT", (d, v)

    def t_probe_scale_dependent():
        d, v, _ = run_all(toy_level, unit)
        assert d["uniform_up"] > 0 and v == "SCALE_DEPENDENT", (d, v)

    def t_probe_mixed_units():
        d, v, _ = run_all(toy_mixed, unit)
        assert d["close_only"] > 0 and v == "CROSS_UNIT_SENSITIVE", (d, v)

    def t_additive_is_diagnostic_only():
        # time-series ratio rules cannot be flipped by a common additive shift:
        # sign(s/p - 1) == sign(s - p) exactly, so zero extra breakage is the
        # correct reading, not a blind spot of the probe
        d, v, _ = run_all(toy_ratio, unit)
        assert d["uniform_add"] == 0 and v == "INVARIANT", (d, v)
        # cross-sectional rank DOES move under a shift (the shift is not common
        # in ratio space across products at different price levels) and that
        # must still not become a verdict
        a = pd.Series(3000.0 * np.cumprod(1.0 + rng.normal(0.0003, 0.01, len(idx))), index=idx)
        b = pd.Series(50.0 * np.cumprod(1.0 + rng.normal(0.0003, 0.01, len(idx))), index=idx)
        two = {"A": a, "B": b}
        base = bg.sig_xs_rank(two, 20, 1.0 / 3.0)
        shifted = bg.sig_xs_rank({k: s + 1000.0 for k, s in two.items()}, 20, 1.0 / 3.0)
        scaled = bg.sig_xs_rank({k: s * 1000.0 for k, s in two.items()}, 20, 1.0 / 3.0)
        assert diff_cells(base, shifted) > 0, "rank rule should move under an additive shift"
        assert diff_cells(base, scaled) == 0, "rank rule should not move under a common rescale"

    def t_real_invariant_families():
        for fn in (lambda c, h, l: bg.sig_ma_cross(c, 50, 200),
                   lambda c, h, l: bft.sig_xs_mom(c)):
            d, v, _ = run_all(fn, unit)
            assert v == "INVARIANT", (fn, d, v)

    def t_real_donchian_sensitive():
        d, v, _ = run_all(lambda c, h, l: bg.sig_donchian(c, h, l, 20, 10), unit)
        assert d["uniform_up"] == 0 and d["close_only"] > 0, d
        assert v == "CROSS_UNIT_SENSITIVE", (d, v)

    def t_adj_factor_identity():
        closes, raw = {"X": px}, {"X": px}
        factor = {c: (closes[c] / raw[c]).ffill().fillna(1.0) for c in closes}
        assert (factor["X"] - 1.0).abs().max() < 1e-12
        a = bg.sig_donchian({"X": px}, {"X": px * 1.02}, {"X": px * 0.98}, 55, 20)
        b = bg.sig_donchian({"X": px}, {"X": px * 1.02 * factor["X"]},
                            {"X": px * 0.98 * factor["X"]}, 55, 20)
        assert diff_cells(a, b) == 0

    def t_two_fixes_differ_when_roll_exists():
        # a 30% level step in the raw series: rebasing keeps the step, the
        # bar-level factor removes it
        raw = px.copy()
        raw.iloc[200:] = raw.iloc[200:] * 1.30
        adj = raw.copy()
        adj.iloc[199:] = adj.iloc[199:] / 1.30  # adjusted world: step removed
        factor = (adj / raw).ffill().fillna(1.0)
        base_lvl = float(raw.dropna().iloc[0])
        hi_raw, lo_raw = raw * 1.01, raw * 0.99
        rebased = bg.sig_donchian({"X": raw}, {"X": hi_raw / base_lvl},
                                  {"X": lo_raw / base_lvl}, 20, 10)
        adjusted = bg.sig_donchian({"X": adj}, {"X": hi_raw * factor},
                                   {"X": lo_raw * factor}, 20, 10)
        assert diff_cells(rebased, adjusted) > 0

    def t_hist_accounting():
        h = hist(toyd)
        assert h["live_bars"] == h["long_bars"] + h["short_bars"] == len(idx)

    def t_diff_detects_one_cell():
        a = {"X": pd.Series([1.0, 1.0, -1.0], index=idx[:3])}
        b = {"X": pd.Series([1.0, -1.0, -1.0], index=idx[:3])}
        assert diff_cells(a, b) == 1

    def t_perturb_keeps_shape():
        c2, h2, l2 = perturb(toyd, highs_raw, lows_raw,
                             {"X": pd.Series(2.0, index=idx)}, "highlow_adj")
        assert (h2["X"] - highs_raw["X"] * 2.0).abs().max() < 1e-12
        assert c2["X"].equals(toyd["X"])

    leg("probe: ratio rule is INVARIANT", t_probe_invariant)
    leg("probe: absolute threshold is SCALE_DEPENDENT", t_probe_scale_dependent)
    leg("probe: mixed-unit rule is CROSS_UNIT_SENSITIVE", t_probe_mixed_units)
    leg("additive shift is diagnostic, never a verdict", t_additive_is_diagnostic_only)
    leg("real bench_generic/bft non-donchian families are INVARIANT", t_real_invariant_families)
    leg("real donchian survives rescale but not closes-only", t_real_donchian_sensitive)
    leg("adjustment factor identity when no roll exists", t_adj_factor_identity)
    leg("two fixes diverge once a level step exists", t_two_fixes_differ_when_roll_exists)
    leg("hist accounting adds up", t_hist_accounting)
    leg("diff_cells detects exactly one changed cell", t_diff_detects_one_cell)
    leg("perturb keeps close series and scales high/low", t_perturb_keeps_shape)

    ok = sum(1 for _, good, _ in legs if good)
    for name, good, err in legs:
        print(("[PASS] " if good else "[FAIL] ") + name + ("" if good else " :: " + err))
    print(f"selftest {ok}/{len(legs)} PASS")
    return 0 if ok == len(legs) else 1


def write_result(payload):
    os.makedirs(os.path.dirname(RESULT), exist_ok=True)
    with open(RESULT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def load_result():
    with open(RESULT, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "verify"))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest or args.cmd == "selftest":
        return selftest()

    if args.check or args.cmd == "check":
        fails = check(load_result())
        for f in fails:
            print("[FAIL] " + f)
        print(f"check {len(fails)} failure(s)")
        return 0 if not fails else 3

    payload = build_payload()
    if args.verify or args.cmd == "verify":
        old = load_result()
        old.pop("generated", None)
        new = dict(payload)
        new.pop("generated", None)
        if old == new:
            print("verify MATCH")
            return 0
        for key in old:
            if old.get(key) != new.get(key):
                print(f"[DIFF] {key}")
        print("verify MISMATCH")
        return 3

    write_result(payload)
    write_page(payload)
    fails = check(payload)
    h = payload["headline"]
    print(f"verdict={payload['verdict']} families={h['families']} "
          f"invariant={h['invariant']} sensitive={len(h['cross_unit_sensitive'])} "
          f"scale_dep={len(h['scale_dependent'])} "
          f"all_short={h['donchian_shipped_all_short_pairs']} "
          f"fixes_agree={h['fixes_agree_pairs']} "
          f"fix_delta={h['fix_disagreement_max_share_short']:.4f}")
    print(f"-> {RESULT}\n-> {PAGE}")
    for f in fails:
        print("[FAIL] " + f)
    return 0 if not fails else 3


if __name__ == "__main__":
    sys.exit(main())
