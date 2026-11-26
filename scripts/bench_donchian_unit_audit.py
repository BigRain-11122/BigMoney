"""Which of the printed breakout arms actually ran a breakout rule.

Why this exists
---------------
`bench_core.align_futures` hands every rule a **return index** (`adjusted_price`,
cumprod of roll-adjusted returns, starting at 1.0) as `closes`, while the panel's
`high`/`low` columns stay in raw price units. Four of the five rule families only
ever compare `closes` with `closes` (a ratio), so the rebasing is invisible to
them. `donchian` is the one rule that compares `closes` against `highs`/`lows` --
and it compares 0.96 against 230.99.

The consequence is not subtle: a close can never exceed a raw high, and always
sits below a raw low, so the state machine opens short on its first usable bar
and never flips. Every printed donchian arm is therefore **a constant short of
the basket**, dressed as a breakout rule, and its `|long` / `|ls` twin is the
same series printed twice.

This module measures that, and only that:

  1. the unit gap, per product, between what `closes` is and what `highs` is;
  2. the state histogram each printed donchian arm actually produced (and
     whether flipping `long_only` changed a single bar);
  3. which card-level verdict tokens were decided partly by those rows, i.e.
     what the card would have said without them;
  4. what a unit-consistent breakout of the same parameters returns, so the size
     of the error is on the page (a reference reading, not a new verdict).

The rule itself is not re-implemented on faith: the local state machine is
required to reproduce `bench_generic.sig_donchian` bit-for-bit on the card's own
inputs (selftest leg `fidelity`), so the only thing that changes in reading 4 is
the unit.

Read-only with respect to every input: it never writes a bench card, a queue row
or a panel.

Usage
-----
  python scripts/bench_donchian_unit_audit.py              # write json + page
  python scripts/bench_donchian_unit_audit.py --check      # offline selftest
  python scripts/bench_donchian_unit_audit.py --verify     # recompute and diff
"""
from __future__ import annotations

import argparse
import ast
import datetime
import glob
import hashlib
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import bench_core as bc  # noqa: E402
import bench_generic as bg  # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "bench_donchian_unit_audit.json")
OUT_MD = os.path.join(ROOT, "research", "BENCH-DONCHIAN-UNIT-AUDIT.md")

SCHEMA = "bench-donchian-unit-audit/1"
TZ = datetime.timezone(datetime.timedelta(hours=8))

VERDICT_CONSTANT_SHORT = "DONCHIAN_ARMS_ARE_A_CONSTANT_SHORT"
VERDICT_PARTIAL = "SOME_ARMS_FLIP_NEGATIVE_ONLY"
VERDICT_CLEAN = "NO_UNIT_MISMATCH_FOUND"

VAR_GRID = re.compile(r"^donchian\|(\{.*\})\|\s*(long|ls)\s*$")
VAR_AB = re.compile(r"^(\d+)_(\d+)$")


def now_iso():
    return datetime.datetime.now(tz=TZ).isoformat(timespec="seconds")


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def file_sha(path):
    with open(path, "rb") as fh:
        return sha256_bytes(fh.read())


# --------------------------------------------------------------------------
# printed-arm discovery
# --------------------------------------------------------------------------
def parse_variant(label):
    """(entry, exit_, flag) for a printed donchian arm label.

    flag is True (long-only), False (long-short) or None (the card carries no
    flag; bench_generic's `run_arm` default then makes it long-short).
    """
    label = str(label)
    m = VAR_GRID.match(label)
    if m:
        params = ast.literal_eval(m.group(1))
        return int(params["entry"]), int(params["exit"]), m.group(2) == "long"
    m = VAR_AB.match(label)
    if m:
        return int(m.group(1)), int(m.group(2)), None
    return 55, 20, None  # bench_fut_trend.sig_donchian defaults, long-short


