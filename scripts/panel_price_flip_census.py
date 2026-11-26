"""Panel price-flip census: measure how much of our price data contains
single-day jumps that cannot be a real price move.

Why this exists
---------------
r2048 判例（2026-11-24）: ETF 报价面翻转凭空造出 ±900% 单日收益（511030 在
2021-01-11 打 -89.97%、2025-03-19 又 +900% 翻回），修在
``scripts/etf_equity_alpha.py::repair_flips`` 里，只覆盖 ETF 面板。判例的
正法写得很清楚：「接任何 ETF 面板先量全样本单日 |r| 分布（>35% 计数）」。
但那条正法从来没有被施加到**其他**面板上——A 股个股、可转债、期货、指数、
分钟线都没有做过同样的体检。

本件就是对全数据面做一次普查：每个面板、每个序列，量出单日 |r| 超过
35% / 50% / 80% 的格子，量出「跳完又跳回」的翻转对，并机械标出哪些脚本
消费了这些面板。不修数据、不改任何判词——只回答一个问题：我们脚下的
面板有多脏。

口径（刻意选得保守）
--------------------
* 涨停板约束：A 股主板 ±10%、创业板/科创板 ±20%，ETF 亦有 ±10% 档（跨境
  ±20%）。所以单日 |r| > 35% 在任何正常交易日都不可能发生——35% 留了三倍
  余量，宁可漏判也不误杀。
* 排他面：
  - ``repo_daily`` 的 close 是年化利率（0~200%），不是价格，收益比无意义，
    单独按「利率跳变」记账（本章不作为污染证据，只作披露）。
  - ``cb_daily`` 的 close 有大量 NaN（退市段），逐行判空。
  - ``minute_feed`` 的频率是分钟，单分钟 35% 门槛同样成立，但它是**前向
    积累**面板（2026-09 起），全窗短，样本小，如实标注。
* 翻转对：要求「前跳与回跳同号相反、幅度各 ≥30%、间隔 ≤5 根 bar」，这正是
  r2048 描述的形态（-89.97% 后 +900%）。单向大跳可能真是退市/停牌复牌，
  回翻才是「价格面被翻过来了」的硬证据。

用法
----
    python scripts/panel_price_flip_census.py run
    python scripts/panel_price_flip_census.py check
    python scripts/panel_price_flip_census.py selftest
"""

from __future__ import annotations

import csv
import io
import json
import os
import statistics
import sys
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "panel_price_flip_census.json")

JUMP_TIERS = (0.35, 0.50, 0.80)
FLIP_MIN = 0.30
FLIP_WINDOW = 5
RECOVER_LOOKAHEAD = 60
RECOVER_FRAC = 0.70

# (panel, dir, date_col, close_col, kind, notes)
PANELS: Sequence[Tuple[str, str, str, str, str, str]] = (
    ("etf_daily", "data/daily", "date", "close", "price", "ETF/指数日线（sina，qfq 因子 1.0）"),
    ("astock_daily", "data/astock_daily", "date", "close", "price", "A股个股 qfq 前复权"),
    ("cb_daily", "data/cb_daily", "date", "close", "price", "可转债（含大量 NaN 退市段）"),
    ("futures_daily", "data/futures_daily", "date", "close", "price", "期货主力连续"),
    ("index_daily", "data/index_daily", "date", "close", "price", "宽基指数"),
    ("repo_daily", "data/repo_daily", "date", "close", "rate", "国债逆回购年化利率（非价格，仅披露）"),
    ("minute_feed", "data/minute_feed", "day", "close", "price", "ETF 分钟前向积累（2026-09 起）"),
)


def _read_series(path: str, date_col: str, close_col: str) -> List[Tuple[str, float]]:
    """Return [(date, close)] sorted by date, dropping unparsable rows."""
    rows: List[Tuple[str, float]] = []
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
            rdr = csv.DictReader(f)
            if not rdr.fieldnames or close_col not in rdr.fieldnames:
                return []
            for r in rdr:
                d = (r.get(date_col) or "").strip()
                c = (r.get(close_col) or "").strip()
                if not d or not c:
                    continue
                try:
                    v = float(c)
                except ValueError:
                    continue
                if v != v:  # NaN
                    continue
                if v <= 0:
                    continue
                rows.append((d, v))
    except (OSError, UnicodeDecodeError):
        return []
    rows.sort(key=lambda t: t[0])
    return rows


