"""How many live threads are actually alive, and which arm did the bar throw away.

Why this exists
---------------
`bench_verdict_book.py` (r2140) counted **6 CANDIDATE rows** and that number went
straight into the round report. Opening the two evidence files shows the six are
not six things: `robust_tsmom_commodity`'s `120d`/`250d` arms and
`census_commodity`'s `tsmom|{lookback:120,skip:21}|ls` / `|ls` 250 arms print the
same annual return, the same Sharpe and the same drawdown to the last digit, on
the same three products, the same 4,597 bars and the same evidence date. One
measurement, two cards, counted twice.

Second miss: the same census card contains two arms the card stamped `NO_EDGE`
that beat its own promoted arms on **Sharpe and drawdown both** -- the 250-day
long-only arm returns 4.56%/yr with Sharpe 0.754 and a -13.70% drawdown against
the promoted long-short arm's 5.24%/0.671/-18.88%. It was rejected by a
`target_edge_pp = 5.0` bar that only looks at return. That is a legitimate bar,
but a reader of the verdict book is never told the arm exists.

So this module answers three questions mechanically and only mechanically:

  1. how many *distinct measurements* are still alive (dedupe by the numbers and
     the panel, never by arm name);
  2. which cards are quoting the same measurement as evidence twice;
  3. which non-live arms beat a live arm of their own card on both Sharpe and
     drawdown, and which bar in that card's own `criteria` rejected them.

It does not re-judge anything. An arm that loses on return and wins on risk is
not "better"; it is a different risk budget, and the point is only that the
reader was not told about it (a missing face is not a zero -- r98 family).

Read-only with respect to every input: it never writes the bank, the queue, or
any bench result.

Usage
-----
  python scripts/bench_live_thread_dedupe.py            # write json + page
  python scripts/bench_live_thread_dedupe.py --check    # selftest, offline
  python scripts/bench_live_thread_dedupe.py --verify   # recompute and diff
"""
from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OUT_JSON = os.path.join(ROOT, "results", "bench_live_thread_dedupe.json")
OUT_MD = os.path.join(ROOT, "research", "BENCH-LIVE-THREAD-DEDUPE.md")

SCHEMA = "bench_live_thread_dedupe.v1"
TZ = datetime.timezone(datetime.timedelta(hours=8))

# verdict tokens that mean "this arm is still alive". Closed set: an unknown
# token must land in OTHER and be printed, never silently dropped.
LIVE_TOKENS = ("GO", "SIGNIFICANT", "HOLD")
SELF_OUTPUTS = ("bench_live_thread_dedupe.json",)

# a measurement is the numbers plus the panel they were computed on
NUMBER_KEYS = ("ann_pct", "sharpe", "mdd_pct")