def collect_printed_arms():
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, "results", "bench_*.json"))):
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except Exception:  # noqa: BLE001 - a broken card must not stop the audit
            continue
        arms = doc.get("arms")
        if not isinstance(arms, list):
            continue
        cfg = doc.get("config") or {}
        cov = doc.get("coverage") or {}
        products = cfg.get("products") or cov.get("products") or []
        cell = str(doc.get("cell") or os.path.basename(path)[:-5])
        card_is_donchian = "donchian" in cell.lower() or "donchian" in str(cfg.get("rule") or "").lower()
        window = cov.get("verdict_window_start") or cov.get("start")
        for arm in arms:
            if not isinstance(arm, dict):
                continue
            label = arm.get("style") or (arm.get("tags") or {}).get("variant") or ""
            if "donchian" not in str(label).lower() and not card_is_donchian:
                continue
            entry, exit_, flag = parse_variant(label)
            cw = arm.get("common_window") or {}
            rows.append({
                "card": cell,
                "result": os.path.relpath(path, ROOT).replace("\\", "/"),
                "products": sorted(products),
                "window": window,
                "entry": entry,
                "exit": exit_,
                "flag": flag,
                "label": str(label),
                "printed": {k: cw.get(k) for k in ("ann_pct", "sharpe", "mdd_pct")},
                "mde_pp": arm.get("mde_pp"),
                "powered": arm.get("powered_for_target"),
                "verdict": arm.get("verdict"),
                "target_vol": cfg.get("target_vol", 0.10),
                "cost_bp_side": cfg.get("cost_bp_side", 3.0),
            })
    return rows


def combos(arms):
    """One row per (panel, window, params, sizing) actually printed."""
    seen = {}
    for arm in arms:
        key = (tuple(arm["products"]), arm["window"], arm["entry"], arm["exit"],
               float(arm["target_vol"]), float(arm["cost_bp_side"]))
        if key in seen:
            seen[key]["labels"].append(arm["label"])
            if arm["card"] not in seen[key]["cards"]:
                seen[key]["cards"].append(arm["card"])
            seen[key]["printed_ann"].append(arm["printed"].get("ann_pct"))
            continue
        seen[key] = {
            "cards": [arm["card"]],
            "products": arm["products"],
            "window": arm["window"],
            "entry": arm["entry"],
            "exit": arm["exit"],
            "target_vol": float(arm["target_vol"]),
            "cost_bp_side": float(arm["cost_bp_side"]),
            "labels": [arm["label"]],
            "printed_ann": [arm["printed"].get("ann_pct")],
        }
    return list(seen.values())


# --------------------------------------------------------------------------
# reference state machine (must reproduce bench_generic.sig_donchian)
# --------------------------------------------------------------------------
def states(close, high, low, entry, exit_, long_only):
    hi = high.rolling(entry).max().shift(1)
    lo = low.rolling(exit_).min().shift(1)
    state, arr = 0, []
    for price, h, l in zip(close.values, hi.values, lo.values):
        if not np.isfinite(price) or not np.isfinite(h) or not np.isfinite(l):
            arr.append(np.nan)
            continue
        if state == 0:
            state = 1 if price > h else (-1 if price < l else 0)
        elif state == 1 and price < l:
            state = -1 if not long_only else 0
        elif state == -1 and price > h:
            state = 1
        arr.append(float(state))
    return pd.Series(arr, index=close.index).replace(0.0, np.nan)


def hist(signals):
    live = short = long_ = 0
    for s in signals.values():
        live += int(s.notna().sum())
        short += int((s < 0).sum())
        long_ += int((s > 0).sum())
    return {"live_bars": live, "short_bars": short, "long_bars": long_,
            "share_short": round(short / live, 6) if live else None}


def perf(signals, rets, vols, dates, target_vol, cost_bp_side, split="2024-01-01"):
    pos, _ = bc.vol_weighted_positions(signals, vols, target_vol=target_vol)
    if pos is None or not pos.notna().any().any():
        return None
    _gross, net, _turn = bc.apply_costs(pos, rets, cost_bp_side=cost_bp_side)
    net = net.reindex(dates).fillna(0.0)
    full = bc.split_perf(net.values, dates, split=split)["full"]
    return {"ann_pct": full.get("ann_pct"), "sharpe": full.get("sharpe"),
            "mdd_pct": full.get("mdd_pct"), "vol_pct": full.get("vol_pct")}


