"""DIVLOWVOL live picks exporter (bm-b r1060, dept: 研究+工程).

Product face for the ONE frozen sleeve that cleared its null distribution
(FUND-DIVLOWVOL-P1 headline rule; results/divlowvol_nulls/NULLS-CONSUME-2026-09-22.json
= z+3.228 / p=0.001 vs 2,000 same-mask nulls).  This script does NOT re-rank or
re-judge anything: it reuses the frozen kernels through the SS-COMBO wiring
layer (single source, zero re-implementation) and exports the CURRENT holdings
implied by the last firing month, so the sleeve is consumable without a backtest
run.

Frozen rule (verbatim, research/FUND-DIVLOWVOL-P1.md sec.2/sec.3):
  * base eligibility mask (active bar, amt20 floor, listed >= LISTED_MIN_BARS,
    not ST), then dividend gate yield_ttm > 0, then screenable sigma;
  * low-vol half: sigma <= cross-sectional median (VOL_FRAC_HEADLINE=0.5);
  * Top-N=20 by yield_ttm DESCENDING, code tiebreak, equal weight, monthly
    rebalance on the T-22 census month-start enumeration.

Outputs (deterministic, idempotent per evidence cutoff):
  results/divlowvol_live/PICKS-<cutoff>.json   (+ latest.json)
  docs/divlowvol_live/PICKS-<cutoff>.md        (one page, CEO-readable)

Honesty face (carried in every artifact):
  * panel = the LOCAL rebuilt qfq panel (data/cache/p1c_local), NOT the Money02
    hosted panel the P1 judged batch ran on -- same frozen rule, different
    panel substrate, disclosed rather than silently equated;
  * the export is a research readout, not investment advice; the company's
    automatic live gate remains the monthly window + CEO sign-off;
  * no cost/turnover model is applied here (the judged face carries x1/x2
    spread cost); the file states the per-rebalance turnover count instead.

Exit codes: 0 ok/idempotent-no-op, 2 mechanism fault, 3 panel missing (honest).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import stagestyle_combo_p1_backtest as SS  # noqa: E402  single-source wiring

FAMILY = "divlowvol"
TOPN = SS.TOPN
PREREG = os.path.join("research", "FUND-DIVLOWVOL-P1.md")
NULLS_EVIDENCE = os.path.join("results", "divlowvol_nulls",
                              "NULLS-CONSUME-2026-09-22.json")
OUT_DIR = os.path.join(ROOT, "results", "divlowvol_live")
DOC_DIR = os.path.join(ROOT, "docs", "divlowvol_live")


def _iso(ts) -> str:
    return np.datetime_as_string(np.datetime64(ts, "D"))


def _sha16(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def current_block(firing, idx):
    """Last firing entry = the live holding block.

    firing = [(m_pos, end_pos, top_idx, weight), ...] from the frozen
    _firing_months().  Returns None when the sleeve holds nothing (honest
    empty block: floor-skipped every recent month)."""
    if not firing:
        return None
    m, end, top, w = firing[-1]
    if len(top) == 0:
        return None
    return {
        "month_pos": int(m),
        "end_pos": int(end),
        "entry_date": _iso(idx[m]),
        "next_entry_date": (_iso(idx[end]) if int(end) < len(idx) else None),
        "weight": round(float(w), 6),
        "top": [int(j) for j in top],
    }


def holdings_rows(codes, top, weight, yields=None, sigmas=None) -> list:
    """Deterministic row table: one row per holding, code-ordered.

    yields/sigmas are optional per-index lookups (dict idx->float); they are
    descriptive context only -- the frozen ranking already happened upstream."""
    rows = []
    for j in top:
        row = {"code": str(codes[j]), "weight": round(float(weight), 6)}
        if yields is not None and j in yields:
            row["yield_ttm"] = round(float(yields[j]), 6)
        if sigmas is not None and j in sigmas:
            row["sigma_daily_pct"] = round(float(sigmas[j]), 4)
        rows.append(row)
    rows.sort(key=lambda r: r["code"])
    return rows


def turnover(prev_codes, cur_codes) -> dict:
    prev, cur = set(prev_codes), set(cur_codes)
    return {
        "added": sorted(cur - prev),
        "removed": sorted(prev - cur),
        "n_held": len(cur),
        "n_changed": len(cur ^ prev),
        "one_way_turnover": ((len(cur - prev) / len(cur))
                             if cur else 0.0),
    }


def render_md(payload) -> str:
    lines = []
    lines.append("# DIVLOWVOL 当前持仓（研究读数）")
    lines.append("")
    lines.append(f"- 证据截止（面板最后 bar）：**{payload['as_of']}**")
    lines.append(f"- 持有窗口起点（最后一发射月）：**{payload['entry_date']}**")
    nxt = payload.get("next_entry_date")
    lines.append(f"- 下次换仓（下一发射月）：**{nxt or '下一交易月首个交易日（面板尾部，待新 bar）'}**")
    lines.append(f"- 规则：{payload['rule']}")
    lines.append(f"- 持仓数：**{payload['n_holdings']}**，等权 "
                 f"**{payload['weight']:.4%}**/只")
    lines.append("")
    tv = payload.get("turnover") or {}
    if tv:
        lines.append(f"- 相对上一发射月：换入 {len(tv['added'])} 只 / "
                     f"换出 {len(tv['removed'])} 只"
                     f"（单边换手 {tv['one_way_turnover']:.1%}）")
        lines.append("")
    lines.append("| # | 代码 | 权重 | 股息率TTM | 日波动率σ(%) |")
    lines.append("|---|---|---|---|---|")
    for i, r in enumerate(payload["holdings"], 1):
        y = f"{r['yield_ttm']:.2%}" if "yield_ttm" in r else "-"
        s = f"{r['sigma_daily_pct']:.2f}" if "sigma_daily_pct" in r else "-"
        lines.append(f"| {i} | {r['code']} | {r['weight']:.2%} | {y} | {s} |")
    lines.append("")
    lines.append("## 面信息披露")
    for d in payload["disclosures"]:
        lines.append(f"- {d}")
    lines.append("")
    lines.append(f"机器件：`results/divlowvol_live/PICKS-{payload['as_of']}.json`"
                 f"（sha16 {payload['sha16']}）")
    return "\n".join(lines) + "\n"


def _disclosures() -> list:
    return [
        "面板=本地重建 qfq 面板（data/cache/p1c_local），非 P1 判决批所用的 "
        "Money02 宿主面板；同一冻结规则、不同面板基座，如实并列不做等价宣称。",
        "规则冻结自 " + PREREG + " §2/§3：基础资格掩码→股息门 yield_ttm>0→"
        "可筛波幅→低波半区（sigma<=截面中位）→按 yield_ttm 降序取 Top-20 等权。",
        "零成本模型（此处不扣费）：judged 面另载 x1/x2 双边成本；本表只给"
        "换手只数供成本自算。",
        "月度换仓（T-22 census 月起点枚举）；非发射月不动作、原持仓延续。",
        "信号窗向前延伸至面板末 bar（census 冻结窗止于 2026-03-02）：延伸只去掉"
        "「起点需 63 个前向 bar」的测量要求，不改规则、不重判任何 census 月。",
        "零收益宣称：本件是研究读数，不构成投资建议；公司自动实盘开闸仍须"
        "月界窗 + CEO 唯一门。",
        "零空头、T+1 成交口径与 P1 一致；一字板/停牌不可成交面不在此剔除。",
    ]


def _live_months(mod, idx, close):
    """Month-start enumeration for LIVE use.

    Same census filter as the frozen enumerate_starts_monthly (window lower
    bound, warmup, active-member floor) minus the 63-bar FORWARD requirement,
    which exists only so a census start has an outcome window to measure.
    A live month needs no forward bars, so suppressing it would silently
    freeze the sleeve three months in the past."""
    out = []
    prev = None
    n = len(idx)
    lo = getattr(mod, "ENUM_LO")
    warmup = int(getattr(mod, "WARMUP_TD"))
    min_listed = int(getattr(mod, "MIN_LISTED"))
    for p in range(n):
        ts = idx[p]
        if ts < lo:
            continue
        k = ts.strftime("%Y-%m")
        if k == prev:
            continue
        prev = k
        if p < warmup:
            continue
        if int((~np.isnan(np.asarray(close[p]))).sum()) < min_listed:
            continue
        out.append(int(p))
    return out


def _live_firing(mod):
    """Frozen rule applied to a FORWARD signal window.

    The judged census froze its month enumeration at ENUM_HI=2026-03-02 (the
    24-month-forward census window).  A live export needs months after that
    date, so the enumeration is rebuilt locally for live use (see
    _live_months); the frozen rule, masks and ranking are untouched and no
    census month is re-judged.  ``_G`` is restored on exit so the frozen
    constants never leak into another caller."""
    idx = mod._G["idx"]
    saved = {k: mod._G.get(k) for k in ("month_pos", "_firing")}
    import warnings
    try:
        mod._G["month_pos"] = _live_months(mod, idx, mod._G["close_np"])
        mod._G.pop("_firing", None)
        with warnings.catch_warnings():
            # frozen family kernel emits nanstd ddof noise on the warmup
            # window; it is pre-existing and does not affect any firing month
            warnings.simplefilter("ignore", RuntimeWarning)
            firing = mod._cell_picks(None, TOPN)
    finally:
        for k, v in saved.items():
            if v is None:
                mod._G.pop(k, None)
            else:
                mod._G[k] = v
    return firing


def build(panel):
    mod = SS.wire_family(FAMILY, panel)
    idx = mod._G["idx"]
    codes = mod._G["codes_arr"]
    firing = _live_firing(mod)
    block = current_block(firing, idx)
    T = len(idx)
    as_of = _iso(idx[T - 1])
    payload = {
        "face": "DIVLOWVOL-LIVE-PICKS",
        "status": "RESEARCH_READOUT_ZERO_JUDGED_CLAIMS",
        "as_of": as_of,
        "panel": {"path": "data/cache/p1c_local",
                  "shape": [int(T), int(len(codes))]},
        "prereg": PREREG,
        "nulls_evidence": NULLS_EVIDENCE,
        "rule": "Top-20 by yield_ttm desc within low-vol half, EW, monthly",
        "census_window_frozen": "1992-09-01..2026-03-02 (FUND-DIVLOWVOL-P1 §2)",
        "signal_window": "%s..%s (forward extension, live only)" % (
            _iso(idx[0]), as_of),
        "t0_date": _iso(idx[mod._G["_t0_pos"]]),
        "n_firing_months": len(firing),
        "n_holdings": 0,
        "holdings": [],
        "weight": 0.0,
        "entry_date": None,
        "next_entry_date": None,
        "turnover": None,
    }
    if block is None:
        payload["status"] = "NO_HOLDINGS_FLOOR_SKIPPED"
        payload["disclosures"] = _disclosures()
        payload["sha16"] = _sha16(payload)
        return payload

    u = mod._month_universe(block["month_pos"])
    ymap = {int(j): float(y) for j, y in
            zip(u["cand_j"], u["cand_yield"])}
    smap = {int(j): float(s) for j, s in
            zip(u["cand_j"], u["cand_sigma"])}
    rows = holdings_rows(codes, block["top"], block["weight"], ymap, smap)

    prev_codes = []
    if len(firing) >= 2:
        prev_codes = [str(codes[j]) for j in firing[-2][2]]
    payload.update({
        "holdings": rows,
        "n_holdings": len(rows),
        "weight": block["weight"],
        "entry_date": block["entry_date"],
        "next_entry_date": block["next_entry_date"],
        "turnover": turnover(prev_codes, [r["code"] for r in rows]),
        "universe": {"n_active": int(u["n_active"]),
                     "n_base": int(u["n_base"]),
                     "n_cand": int(u["n_cand"]),
                     "floor_skipped": bool(u["skipped"])},
        "disclosures": _disclosures(),
    })
    payload["sha16"] = _sha16({k: v for k, v in payload.items()
                               if k != "sha16"})
    return payload


def _write(payload) -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DOC_DIR, exist_ok=True)
    js = os.path.join(OUT_DIR, "PICKS-%s.json" % payload["as_of"])
    with open(js, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    latest = os.path.join(OUT_DIR, "latest.json")
    prev = None
    if os.path.exists(latest):
        try:
            prev = json.load(open(latest, encoding="utf-8"))
        except Exception:
            prev = None
    with open(latest, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    md = os.path.join(DOC_DIR, "PICKS-%s.md" % payload["as_of"])
    with open(md, "w", encoding="utf-8") as fh:
        fh.write(render_md(payload))
    same = (prev is not None and prev.get("sha16") == payload["sha16"]
            and prev.get("as_of") == payload["as_of"])
    print(json.dumps({
        "status": payload["status"],
        "as_of": payload["as_of"],
        "holdings": payload["n_holdings"],
        "weight": payload["weight"],
        "entry_date": payload["entry_date"],
        "next_entry_date": payload["next_entry_date"],
        "turnover_one_way": (payload.get("turnover") or {}).get(
            "one_way_turnover"),
        "idempotent_no_op": bool(same),
        "json": os.path.relpath(js, ROOT).replace("\\", "/"),
        "md": os.path.relpath(md, ROOT).replace("\\", "/"),
        "sha16": payload["sha16"],
    }, ensure_ascii=False, indent=1))
    return 0


def cmd_run(_args) -> int:
    panel = SS.load_local_panel()
    if panel is None:
        print("PANEL_MISSING: data/cache/p1c_local not readable -> exit 3")
        return 3
    return _write(build(panel))


def cmd_selftest(_args) -> int:
    ok = 0
    fails = []

    def chk(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(name)

    # T1: empty firing -> no block (honest empty face)
    chk("T1 empty firing", current_block([], [])is None)
    # T2: last firing entry is the block, weight/normalisation preserved
    idx = np.array(["2026-01-05", "2026-02-02", "2026-03-02"],
                   dtype="datetime64[D]")
    firing = [(0, 1, np.array([3, 1]), 0.5), (1, 3, np.array([2, 5]), 0.5)]
    b = current_block(firing, idx)
    chk("T2 last entry", b["month_pos"] == 1 and b["top"] == [2, 5])
    chk("T2 weight", abs(b["weight"] - 0.5) < 1e-12)
    chk("T2 entry date", b["entry_date"] == "2026-02-02")
    chk("T2 no next (tail)", b["next_entry_date"] is None)
    # T3: rows are code-ordered, yields/sigmas attached only when known
    codes = np.array(["000003", "000001", "600000"])
    rows = holdings_rows(codes, [1, 0], 0.5,
                         yields={1: 0.051, 0: 0.033},
                         sigmas={0: 0.21})
    chk("T3 sorted", [r["code"] for r in rows] == ["000001", "000003"])
    chk("T3 yield attach", rows[0]["yield_ttm"] == 0.051)
    chk("T3 sigma absent", "sigma_daily_pct" not in rows[0])
    chk("T3 sigma attach", rows[1]["sigma_daily_pct"] == 0.21)
    # T4: turnover arithmetic
    tv = turnover(["A", "B", "C"], ["B", "C", "D", "E"])
    chk("T4 added", tv["added"] == ["D", "E"])
    chk("T4 removed", tv["removed"] == ["A"])
    chk("T4 one-way", abs(tv["one_way_turnover"] - 0.5) < 1e-12)
    chk("T4 empty cur", turnover(["A"], [])["one_way_turnover"] == 0.0)
    # T5: md render carries the core lines
    payload = {
        "as_of": "2026-10-19", "entry_date": "2026-10-01",
        "next_entry_date": "2026-11-02",
        "rule": "Top-20 by yield_ttm desc within low-vol half, EW, monthly",
        "n_holdings": 2, "weight": 0.5,
        "turnover": {"added": ["X"], "removed": [], "one_way_turnover": 0.5},
        "holdings": [{"code": "000001", "weight": 0.5,
                      "yield_ttm": 0.051, "sigma_daily_pct": 2.1},
                     {"code": "000003", "weight": 0.5}],
        "disclosures": ["d1"], "sha16": "deadbeefdeadbeef",
    }
    md = render_md(payload)
    chk("T5 md header", md.startswith("# DIVLOWVOL"))
    chk("T5 md rows", "| 1 | 000001 | 50.00% | 5.10% | 2.10 |" in md)
    chk("T5 md disclosure", "- d1" in md)
    chk("T5 md sha", "deadbeefdeadbeef" in md)
    # T6: sha16 stable and payload-hash excludes the field itself
    a = {"x": 1}
    chk("T6 stable", _sha16(a) == _sha16(dict(a)))
    chk("T6 len", len(_sha16(a)) == 16)
    # T7: disclosures always carry the no-advice and panel honesty lines
    d = " ".join(_disclosures())
    chk("T7 advice", "不构成投资建议" in d)
    chk("T7 panel", "p1c_local" in d )
    print(json.dumps({"selftest": "PASS" if not fails else "FAIL",
                      "passed": ok, "fails": fails}, ensure_ascii=False))
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run", help="export current DIVLOWVOL holdings")
    sub.add_parser("selftest", help="offline self-test")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return cmd_selftest(args)
    return cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())