def now_iso():
    return datetime.datetime.now(TZ).replace(microsecond=0).isoformat()


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def digest_of(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    except OSError:
        return None


def _round(value, nd):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return round(float(value), nd)


def measurement_key(rec):
    """Identity of a measurement: panel + numbers. Never the arm name.

    Two cards naming the same rule differently must collapse; two cards naming
    the same rule identically but on different bars must not."""
    panel = (tuple(rec.get("products") or ()), rec.get("bars"), rec.get("cutoff"))
    nums = (
        _round(rec.get("ann_pct"), 2),
        _round(rec.get("sharpe"), 3),
        _round(rec.get("mdd_pct"), 2),
    )
    if any(v is None for v in nums):
        return None
    return panel + nums


def arm_records(card_id, payload, path):
    """Flatten one card into arm records. Missing numbers stay missing."""
    config = payload.get("config") if isinstance(payload.get("config"), dict) else {}
    coverage = payload.get("coverage") if isinstance(payload.get("coverage"), dict) else {}
    products = config.get("products") or coverage.get("products") or []
    bars = coverage.get("bars")
    cutoff = payload.get("evidence_cutoff")
    out = []
    for arm in payload.get("arms") or []:
        if not isinstance(arm, dict):
            continue
        tags = arm.get("tags") if isinstance(arm.get("tags"), dict) else {}
        cw = arm.get("common_window") if isinstance(arm.get("common_window"), dict) else {}
        oos = arm.get("oos_2024_after") if isinstance(arm.get("oos_2024_after"), dict) else {}
        out.append({
            "card": card_id,
            "source": path,
            "variant": tags.get("variant"),
            "verdict": arm.get("verdict"),
            "products": list(products),
            "bars": bars,
            "cutoff": cutoff,
            "ann_pct": cw.get("ann_pct"),
            "sharpe": cw.get("sharpe"),
            "mdd_pct": cw.get("mdd_pct"),
            "vol_pct": cw.get("vol_pct"),
            "t_stat": cw.get("t_stat"),
            "turnover": arm.get("turnover_per_year"),
            "oos_ann_pct": oos.get("ann_pct"),
            "target_edge_pp": (config.get("criteria") or payload.get("criteria") or {}).get("target_edge_pp")
            if isinstance(config.get("criteria") or payload.get("criteria"), dict) else None,
        })
    return out


def is_live(rec):
    return str(rec.get("verdict") or "").upper() in LIVE_TOKENS


def dedupe(records):
    """Group records that are the same measurement. Order-independent."""
    groups = {}
    for rec in records:
        key = measurement_key(rec)
        if key is None:
            continue
        groups.setdefault(key, []).append(rec)
    dups = []
    for key, members in groups.items():
        cards = sorted({m["card"] for m in members})
        if len(cards) < 2:
            continue
        dups.append({
            "cards": cards,
            "arms": sorted({str(m.get("variant")) for m in members}),
            "products": list(key[0]),
            "bars": key[1],
            "cutoff": key[2],
            "ann_pct": key[3],
            "sharpe": key[4],
            "mdd_pct": key[5],
            "rows": len(members),
        })
    dups.sort(key=lambda d: (-len(d["cards"]), d["cards"]))
    return dups


def distinct_live(records):
    """Live arms collapsed to distinct measurements, with the cards that quote them."""
    live = [r for r in records if is_live(r)]
    seen = {}
    groups = {}
    for rec in live:
        key = measurement_key(rec)
        if key is None:
            # live but unreadable numbers: keep it visible rather than merging it
            key = ("UNREADABLE", rec["card"], str(rec.get("variant")))
        groups.setdefault(key, []).append(rec)
        slot = seen.setdefault(key, {
            "products": rec.get("products"),
            "bars": rec.get("bars"),
            "cutoff": rec.get("cutoff"),
            "ann_pct": rec.get("ann_pct"),
            "sharpe": rec.get("sharpe"),
            "mdd_pct": rec.get("mdd_pct"),
            "vol_pct": rec.get("vol_pct"),
            "oos_ann_pct": rec.get("oos_ann_pct"),
            "turnover": rec.get("turnover"),
            "arms": [],
            "cards": [],
            "verdicts": [],
        })
        if str(rec.get("variant")) not in slot["arms"]:
            slot["arms"].append(str(rec.get("variant")))
        if rec["card"] not in slot["cards"]:
            slot["cards"].append(rec["card"])
        if str(rec.get("verdict")) not in slot["verdicts"]:
            slot["verdicts"].append(str(rec.get("verdict")))
    out = list(seen.values())
    for s in out:
        s["cards"].sort()
        s["arms"].sort()
    # one measurement may be quoted by two cards that print different column
    # sets (the census card drops vol_pct, the robust card carries it). Fill a
    # blank from the group rather than printing "—" for a number we do have.
    for key, members in groups.items():
        slot = seen.get(key)
        if slot is None:
            continue
        for k in ("vol_pct", "turnover", "oos_ann_pct", "bars", "cutoff"):
            if slot.get(k) is None:
                for m in members:
                    if m.get(k) is not None:
                        slot[k] = m[k]
                        break
    out.sort(key=lambda s: (s["cards"][0], s["arms"][0]))
    return out


def missed_arms(records):
    """Non-live arms that beat a live arm of their own card on Sharpe AND drawdown.

    Both axes are required: an arm that only wins on Sharpe has a different
    volatility, one that only wins on drawdown has a different tail. Requiring
    both is the conservative reading and keeps the list short enough to read."""
    per_card = {}
    for rec in records:
        per_card.setdefault(rec["card"], []).append(rec)
    out = []
    for card_id, members in sorted(per_card.items()):
        live = [m for m in members if is_live(m)]
        if not live:
            continue
        for cand in members:
            if is_live(cand):
                continue
            c_sr, c_mdd = cand.get("sharpe"), cand.get("mdd_pct")
            if c_sr is None or c_mdd is None:
                continue
            beaten = []
            for win in live:
                w_sr, w_mdd = win.get("sharpe"), win.get("mdd_pct")
                if w_sr is None or w_mdd is None:
                    continue
                if c_sr > w_sr and c_mdd > w_mdd:
                    beaten.append(win)
            if not beaten:
                continue
            # compare against the strongest live arm it beats: the point is
            # "it is not worse than what was promoted", so use the best one
            win = max(beaten, key=lambda w: w.get("sharpe") or 0.0)
            out.append({
                "card": card_id,
                "source": cand["source"],
                "arm": cand.get("variant"),
                "verdict": cand.get("verdict"),
                "ann_pct": cand.get("ann_pct"),
                "sharpe": c_sr,
                "mdd_pct": c_mdd,
                "turnover": cand.get("turnover"),
                "oos_ann_pct": cand.get("oos_ann_pct"),
                "beats_arm": win.get("variant"),
                "beats_ann_pct": win.get("ann_pct"),
                "beats_sharpe": win.get("sharpe"),
                "beats_mdd_pct": win.get("mdd_pct"),
                "beats_turnover": win.get("turnover"),
                "delta_ann_pp": _round((cand.get("ann_pct") or 0.0) - (win.get("ann_pct") or 0.0), 2)
                if isinstance(cand.get("ann_pct"), (int, float)) and isinstance(win.get("ann_pct"), (int, float)) else None,
                "delta_sharpe": _round(c_sr - (win.get("sharpe") or 0.0), 3),
                "delta_mdd_pp": _round(c_mdd - (win.get("mdd_pct") or 0.0), 2),
                "rejecting_bar": cand.get("target_edge_pp"),
            })
    out.sort(key=lambda m: (-(m["delta_sharpe"] or 0.0), m["card"], str(m["arm"])))
    return out


def flat_live_cards(cards):
    """Cards that answer at card level and carry no arms[] at all.

    Two of the six rows in the answer book are like this (basis_timing_size,
    basis_timing_perm): one verdict, no arm list. Reading only `arms` would make
    them vanish, which is the same sin this module is auditing -- a face that is
    not printed is not a zero."""
    out = []
    for card_id, payload, path in cards:
        if isinstance(payload.get("arms"), list) and payload["arms"]:
            continue
        verdict = str(payload.get("verdict") or "").upper()
        if verdict not in LIVE_TOKENS:
            continue
        products = payload.get("products") if isinstance(payload.get("products"), dict) else {}
        rows = []
        for name, blk in sorted(products.items()):
            if not isinstance(blk, dict):
                continue
            # some cards nest the numbers one level down (`weighted: {...}`)
            inner = blk.get("weighted") if isinstance(blk.get("weighted"), dict) else blk
            rows.append({
                "product": name,
                "ann_pct": inner.get("net_ann_pct",
                                     inner.get("weighted_ann_pct",
                                               inner.get("carry_ann_pct",
                                                         inner.get("weighted_carry_ann_pct")))),
                "mdd_pct": inner.get("carry_mdd_pct", inner.get("mdd_pct")),
                "bars": blk.get("bars"),
            })
        out.append({
            "card": card_id,
            "source": path,
            "verdict": verdict,
            "cutoff": payload.get("evidence_cutoff"),
            "per_product": rows,
        })
    out.sort(key=lambda c: c["card"])
    return out


def build(cards):
    """cards = [(card_id, payload, path)]. Pure: no I/O."""
    records = []
    for card_id, payload, path in cards:
        records.extend(arm_records(card_id, payload, path))
    cutoffs = [r["cutoff"] for r in records if r.get("cutoff")]
    cutoffs += [c["cutoff"] for c in flat_live_cards(cards) if c.get("cutoff")]
    unknown = sorted({str(r.get("verdict")) for r in records if not is_live(r)
                      and str(r.get("verdict") or "").upper() not in ("NO_EDGE",)})
    payload = {
        "schema": SCHEMA,
        "generated": now_iso(),
        "evidence_cutoff": max(cutoffs) if cutoffs else None,
        "cards_examined": sorted({c[0] for c in cards}),
        "arms_examined": len(records),
        "live_rows": sum(1 for r in records if is_live(r)),
        "live_measurements": distinct_live(records),
        "live_card_level": flat_live_cards(cards),
        "duplicate_measurements": dedupe(records),
        "missed_arms": missed_arms(records),
        "other_verdict_tokens": unknown,
        "sources": sorted({r["source"] for r in records}),
    }
    return payload


def collect_cards():
    paths = sorted(glob.glob(os.path.join(ROOT, "results", "bench_*.json")))
    out = []
    for path in paths:
        if os.path.basename(path) in SELF_OUTPUTS:
            continue
        try:
            payload = load(path)
        except (OSError, ValueError):
            continue
        if not isinstance(payload, dict):
            continue
        # a card may answer at card level with no arms[] at all; dropping those
        # here is exactly the "missing face read as zero" defect
        if not isinstance(payload.get("arms"), list) and not payload.get("verdict"):
            continue
        card_id = payload.get("cell") or os.path.basename(path)[len("bench_"):-len(".json")]
        out.append((str(card_id), payload, os.path.relpath(path, ROOT).replace("\\", "/")))
    return out


def render_md(payload):
    L = []
    L.append("# 还有几条活口：判词册的 6 条 CANDIDATE 去重后剩下几条，以及被收益门扔掉的那条臂")
    L.append("")
    L.append("generated %s | evidence_cutoff %s | 卡片 %d · 臂 %d | 活口行 %d + 卡级活口 %d → **distinct 测量 %d**"
             % (payload["generated"], payload["evidence_cutoff"],
                len(payload["cards_examined"]), payload["arms_examined"],
                payload["live_rows"], len(payload["live_card_level"]),
                len(payload["live_measurements"]) + len(payload["live_card_level"])))
    L.append("")
    L.append("读法：一条「活口」= 一个测量（同一面板上的同一年化/夏普/回撤）。"
             "两张卡片印出逐位相同的读数时，它们证明的是跑了同一条规则同一个面板，"
             "**不是独立复算，不能当两次证据**。")
    L.append("")
    L.append("## 一、还活着的测量（去重后）")
    L.append("")
    L.append("### 1a 有臂的卡片（按臂去重）")
    L.append("")
    L.append("| 卡 | 臂 | 年化 | 夏普 | 回撤 | 波动 | 换手/年 | 样本外年化 | 判词 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for m in payload["live_measurements"]:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            _cell(" / ".join(m["cards"])), _cell(" / ".join(m["arms"])),
            _fmt(m["ann_pct"]), _fmt(m["sharpe"]), _fmt(m["mdd_pct"]), _fmt(m["vol_pct"]),
            _fmt(m["turnover"]), _fmt(m["oos_ann_pct"]), " / ".join(m["verdicts"])))
    L.append("")
    if payload["live_card_level"]:
        L.append("### 1b 卡级活口（这些卡没有 arms[]，只有一句判词 → 分母会少算）")
        L.append("")
        L.append("| 卡 | 判词 | 截止 | 逐品种读数 |")
        L.append("|---|---|---|---|")
        for c in payload["live_card_level"]:
            bits = []
            for r in c["per_product"]:
                bits.append("%s %s 年化 / 回撤 %s / %s bar"
                            % (r["product"], _fmt(r["ann_pct"]), _fmt(r["mdd_pct"]), _fmt(r["bars"])))
            L.append("| %s | %s | %s | %s |" % (c["card"], c["verdict"], _fmt(c["cutoff"]),
                                               "；".join(bits) or "—"))
        L.append("")
        L.append("这一节存在的理由：只读 `arms[]` 的审计会把这两条活口读成不存在——"
                 "**缺面不是零**。它们的形状与 1a 不同，所以不能并进同一张表，也不能假装它们已经被算进去。")
        L.append("")
    L.append("## 二、同一测量被两张卡片各印一次")
    L.append("")
    if payload["duplicate_measurements"]:
        L.append("| 卡 | 臂 | 面板 | 年化 | 夏普 | 回撤 |")
        L.append("|---|---|---|---|---|---|")
        for d in payload["duplicate_measurements"]:
            L.append("| %s | %s | %s × %s bar @ %s | %s | %s | %s |" % (
                _cell(" / ".join(d["cards"])), _cell(" / ".join(d["arms"])),
                "+".join(d["products"]), d["bars"], d["cutoff"],
                _fmt(d["ann_pct"]), _fmt(d["sharpe"]), _fmt(d["mdd_pct"])))
        L.append("")
        L.append("这不是「两个独立来源互相印证」，是同一笔读数被记账两次；"
                 "把 6 当 6 条活口汇报，等于把同一件事卖两遍。")
    else:
        L.append("本轮没有跨卡重复。")
    L.append("")
    L.append("## 三、被自己卡片的收益门扔掉、但风险两项都更好的臂")
    L.append("")
    if payload["missed_arms"]:
        L.append("判据：同一张卡片里，判词不是活的臂，夏普**和**回撤**同时**优于一条活臂。")
        L.append("")
        L.append("| 卡 | 被扔掉的臂 | 判词 | 年化 | 夏普 | 回撤 | 换手 | 对比被选中的臂 | 差（年化/夏普/回撤） | 拒收的门 |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for m in payload["missed_arms"]:
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s (%s/%s/%s) | %+0.2fpp / %+0.3f / %+0.2fpp | %s |" % (
                m["card"], _cell(m["arm"]), m["verdict"],
                _fmt(m["ann_pct"]), _fmt(m["sharpe"]), _fmt(m["mdd_pct"]), _fmt(m["turnover"]),
                _cell(m["beats_arm"]), _fmt(m["beats_ann_pct"]), _fmt(m["beats_sharpe"]), _fmt(m["beats_mdd_pct"]),
                m["delta_ann_pp"] or 0.0, m["delta_sharpe"] or 0.0, m["delta_mdd_pp"] or 0.0,
                ("target_edge_pp=%s" % _fmt(m["rejecting_bar"])) if m["rejecting_bar"] is not None else "未在卡片 criteria 里找到收益门"))
        L.append("")
        L.append("这些臂**不是更优**，是风险预算不同（少一条空头腿、换手更低）。"
                 "问题只有一个：读者从来没被告诉它存在过——卡片的门只量收益，"
                 "于是「用 0.6pp 年化换 0.09 夏普和 5pp 回撤」这个交换在页面上根本没有出现。")
    else:
        L.append("本轮没有被扔掉的臂满足双轴条件。")
    L.append("")
    if payload["other_verdict_tokens"]:
        L.append("## 四、读不懂的判词词面（原样列出，不猜测）")
        L.append("")
        L.append(", ".join("`%s`" % t for t in payload["other_verdict_tokens"]))
        L.append("")
    L.append("## 五、诚实边界")
    L.append("")
    L.append("1. 去重靠「面板 + 三个数逐位相同」，所以**同一条规则跑在两个不完全相同的面板上会被算成两条**；"
             "反过来，两条不同规则碰巧给出同样的三个数，会被并成一条（本册里前者更可能，因为它带着同一份 4,597 bar）。")
    L.append("2. 只读各卡片自己的 `arms[].common_window` 与 `criteria`，不重算任何收益、不重判任何门。")
    L.append("3. 「被扔掉的臂」只做双轴（夏普与回撤同时更好）筛选，不构成推荐；"
             "要变成推荐必须补敞口口径、成本口径与样本外一致性，那是另开票的事。")
    L.append("4. 本册不回答「该做哪条」，只回答「现在有几件事是真的、有几件被印了两遍、有几件没被印出来」。")
    L.append("")
    return "\n".join(L)