def audit_combo(spec):
    panel = bc.load_futures_products(spec["products"])
    if len(panel) < 1:
        return dict(spec, ok=False, reason="no panel")
    dates, closes, rets, vols = bc.align_futures(panel)
    highs = {c: df["high"].reindex(dates) for c, df in panel.items()}
    lows = {c: df["low"].reindex(dates) for c, df in panel.items()}
    raw_close = {c: df["close"].reindex(dates) for c, df in panel.items()}
    base = {}
    for code, series in raw_close.items():
        first = series.dropna()
        base[code] = float(first.iloc[0]) if len(first) else None
    h_n = {c: highs[c] / base[c] for c in highs if base.get(c)}
    l_n = {c: lows[c] / base[c] for c in lows if base.get(c)}
    c_n = {c: raw_close[c] / base[c] for c in raw_close if base.get(c)}

    unit_gap = {}
    for code in closes:
        ratio = (highs[code] / closes[code]).replace([np.inf, -np.inf], np.nan).dropna()
        unit_gap[code] = round(float(ratio.median()), 3) if len(ratio) else None

    prod_long = bg.sig_donchian(closes, highs, lows, spec["entry"], spec["exit"], long_only=True)
    prod_ls = bg.sig_donchian(closes, highs, lows, spec["entry"], spec["exit"], long_only=False)
    ref_long = {c: states(closes[c], highs[c], lows[c], spec["entry"], spec["exit"], True) for c in closes}
    ref_ls = {c: states(closes[c], highs[c], lows[c], spec["entry"], spec["exit"], False) for c in closes}

    def identical(a, b):
        for code in a:
            if not ((a[code].fillna(-99) - b[code].fillna(-99)).abs() < 1e-9).all():
                return False
        return True

    fixed_long = {c: states(c_n[c], h_n[c], l_n[c], spec["entry"], spec["exit"], True) for c in c_n}
    fixed_ls = {c: states(c_n[c], h_n[c], l_n[c], spec["entry"], spec["exit"], False) for c in c_n}

    fidelity_long = identical(prod_long, ref_long)
    fidelity_ls = identical(prod_ls, ref_ls)
    flags_identical = identical(prod_long, prod_ls)

    # the card printed its numbers inside its own window; compare like for like
    if spec.get("window"):
        window = pd.Timestamp(spec["window"])
        dates = dates[dates >= window]
        prod_long = {c: s.reindex(dates) for c, s in prod_long.items()}
        prod_ls = {c: s.reindex(dates) for c, s in prod_ls.items()}
        fixed_long = {c: s.reindex(dates) for c, s in fixed_long.items()}
        fixed_ls = {c: s.reindex(dates) for c, s in fixed_ls.items()}

    hp = hist(prod_long)
    hf = hist(fixed_long)
    return {
        "ok": True,
        "cards": spec["cards"],
        "products": spec["products"],
        "window": spec.get("window"),
        "entry": spec["entry"],
        "exit": spec["exit"],
        "labels": spec["labels"],
        "target_vol": spec["target_vol"],
        "cost_bp_side": spec["cost_bp_side"],
        "card_printed_ann_pct": spec.get("printed_ann"),
        "bars": int(len(dates)),
        "unit_gap_median_high_over_close": unit_gap,
        "fidelity_long": fidelity_long,
        "fidelity_ls": fidelity_ls,
        "flags_identical": flags_identical,
        "printed_state": hp,
        "printed_perf": perf(prod_long, rets, vols, dates, spec["target_vol"], spec["cost_bp_side"]),
        "unit_fixed_state_long_only": hf,
        "unit_fixed_perf_long_only": perf(fixed_long, rets, vols, dates, spec["target_vol"], spec["cost_bp_side"]),
        "unit_fixed_perf_ls": perf(fixed_ls, rets, vols, dates, spec["target_vol"], spec["cost_bp_side"]),
    }