def _year(date_str: str) -> Optional[int]:
    try:
        return int(date_str[:4])
    except (TypeError, ValueError):
        return None


def _stats(series: List[Tuple[str, float]], kind: str) -> Dict[str, object]:
    n = len(series)
    out: Dict[str, object] = {
        "bars": n,
        "first": series[0][0] if n else None,
        "last": series[-1][0] if n else None,
        "jumps": {f"{int(t*100)}pct": 0 for t in JUMP_TIERS},
        "max_abs_ret": 0.0,
        "max_abs_ret_date": None,
        "flip_pairs": [],
        "tier_hits": [],
        "recovered": 0,
        "recovered_examples": [],
        "split_rebase": [],
        "jump_era": {"pre2000": 0, "2000s": 0, "2010s": 0, "2020plus": 0},
    }
    if n < 2:
        return out
    rets: List[Optional[float]] = [None]
    for i in range(1, n):
        prev = series[i - 1][1]
        cur = series[i][1]
        rets.append(cur / prev - 1.0 if prev > 0 else None)

    for i in range(1, n):
        r = rets[i]
        if r is None:
            continue
        a = abs(r)
        if a > out["max_abs_ret"]:
            out["max_abs_ret"] = a
            out["max_abs_ret_date"] = series[i][0]
        for t in JUMP_TIERS:
            if a >= t:
                # 累计口径：50% 档是 35% 档的子集，读者一眼能看出分布厚度
                out["jumps"][f"{int(t*100)}pct"] += 1
        if a >= JUMP_TIERS[0]:
            out["tier_hits"].append(
                {"date": series[i][0], "ret": round(r, 6), "close": series[i][1]}
            )
            # A jump that the series walks back within RECOVER_LOOKAHEAD bars is
            # stronger evidence of a re-based price face than a one-way gap
            # (which can legitimately be a suspension resumption).
            yr = _year(series[i][0])
            if yr is not None:
                bucket = "pre2000" if yr < 2000 else ("2000s" if yr < 2010 else ("2010s" if yr < 2020 else "2020plus"))
                out["jump_era"][bucket] += 1
            if kind == "price":
                lim = min(n - 1, i + RECOVER_LOOKAHEAD)
                base_v = series[i][1]
                best = 0.0
                for j in range(i + 1, lim + 1):
                    c = series[j][1] / base_v - 1.0
                    if (c > 0) != (r > 0) and abs(c) > best:
                        best = abs(c)
                if a > 0 and best >= RECOVER_FRAC * a:
                    out["recovered"] += 1
                    if len(out["recovered_examples"]) < 3:
                        out["recovered_examples"].append(
                            {
                                "date": series[i][0],
                                "ret": round(r, 6),
                                "recovered_frac": round(best / a, 3),
                            }
                        )

    # split/rebase signature: a ~-80..-90% bar followed (at any distance) by a
    # >= +150% bar. This is the 1:10 share-split fingerprint: the series runs at
    # 1/10 of the true level between the two dates, so the whole stretch is wrong,
    # not just the jump bar.
    if kind == "price":
        big = [(i, rets[i]) for i in range(1, n) if rets[i] is not None and abs(rets[i]) >= 0.70]
        for ai in range(len(big)):
            i1, r1 = big[ai]
            for bi in range(ai + 1, len(big)):
                i2, r2 = big[bi]
                if r1 * r2 < 0 and abs(r2) >= 1.5:
                    out["split_rebase"].append(
                        {
                            "down_date": series[i1][0] if r1 < 0 else series[i2][0],
                            "up_date": series[i2][0] if r1 < 0 else series[i1][0],
                            "down_ret": round(min(r1, r2), 6),
                            "up_ret": round(max(r1, r2), 6),
                            "gap_bars": abs(i2 - i1),
                        }
                    )
                    break

    # flip pairs: opposite sign, both >= FLIP_MIN, separated by <= FLIP_WINDOW bars
    for i in range(1, n):
        r1 = rets[i]
        if r1 is None or abs(r1) < FLIP_MIN:
            continue
        for j in range(i + 1, min(n, i + 1 + FLIP_WINDOW + 1)):
            r2 = rets[j]
            if r2 is None or abs(r2) < FLIP_MIN:
                continue
            if (r1 > 0) != (r2 > 0):
                out["flip_pairs"].append(
                    {
                        "down_date": series[i][0] if r1 < 0 else series[j][0],
                        "up_date": series[i][0] if r1 > 0 else series[j][0],
                        "gap_bars": j - i,
                        "r1": round(r1, 6),
                        "r2": round(r2, 6),
                    }
                )
                break
    return out