def _cell(value):
    """Markdown table cell. Arm names in this corpus literally contain '|'
    (`tsmom|{'lookback': 120, 'skip': 21}|ls`), and an unescaped pipe silently
    splits the row into the wrong columns."""
    if value is None:
        return "—"
    return str(value).replace("|", "\\|")


def _fmt(v):
    if v is None:
        return "—"
    if isinstance(v, float):
        return ("%.3f" % v).rstrip("0").rstrip(".") if abs(v) < 1000 else "%.1f" % v
    return str(v)


# ---------------------------------------------------------------- selftest
def _card(cell, verdict=None, products=("AU", "RB"), bars=100, cutoff="2026-01-01", crit=None):
    p = {
        "cell": cell,
        "evidence_cutoff": cutoff,
        "config": {"products": list(products), "criteria": crit or {}},
        "coverage": {"bars": bars, "products": list(products)},
        "arms": [],
    }
    return p


def _arm(variant, verdict, ann, sr, mdd, turnover=None, oos=None):
    return {
        "tags": {"variant": variant},
        "verdict": verdict,
        "common_window": {"ann_pct": ann, "sharpe": sr, "mdd_pct": mdd, "vol_pct": 8.0},
        "turnover_per_year": turnover,
        "oos_2024_after": {"ann_pct": oos} if oos is not None else {},
    }


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # L1 identical numbers under two cards collapse to one measurement
    a = _card("alpha", crit={"target_edge_pp": 5.0})
    a["arms"] = [_arm("120d", "GO", 5.01, 0.626, -21.74)]
    b = _card("beta", crit={"target_edge_pp": 5.0})
    b["arms"] = [_arm("tsmom|120|ls", "GO", 5.01, 0.626, -21.74)]
    p = build([("alpha", a, "results/bench_alpha.json"), ("beta", b, "results/bench_beta.json")])
    leg("same numbers on same panel collapse to one measurement",
        len(p["live_measurements"]) == 1 and p["live_measurements"][0]["cards"] == ["alpha", "beta"])
    leg("collapsed measurement is reported as a duplicate pair",
        len(p["duplicate_measurements"]) == 1 and p["duplicate_measurements"][0]["cards"] == ["alpha", "beta"])
    leg("arm names differ so the merge is by numbers not by name",
        sorted(p["duplicate_measurements"][0]["arms"]) == ["120d", "tsmom|120|ls"])

    # L2 same card, different numbers -> two threads
    c = _card("gamma")
    c["arms"] = [_arm("120d", "GO", 5.01, 0.626, -21.74), _arm("250d", "GO", 5.24, 0.671, -18.88)]
    p2 = build([("gamma", c, "results/bench_gamma.json")])
    leg("two live arms with different numbers stay two", len(p2["live_measurements"]) == 2)
    leg("single-card arms are never reported as duplicates", p2["duplicate_measurements"] == [])

    # L3 same numbers but different panel -> never merged
    d = _card("delta", bars=4597)
    d["arms"] = [_arm("x", "GO", 5.01, 0.626, -21.74)]
    e = _card("epsilon", bars=4596)
    e["arms"] = [_arm("x", "GO", 5.01, 0.626, -21.74)]
    p3 = build([("delta", d, "results/bench_delta.json"), ("epsilon", e, "results/bench_epsilon.json")])
    leg("identical numbers on different bar counts are not merged",
        len(p3["live_measurements"]) == 2 and p3["duplicate_measurements"] == [])

    # L4 non-live arm beating a live arm on both axes is flagged, with its bar
    f = _card("zeta", crit={"target_edge_pp": 5.0})
    f["arms"] = [
        _arm("ls250", "GO", 5.24, 0.671, -18.88, turnover=4.83),
        _arm("long250", "NO_EDGE", 4.56, 0.754, -13.70, turnover=2.49, oos=8.51),
    ]
    p4 = build([("zeta", f, "results/bench_zeta.json")])
    leg("an arm better on Sharpe AND drawdown is flagged", len(p4["missed_arms"]) == 1)
    m = p4["missed_arms"][0] if p4["missed_arms"] else {}
    leg("flagged arm names the live arm it beats", m.get("beats_arm") == "ls250")
    leg("flagged arm quotes its own deltas", m.get("delta_ann_pp") == -0.68 and m.get("delta_sharpe") == 0.083)
    leg("flagged arm carries the rejecting bar from the card's own criteria",
        m.get("rejecting_bar") == 5.0)

    # L5 better on Sharpe only -> not flagged (conservative reading)
    g = _card("eta", crit={"target_edge_pp": 5.0})
    g["arms"] = [
        _arm("ls", "GO", 5.24, 0.671, -18.88),
        _arm("long", "NO_EDGE", 4.56, 0.754, -25.00),
    ]
    p5 = build([("eta", g, "results/bench_eta.json")])
    leg("better on Sharpe only is not flagged", p5["missed_arms"] == [])

    # L6 better on drawdown only -> not flagged
    g2 = _card("theta", crit={"target_edge_pp": 5.0})
    g2["arms"] = [
        _arm("ls", "GO", 5.24, 0.671, -18.88),
        _arm("long", "NO_EDGE", 4.56, 0.400, -13.70),
    ]
    p6 = build([("theta", g2, "results/bench_theta.json")])
    leg("better on drawdown only is not flagged", p6["missed_arms"] == [])

    # L7 a live arm with unreadable numbers stays visible instead of vanishing
    h = _card("iota")
    h["arms"] = [_arm("blind", "GO", None, None, None)]
    p7 = build([("iota", h, "results/bench_iota.json")])
    leg("live arm with missing numbers is kept, not merged away", len(p7["live_measurements"]) == 1)

    # L8 unknown verdict token is reported, not silently dropped
    i = _card("kappa")
    i["arms"] = [_arm("w", "CENSUS_SIGN_MIXED", 1.0, 0.1, -5.0)]
    p8 = build([("kappa", i, "results/bench_kappa.json")])
    leg("unknown non-live token is listed for the reader",
        "CENSUS_SIGN_MIXED" in p8["other_verdict_tokens"])

    # L9 determinism: same input, same payload minus the clock
    p9 = build([("alpha", a, "results/bench_alpha.json"), ("beta", b, "results/bench_beta.json")])
    p9.pop("generated")
    p.pop("generated")
    leg("build is deterministic", json.dumps(p, sort_keys=True) == json.dumps(p9, sort_keys=True))

    # L10 evidence_cutoff is the max of contributing cards
    leg("evidence_cutoff is the max cutoff seen", p2["evidence_cutoff"] == "2026-01-01")

    # L11 a live card with no arms[] is kept as a card-level thread, not dropped
    flat = {
        "cell": "flatcard",
        "evidence_cutoff": "2026-02-02",
        "verdict": "SIGNIFICANT",
        "products": {"IC": {"bars": 2390, "weighted_ann_pct": 10.07, "carry_mdd_pct": -1.89}},
    }
    p10 = build([("flatcard", flat, "results/bench_flatcard.json")])
    leg("card-level live verdict with no arms is kept", len(p10["live_card_level"]) == 1)
    leg("card-level thread quotes its own per-product numbers",
        p10["live_card_level"][0]["per_product"][0]["ann_pct"] == 10.07)
    leg("card-level cutoff reaches the payload cutoff", p10["evidence_cutoff"] == "2026-02-02")

    # L12 a dead card with no arms stays out
    dead = {"cell": "deadcard", "evidence_cutoff": "2026-02-02", "verdict": "NO_EDGE", "products": {}}
    p11 = build([("deadcard", dead, "results/bench_deadcard.json")])
    leg("card-level NO_EDGE is not counted as live", p11["live_card_level"] == [])

    bad = [n for n, ok in legs if not ok]
    for name, ok in legs:
        print(("PASS  " if ok else "FAIL  ") + name)
    print("%d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 3


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="offline selftest")
    ap.add_argument("--verify", action="store_true", help="re-derive and diff the published json")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.check:
        return selftest()

    payload = build(collect_cards())

    if args.verify:
        old = load(OUT_JSON)
        a = dict(old)
        b = dict(payload)
        a.pop("generated", None)
        b.pop("generated", None)
        same = json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
        print("VERIFY %s" % ("MATCH" if same else "DIFFERS"))
        if not same:
            for k in sorted(set(a) | set(b)):
                if json.dumps(a.get(k), sort_keys=True) != json.dumps(b.get(k), sort_keys=True):
                    print("  differs:", k)
        return 0 if same else 3

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    md = render_md(payload)
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(md + "\n")
    if not args.quiet:
        print(json.dumps({
            "cards": len(payload["cards_examined"]),
            "arms": payload["arms_examined"],
            "live_rows": payload["live_rows"],
            "live_measurements": len(payload["live_measurements"]),
            "duplicates": len(payload["duplicate_measurements"]),
            "missed_arms": len(payload["missed_arms"]),
            "evidence_cutoff": payload["evidence_cutoff"],
            "json": os.path.relpath(OUT_JSON, ROOT),
            "md": os.path.relpath(OUT_MD, ROOT),
        }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