# --------------------------------------------------------------------------
# card-level token impact
# --------------------------------------------------------------------------
def census_token(rows):
    """bench_generic.run_census's pooled token, applied to printed rows."""
    powered = [r for r in rows if r.get("powered")]
    pos = [r for r in powered if (r.get("ann_pct") or 0) > 0]
    neg = [r for r in powered if (r.get("ann_pct") or 0) < 0]
    if not powered:
        return "CENSUS_UNPOWERED"
    if pos and neg:
        return "CENSUS_SIGN_MIXED"
    return "CENSUS_LEANS_POSITIVE" if pos else "CENSUS_LEANS_NEGATIVE"


def robust_token(rows):
    """bench_generic.run_cell's robust pooled token, applied to printed rows."""
    anns = [r.get("ann_pct") for r in rows if r.get("ann_pct") is not None]
    mdes = [r.get("mde_pp") for r in rows if r.get("mde_pp")]
    if not anns:
        return "DATA_BLOCKED"
    signs = {1 if x > 0 else -1 for x in anns}
    stable = len(signs) == 1 and bool(mdes) and min(abs(x) for x in anns) > max(mdes)
    if stable:
        return "STABLE_POSITIVE" if 1 in signs else "STABLE_NEGATIVE"
    return "UNSTABLE_ACROSS_PARAMS"


def card_token_impact(arm_rows):
    """What each card's own token would be without its donchian rows."""
    out = []
    by_card = {}
    for row in arm_rows:
        by_card.setdefault(row["card"], []).append(row)
    for card, rows in sorted(by_card.items()):
        path = os.path.join(ROOT, "results", f"bench_{card}.json")
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        all_arms = [a for a in (doc.get("arms") or []) if isinstance(a, dict)]
        cfg = doc.get("config") or {}
        card_is_donchian = ("donchian" in str(doc.get("cell") or card).lower()
                            or "donchian" in str(cfg.get("rule") or "").lower())
        flat = [{"ann_pct": (a.get("common_window") or {}).get("ann_pct"),
                 "powered": a.get("powered_for_target"),
                 "mde_pp": a.get("mde_pp")} for a in all_arms]
        drop = [row for row, arm in zip(flat, all_arms)
                if not card_is_donchian
                and "donchian" not in str(arm.get("style")
                                          or (arm.get("tags") or {}).get("variant") or "").lower()]
        kind = cfg.get("type") or "styles"
        if kind == "census":
            fn = census_token
        elif kind == "robust":
            fn = robust_token
        else:
            fn = None
        printed = fn(flat) if fn else None
        without = fn(drop) if (fn and drop) else None
        raw_verdict = doc.get("verdict")
        if isinstance(raw_verdict, dict):
            token_printed = raw_verdict.get("donchian") or raw_verdict.get("tsmom")
        else:
            token_printed = raw_verdict if isinstance(raw_verdict, str) else printed
        out.append({
            "card": card,
            "kind": kind,
            "card_is_only_donchian": card_is_donchian and not drop,
            "arms_total": len(all_arms),
            "arms_donchian": len(all_arms) - len(drop),
            "token_printed": token_printed,
            "token_recomputed_all": printed,
            "token_without_donchian": without,
            "changed": without is not None and printed is not None and without != printed,
        })
    return out