def _panel_files(rel: str) -> List[str]:
    base = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.isdir(base):
        return []
    files = []
    for root, _dirs, names in os.walk(base):
        for name in names:
            if name.lower().endswith(".csv"):
                files.append(os.path.join(root, name))
    return sorted(files)


def _consumers() -> Dict[str, List[str]]:
    """Which scripts reference each panel directory (mechanical, literal match)."""
    scripts_dir = os.path.join(ROOT, "scripts")
    subs = {p[0]: p[1] for p in PANELS}
    hits: Dict[str, List[str]] = {k: [] for k in subs}
    if not os.path.isdir(scripts_dir):
        return hits
    for name in sorted(os.listdir(scripts_dir)):
        if not name.endswith(".py"):
            continue
        path = os.path.join(scripts_dir, name)
        try:
            with io.open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError:
            continue
        for panel, rel in subs.items():
            needle = rel.replace("/", "\\\\") if os.sep == "\\" else rel
            if rel in text or rel.replace("/", "\\") in text or os.path.basename(rel) in text:
                # require the directory-ish token to avoid matching bare "daily"
                if rel in text or rel.replace("/", "\\") in text or ("data" in text and os.path.basename(rel) in text):
                    if name not in hits[panel]:
                        hits[panel].append(name)
    return hits


def run() -> Dict[str, object]:
    consumers = _consumers()
    panels_out: List[Dict[str, object]] = []
    for panel, rel, date_col, close_col, kind, note in PANELS:
        files = _panel_files(rel)
        agg = {
            "panel": panel,
            "dir": rel,
            "kind": kind,
            "note": note,
            "files": len(files),
            "files_with_jumps": 0,
            "bars": 0,
            "jumps": {f"{int(t*100)}pct": 0 for t in JUMP_TIERS},
            "flip_files": 0,
            "flip_pairs": 0,
            "recovered": 0,
            "split_rebase_files": 0,
            "jump_era": {"pre2000": 0, "2000s": 0, "2010s": 0, "2020plus": 0},
            "max_abs_ret": 0.0,
            "max_file": None,
            "max_date": None,
            "top_files": [],
            "consumers": consumers.get(panel, []),
        }
        per_file: List[Dict[str, object]] = []
        for path in files:
            series = _read_series(path, date_col, close_col)
            st = _stats(series, kind)
            if not st["bars"]:
                continue
            fname = os.path.relpath(path, os.path.join(ROOT, rel.replace("/", os.sep)))
            if st["jumps"][f"{int(JUMP_TIERS[0]*100)}pct"]:
                agg["files_with_jumps"] += 1
            if st["flip_pairs"]:
                agg["flip_files"] += 1
                agg["flip_pairs"] += len(st["flip_pairs"])
            agg["bars"] += st["bars"]
            agg["recovered"] += st["recovered"]
            if st["split_rebase"]:
                agg["split_rebase_files"] += 1
            for k in agg["jump_era"]:
                agg["jump_era"][k] += st["jump_era"][k]
            for t in JUMP_TIERS:
                agg["jumps"][f"{int(t*100)}pct"] += st["jumps"][f"{int(t*100)}pct"]
            if st["max_abs_ret"] > agg["max_abs_ret"]:
                agg["max_abs_ret"] = st["max_abs_ret"]
                agg["max_file"] = fname
                agg["max_date"] = st["max_abs_ret_date"]
            if st["jumps"][f"{int(JUMP_TIERS[0]*100)}pct"] or st["flip_pairs"]:
                per_file.append(
                    {
                        "file": fname,
                        "bars": st["bars"],
                        "jumps": st["jumps"],
                        "flip_pairs": len(st["flip_pairs"]),
                        "recovered": st["recovered"],
                        "split_rebase": st["split_rebase"][:3],
                        "max_abs_ret": round(st["max_abs_ret"], 6),
                        "max_date": st["max_abs_ret_date"],
                        "hits": st["tier_hits"][:8],
                        "flips": st["flip_pairs"][:5],
                        "recovered_examples": st["recovered_examples"],
                    }
                )
        per_file.sort(key=lambda d: (-d["flip_pairs"], -d["jumps"]["50pct"], -d["max_abs_ret"]))
        agg["affected_files"] = len(per_file)
        agg["top_files"] = per_file[:15]
        panels_out.append(agg)

    verdict = _verdict(panels_out)
    return {
        "generated": _now(),
        "tiers": list(JUMP_TIERS),
        "flip_min": FLIP_MIN,
        "flip_window": FLIP_WINDOW,
        "panels": panels_out,
        "verdict": verdict,
    }