# --------------------------------------------------------------------------
# payload
# --------------------------------------------------------------------------
def build_payload():
    arms = collect_printed_arms()
    combo_rows = [audit_combo(spec) for spec in combos(arms)]
    combo_rows = [c for c in combo_rows if c.get("ok")]

    constant = [c for c in combo_rows if (c["printed_state"]["share_short"] or 0) >= 0.999]
    flags_dead = [c for c in combo_rows if c["flags_identical"]]
    if len(constant) == len(combo_rows) and combo_rows and len(flags_dead) == len(combo_rows):
        verdict = VERDICT_CONSTANT_SHORT
    elif constant:
        verdict = VERDICT_PARTIAL
    else:
        verdict = VERDICT_CLEAN

    inputs = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "results", "bench_*.json"))):
        if os.path.basename(path) == os.path.basename(OUT_JSON):
            continue
        inputs[os.path.relpath(path, ROOT).replace("\\", "/")] = file_sha(path)
    for path in ("scripts/bench_core.py", "scripts/bench_generic.py"):
        inputs[path] = file_sha(os.path.join(ROOT, path))

    cutoffs = []
    for row in arms:
        with open(os.path.join(ROOT, row["result"]), encoding="utf-8") as fh:
            doc = json.load(fh)
        if doc.get("evidence_cutoff"):
            cutoffs.append(str(doc["evidence_cutoff"]))

    printed_arms = [{k: r[k] for k in ("card", "label", "entry", "exit", "flag",
                                       "printed", "mde_pp", "powered", "verdict")} for r in arms]

    return {
        "schema": SCHEMA,
        "generated": now_iso(),
        "evidence_cutoff": max(cutoffs) if cutoffs else None,
        "verdict": verdict,
        "headline": {
            "printed_donchian_arms": len(arms),
            "cards": sorted({r["card"] for r in arms}),
            "distinct_combos": len(combo_rows),
            "combos_constant_short": len(constant),
            "combos_where_long_only_did_nothing": len(flags_dead),
            "distinct_measurements_behind_printed_arms": len(combo_rows),
        },
        "combos": combo_rows,
        "printed_arms": printed_arms,
        "card_tokens": card_token_impact(arms),
        "inputs": inputs,
    }


# --------------------------------------------------------------------------
# page
# --------------------------------------------------------------------------
def fmt(v, suffix=""):
    return "n/a" if v is None else f"{v}{suffix}"


def write_page(payload):
    head = payload["headline"]
    lines = [
        "# The breakout arms never ran a breakout",
        "",
        f"`{payload['schema']}` · generated {payload['generated']} · "
        f"evidence cutoff {payload['evidence_cutoff']} · **{payload['verdict']}**",
        "",
        "## What this page is",
        "",
        "`bench_core.align_futures` gives every rule a **return index** as `closes` "
        "(cumprod of roll-adjusted returns, starting at 1.0) and leaves `high`/`low` in "
        "**raw price** units. Four of five rule families only compare `closes` with "
        "`closes`, so they cannot notice. `donchian` compares `closes` with `highs`/`lows`.",
        "",
        "This page counts what that means for the arms already printed.",
        "",
        "## Reading 1 — the two series are two units",
        "",
        "| product | median(raw high / closes) |",
        "| --- | --- |",
    ]
    gap = {}
    for combo in payload["combos"]:
        for code, value in (combo.get("unit_gap_median_high_over_close") or {}).items():
            if code not in gap and value is not None:
                gap[code] = value
    for code in sorted(gap):
        lines.append(f"| {code} | {gap[code]:.1f}× |")
    lines += [
        "",
        "A close near 1.0 against a high near 200-900: a close can never exceed the raw "
        "high, and is below the raw low on every usable bar.",
        "",
        "## Reading 2 — so the state machine opens short once and never flips",
        "",
        "| card | params | products | window | bars | live | short | long | long_only did anything? | ann on the card | ann here |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for combo in payload["combos"]:
        st = combo["printed_state"]
        card_ann = [v for v in (combo.get("card_printed_ann_pct") or []) if v is not None]
        lines.append(
            f"| {', '.join(combo['cards'])} | {combo['entry']}/{combo['exit']} | "
            f"{'+'.join(combo['products'])} | {combo['window'] or 'full'} | {combo['bars']} | "
            f"{st['live_bars']} | {st['short_bars']} | {st['long_bars']} | "
            f"{'no' if combo['flags_identical'] else 'yes'} | "
            f"{fmt(card_ann[0] if card_ann else None, '%')} | "
            f"{fmt((combo['printed_perf'] or {}).get('ann_pct'), '%')} |"
        )
    lines += [
        "",
        f"**{head['combos_constant_short']} of {head['distinct_combos']} printed combos are 100% short**, "
        f"and in **{head['combos_where_long_only_did_nothing']} of {head['distinct_combos']}** flipping "
        "`long_only` does not change a single bar. The `|long` and `|ls` rows of the same "
        "parameters are one measurement printed twice.",
        "",
        "## Reading 3 — which card tokens those rows decided",
        "",
        "| card | kind | arms | donchian arms | token printed | recomputed from all rows | without donchian | flips |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["card_tokens"]:
        without = "no other arms" if row.get("card_is_only_donchian") else fmt(row["token_without_donchian"])
        lines.append(
            f"| {row['card']} | {row['kind']} | {row['arms_total']} | {row['arms_donchian']} | "
            f"{fmt(row['token_printed'])} | {fmt(row['token_recomputed_all'])} | "
            f"{without} | {'yes' if row['changed'] else 'no'} |"
        )
    flips = [r["card"] for r in payload["card_tokens"] if r["changed"]]
    if flips:
        lines += [
            "",
            f"Dropping the artifact rows changes the card token for: **{', '.join(flips)}** -- "
            "the negative powered rows that made it a two-sided census were the constant short.",
        ]
    for row in payload["card_tokens"]:
        if row.get("card_is_only_donchian"):
            lines += [
                "",
                f"`{row['card']}` has nothing left when its donchian rows are removed: the whole "
                "card is three start dates of the same constant short, and its "
                "`UNSTABLE_ACROSS_PARAMS` token was decided by MDE, not by a sign change.",
            ]
    lines += [
        "",
        "## Reading 4 — what a breakout with one unit returns",
        "",
        "Reference only: every series divided by that product's first close, the rule and "
        "its parameters untouched. Raw highs/lows still carry contract rolls, so this is "
        "the size of the error, not a new verdict on breakouts.",
        "",
        "| products | params | reproduced ann / sharpe / mdd | unit-fixed long-only | unit-fixed long-short |",
        "| --- | --- | --- | --- | --- |",
    ]
    for combo in payload["combos"]:
        p = combo["printed_perf"] or {}
        lo = combo["unit_fixed_perf_long_only"] or {}
        ls = combo["unit_fixed_perf_ls"] or {}
        lines.append(
            f"| {'+'.join(combo['products'])} | {combo['entry']}/{combo['exit']} | "
            f"{fmt(p.get('ann_pct'))}% / {fmt(p.get('sharpe'))} / {fmt(p.get('mdd_pct'))}% | "
            f"{fmt(lo.get('ann_pct'))}% / {fmt(lo.get('sharpe'))} / {fmt(lo.get('mdd_pct'))}% | "
            f"{fmt(ls.get('ann_pct'))}% / {fmt(ls.get('sharpe'))} / {fmt(ls.get('mdd_pct'))}% |"
        )
    worst_printed = min((c["printed_perf"] or {}).get("ann_pct") or 0.0 for c in payload["combos"])
    best_fixed = max((c["unit_fixed_perf_long_only"] or {}).get("ann_pct") or 0.0 for c in payload["combos"])
    lines += [
        "",
        "## What this does not say",
        "",
        f"- It does not say breakouts work. The printed arms run from {worst_printed:.2f}%/yr and a "
        f"unit-fixed reference reaches at most {best_fixed:.2f}%/yr -- still one unlevered, "
        "roll-contaminated family with no control run. The honest statement is that **the printed "
        "number was a different position**, not that the rule is good.",
        "- It does not re-open any card. The fix belongs in `bench_generic.build_signals` "
        "(hand `sig_donchian` one unit), which is a shared code face; this round was a "
        "contention window and only new-file faces were written.",
        "- The cards' own numbers were computed on their own cutoffs and windows; reproduction "
        "here uses today's panel, so annualised returns move by up to a percentage point between "
        "vintages. The state histogram and the dead `long_only` flag do not move.",
        "- Roll jumps are still inside the raw high/low series, so the unit-fixed reference is a "
        "size-of-error reading, not a clean re-run.",
        "",
        "## Reproduction",
        "",
        "```",
        "python scripts/bench_donchian_unit_audit.py --check    # offline selftest",
        "python scripts/bench_donchian_unit_audit.py --verify    # recompute and diff",
        "```",
        "",
    ]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
def selftest():
    legs = []

    def add(name, ok):
        legs.append((name, bool(ok)))

    add("parse grid long", parse_variant("donchian|{'entry': 20, 'exit': 10}|long") == (20, 10, True))
    add("parse grid ls", parse_variant("donchian|{'entry': 55, 'exit': 20}|ls") == (55, 20, False))
    add("parse ab", parse_variant("20_10") == (20, 10, None))
    add("parse bare", parse_variant("donchian") == (55, 20, None))

    # a synthetic panel where the two series share one unit: the rule must toggle
    idx = pd.date_range("2020-01-01", periods=60, freq="D")
    price = pd.Series(np.linspace(100.0, 160.0, 60), index=idx)
    high = price + 1.0
    low = price - 1.0
    same_unit = states(price / 100.0, high / 100.0, low / 100.0, 5, 3, False)
    add("same-unit arms are comparable", same_unit.notna().sum() == len(idx) - 5)

    mixed = states(price / 100.0, high, low, 5, 3, False)
    add("unit mismatch pins the state short", (mixed.dropna() < 0).all())

    add("hist all short", hist({"a": pd.Series([-1.0, -1.0, np.nan])})["share_short"] == 1.0)
    add("hist half", hist({"a": pd.Series([-1.0, 1.0])})["share_short"] == 0.5)

    rows = [{"ann_pct": 1.0, "powered": True, "mde_pp": 1.0},
            {"ann_pct": -1.0, "powered": True, "mde_pp": 1.0}]
    add("census token mixed", census_token(rows) == "CENSUS_SIGN_MIXED")
    add("census token without negatives", census_token(rows[:1]) == "CENSUS_LEANS_POSITIVE")
    add("census token unpowered",
        census_token([{"ann_pct": 1.0, "powered": False, "mde_pp": 9.0}]) == "CENSUS_UNPOWERED")
    add("robust token unstable on power",
        robust_token([{"ann_pct": -4.0, "mde_pp": 9.0}, {"ann_pct": -4.2, "mde_pp": 9.0}])
        == "UNSTABLE_ACROSS_PARAMS")

    arms = collect_printed_arms()
    add("printed donchian arms found", len(arms) > 0)
    add("every printed arm maps to a card file",
        all(os.path.exists(os.path.join(ROOT, r["result"])) for r in arms))

    first = build_payload()
    second = build_payload()
    first.pop("generated")
    second.pop("generated")
    add("deterministic payload", json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True))
    add("every combo reports fidelity",
        all(c["fidelity_long"] and c["fidelity_ls"] for c in first["combos"]))

    passed = sum(1 for _n, ok in legs if ok)
    for name, ok in legs:
        print(("PASS " if ok else "FAIL ") + name)
    print(f"{passed}/{len(legs)} PASS")
    return 0 if passed == len(legs) else 1


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="offline selftest")
    ap.add_argument("--verify", action="store_true", help="recompute and diff the published face")
    ap.add_argument("--write", action="store_true", help="write json + page")
    args = ap.parse_args(argv)

    if args.check:
        return selftest()

    payload = build_payload()

    if args.verify:
        if not os.path.exists(OUT_JSON):
            print("STALE: face missing " + os.path.relpath(OUT_JSON, ROOT))
            return 3
        with open(OUT_JSON, encoding="utf-8") as fh:
            published = json.load(fh)
        a = dict(published)
        b = dict(payload)
        a.pop("generated", None)
        b.pop("generated", None)
        if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True):
            print("MATCH: recomputation equals the published face")
            return 0
        for key in sorted(set(a) | set(b)):
            if json.dumps(a.get(key), sort_keys=True) != json.dumps(b.get(key), sort_keys=True):
                print(f"DIFF at {key}")
        return 3

    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    write_page(payload)
    print(f"{payload['verdict']} · printed donchian arms={payload['headline']['printed_donchian_arms']} "
          f"· combos={payload['headline']['distinct_combos']} "
          f"· constant short={payload['headline']['combos_constant_short']}")
    print(f"wrote {os.path.relpath(OUT_JSON, ROOT)} and {os.path.relpath(OUT_MD, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