def _now() -> str:
    import datetime

    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _verdict(panels: List[Dict[str, object]]) -> Dict[str, object]:
    price_panels = [p for p in panels if p["kind"] == "price"]
    jump_panels = [p["panel"] for p in price_panels if p["jumps"]["35pct"] > 0]
    flip_panels = [p["panel"] for p in price_panels if p["flip_pairs"] > 0]
    recovered_panels = [p["panel"] for p in price_panels if p.get("recovered", 0) > 0]
    total_flips = sum(p["flip_pairs"] for p in price_panels)
    total_jumps = sum(p["jumps"]["35pct"] for p in price_panels)
    total_recovered = sum(p.get("recovered", 0) for p in price_panels)
    total_bars = sum(p.get("bars", 0) for p in price_panels)
    era = {"pre2000": 0, "2000s": 0, "2010s": 0, "2020plus": 0}
    for p in price_panels:
        for k in era:
            era[k] += p.get("jump_era", {}).get(k, 0)
    if not jump_panels:
        code = "PANELS_CLEAN"
    elif flip_panels or recovered_panels:
        code = "FLIP_CONFIRMED"
    else:
        code = "PRICE_JUMPS_UNEXPLAINED"
    return {
        "code": code,
        "price_panels_with_jumps": jump_panels,
        "price_panels_with_flips": flip_panels,
        "price_panels_with_walkback": recovered_panels,
        "total_35pct_hits": total_jumps,
        "total_flip_pairs": total_flips,
        "total_walkback_recoveries": total_recovered,
        "split_rebased_files": sum(p.get("split_rebase_files", 0) for p in price_panels),
        "price_bars_scanned": total_bars,
        "jump_era": era,
        "contamination_rate": (round(total_jumps / total_bars, 8) if total_bars else None),
        "reading": (
            "35% 单日跳变在任何正常价格面都不可能发生（A股 ±10/±20%，ETF ±10/±20%）；"
            "命中即污染。其中「5 根内反向回跳」或「60 根内走回 70%」两种形态是被证实的价格面翻转。"
        ),
    }


def check() -> int:
    if not os.path.exists(OUT_JSON):
        print("face missing: %s" % OUT_JSON)
        return 3
    with io.open(OUT_JSON, "r", encoding="utf-8") as f:
        published = json.load(f)
    fresh = run()
    keys = ("tiers", "flip_min", "flip_window", "verdict")
    diffs = [k for k in keys if published.get(k) != fresh.get(k)]
    # panel-level counters
    pub_panels = {p["panel"]: p for p in published.get("panels", [])}
    for p in fresh["panels"]:
        q = pub_panels.get(p["panel"])
        if not q:
            diffs.append("panel:%s missing" % p["panel"])
            continue
        for k in ("files", "files_with_jumps", "flip_pairs", "recovered", "split_rebase_files", "max_abs_ret"):
            if q.get(k) != p.get(k):
                diffs.append("panel:%s:%s %r != %r" % (p["panel"], k, q.get(k), p.get(k)))
    if diffs:
        print("STALE / MISMATCH: %s" % "; ".join(diffs[:8]))
        return 3
    print("OK verdict=%s panels=%d" % (fresh["verdict"]["code"], len(fresh["panels"])))
    return 0


# ---------------------------------------------------------------- selftest

def _mk(tmp: str, name: str, rows: Iterable[Tuple[str, float]]) -> str:
    path = os.path.join(tmp, name)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write("date,close\n")
        for d, c in rows:
            f.write("%s,%s\n" % (d, c))
    return path


def selftest() -> int:
    import tempfile

    fails: List[str] = []
    checks = [0]

    def eq(name: str, got, want):
        checks[0] += 1
        if got != want:
            fails.append("%s: got %r want %r" % (name, got, want))

    with tempfile.TemporaryDirectory() as tmp:
        # 1. clean ramp: no jumps, no flips
        rows = [("2026-01-%02d" % (i + 1), 100.0 + i) for i in range(20)]
        p = _mk(tmp, "clean.csv", rows)
        st = _stats(_read_series(p, "date", "close"), "price")
        eq("clean.bars", st["bars"], 20)
        eq("clean.jumps", st["jumps"]["35pct"], 0)
        eq("clean.flips", len(st["flip_pairs"]), 0)

        # 2. single big jump down (no rebound) -> 35pct hit, no flip
        rows = [("2026-01-01", 100.0), ("2026-01-02", 50.0), ("2026-01-03", 50.5), ("2026-01-04", 51.0)]
        p = _mk(tmp, "downonly.csv", rows)
        st = _stats(_read_series(p, "date", "close"), "price")
        eq("downonly.jumps", st["jumps"]["35pct"], 1)
        eq("downonly.flips", len(st["flip_pairs"]), 0)
        eq("downonly.max", round(st["max_abs_ret"], 6), -0.5 if False else 0.5)

        # 3. flip: -50% then +100% next bar -> one flip pair
        rows = [
            ("2026-01-01", 100.0),
            ("2026-01-02", 50.0),
            ("2026-01-03", 100.0),
            ("2026-01-04", 101.0),
        ]
        p = _mk(tmp, "flip.csv", rows)
        st = _stats(_read_series(p, "date", "close"), "price")
        eq("flip.pairs", len(st["flip_pairs"]), 1)
        eq("flip.35", st["jumps"]["35pct"], 2)  # -50% and +100% both clear 35
        eq("flip.50", st["jumps"]["50pct"], 2)

        # 4. out-of-window rebound is NOT a flip
        rows = [("2026-01-01", 100.0), ("2026-01-02", 50.0)] + [
            ("2026-01-%02d" % (3 + i), 50.0 + i) for i in range(8)
        ] + [("2026-01-20", 100.0)]
        p = _mk(tmp, "slowrecover.csv", rows)
        st = _stats(_read_series(p, "date", "close"), "price")
        eq("slowrecover.flips", len(st["flip_pairs"]), 0)

        # 5. NaN / empty / non-positive rows are dropped
        path = os.path.join(tmp, "nan.csv")
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write("date,close\n2026-01-01,10\n2026-01-02,\n2026-01-03,abc\n2026-01-04,0\n2026-01-05,11\n")
        st = _stats(_read_series(path, "date", "close"), "price")
        eq("nan.bars", st["bars"], 2)

        # 6. unsorted input gets sorted (flip detection needs order)
        path = os.path.join(tmp, "unsorted.csv")
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write("date,close\n2026-01-03,100\n2026-01-01,100\n2026-01-02,50\n")
        st = _stats(_read_series(path, "date", "close"), "price")
        eq("unsorted.first", st["first"], "2026-01-01")
        eq("unsorted.flips", len(st["flip_pairs"]), 1)

        # 7. rate panel is excluded from contamination verdict
        fake = [
            {"panel": "etf_daily", "kind": "price", "jumps": {"35pct": 0, "50pct": 0, "80pct": 0}, "flip_pairs": 0},
            {"panel": "repo_daily", "kind": "rate", "jumps": {"35pct": 9, "50pct": 9, "80pct": 9}, "flip_pairs": 9},
        ]
        v = _verdict(fake)
        eq("verdict.clean", v["code"], "PANELS_CLEAN")

        # 8. flip beats jump-only
        fake2 = [
            {"panel": "a", "kind": "price", "jumps": {"35pct": 3, "50pct": 1, "80pct": 0}, "flip_pairs": 0},
            {"panel": "b", "kind": "price", "jumps": {"35pct": 1, "50pct": 0, "80pct": 0}, "flip_pairs": 2},
        ]
        v = _verdict(fake2)
        eq("verdict.flip", v["code"], "FLIP_CONFIRMED")
        eq("verdict.flip.total", v["total_flip_pairs"], 2)

        # 9. jump without flip is its own verdict
        v = _verdict([{"panel": "a", "kind": "price", "jumps": {"35pct": 3, "50pct": 0, "80pct": 0}, "flip_pairs": 0}])
        eq("verdict.jumponly", v["code"], "PRICE_JUMPS_UNEXPLAINED")

        # 9b. walkback (slow recovery inside 60 bars) also confirms a re-based face
        v = _verdict([{"panel": "a", "kind": "price", "jumps": {"35pct": 1, "50pct": 0, "80pct": 0},
                       "flip_pairs": 0, "recovered": 1}])
        eq("verdict.walkback", v["code"], "FLIP_CONFIRMED")

        # 9c. walkback detection: -60% then gradual return over 30 bars
        rows = [("2026-01-01", 100.0), ("2026-01-02", 40.0)]
        rows += [("2026-02-%02d" % (i + 1), 40.0 + i * 1.26) for i in range(30)]
        p = _mk(tmp, "walkback.csv", rows)
        st = _stats(_read_series(p, "date", "close"), "price")
        eq("walkback.jumps", st["jumps"]["35pct"], 1)
        eq("walkback.recovered", st["recovered"], 1)
        eq("walkback.flips", len(st["flip_pairs"]), 0)

        # 10. tier accounting is cumulative (a -90% bar counts in every tier it clears)
        rows = [("2026-01-01", 100.0), ("2026-01-02", 10.0)]
        p = _mk(tmp, "deep.csv", rows)
        st = _stats(_read_series(p, "date", "close"), "price")
        eq("deep.35", st["jumps"]["35pct"], 1)
        eq("deep.50", st["jumps"]["50pct"], 1)
        eq("deep.80", st["jumps"]["80pct"], 1)

        # 11. _read_series on a missing file returns empty, does not raise
        eq("missing", _read_series(os.path.join(tmp, "nope.csv"), "date", "close"), [])

    if fails:
        print("selftest: FAIL (%d/%d)" % (len(fails), checks[0]))
        for f_ in fails:
            print("  - " + f_)
        return 1
    print("selftest: PASS (%d/%d)" % (checks[0], checks[0]))
    return 0


def main(argv: Sequence[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = run()
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
            json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=False)
            f.write("\n")
        v = face["verdict"]
        print("PANEL-FLIP-CENSUS %s" % v["code"])
        for p in face["panels"]:
            print(
                "  %-14s files=%-5d jumps35=%-4d flips=%-3d max=%.1f%% (%s)"
                % (
                    p["panel"],
                    p["files"],
                    p["jumps"]["35pct"],
                    p["flip_pairs"],
                    100.0 * p["max_abs_ret"],
                    p["max_file"],
                )
            )
        print("face -> %s" % OUT_JSON)
        return 0
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: panel_price_flip_census.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
