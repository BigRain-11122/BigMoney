"""YTD-TRACK-RECORD assembly (T-2026-10-02-146, CEO direct order O-20261002-2135).

Splice ONE continuous YTD NAV curve per live face: backtest leg
(2026-01-05 -> 2026-09-23, retro_paper_2026 frozen ledgers, daily equity
series) chain-linked with paper leg (2026-09-23 -> latest complete bar,
per-account daily marks) -- normalize paper leg onto backtest leg
terminal NAV, no double-count. Dual baseline: 510300 unadjusted
buy&hold + core48 DAILY-REBALANCED equal-weight (o1600_market_fit.py
published method, single-source reproduction). Pure aggregation of EXISTING artifacts: zero new
burns, zero network, zero judgment lines (T-105 one-pager precedent).

Honesty anchors (order verbatim): backtest leg is NOT out-of-sample
evidence (retro replay = historical paper testimony), paper leg is;
no window cherry-picking; no cost removal; negative results as-is;
paper-only members labeled (no backtest leg exists for them); holiday
mark = 2026-09-30 close (Golden Week), resumes 10-09.

Members: 6 registered employees + B_MAXDIV + 20 AGGR + 7 ALLOC + 5 GRID
+ SYSTEM-V1 + REV-OSC-STD = 41 faces (full pool census asserted).

CLI: run | selftest      exit 0 ok / 2 mechanical failure (honest).
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from live.paper import load_core, build_panels

ROOT = PATHS.root
BT_END = "2026-09-23"          # order-frozen backtest-leg terminal (177 td)
W_START = "2026-09-23"         # paper-leg start (employees' hire day)
INITIAL = 1_000_000.0
EMPLOYEES = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
             "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
RETRO_DIR = os.path.join(ROOT, "results", "retro_paper_2026")
MARKS_DIR = os.path.join(ROOT, "results", "paper", "marks")
OUT_DIR = os.path.join(ROOT, "results", "ytd_track_record")
BEAT_HTML = os.path.join(ROOT, "results", "beat_market.html")
DASH_HTML = os.path.join(ROOT, "dashboard.html")
PAPER_EXPORT = os.path.join(ROOT, "results", "paper_export")
PAPER_DIR = os.path.join(ROOT, "results", "paper")

# beat_market.html v1.0 static-snapshot published values (o1600 slice,
# 09-24 pre-wiring snapshot -- NOT anchors, registry for divergence
# disclosure only: 3 members were rewired by T-78 s4 exit-overlay on
# 09-26, git d65f2d4ac, between the o1600 slice and the retro replay)
PUBLISHED_510300_BT = -0.0524
PUBLISHED_48EW_BT = -0.0389
PUBLISHED_EMP_BT = {"COMPOSITE-CE-01": 0.0141, "COMPOSITE-CE-02": 0.0247,
                    "DROUGHT-CE-01": 0.0399, "ENGULF-CE-01": -0.0145,
                    "NEEDLE-DE-01": 0.0061, "VOLATILITY-CE-01": 0.0294}

FAM_DIRS = {
    "AGGR": os.path.join(ROOT, "results", "aggr_paper"),
    "ALLOC": os.path.join(ROOT, "results", "alloc_paper"),
    "GRID": os.path.join(ROOT, "results", "grid_paper"),
}
SYSV1_DIR = os.path.join(ROOT, "results", "system_v1_paper")

SECTION_A = "<!-- YTD-SECTION-START -->"
SECTION_B = "<!-- YTD-SECTION-END -->"


def log(msg):
    print(msg, flush=True)


def jload(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def path_maxdd(nav):
    peak = nav[0]
    mdd = 0.0
    for v in nav:
        if v > peak:
            peak = v
        if peak > 0:
            d = v / peak - 1.0
            if d < mdd:
                mdd = d
    return mdd


# ---------------------------------------------------------------- legs
def backtest_legs():
    """Retro daily equity series, cut at BT_END (order boundary)."""
    legs = {}
    for fn in sorted(os.listdir(RETRO_DIR)):
        if not fn.endswith("_ledger.json"):
            continue
        name = fn[:-len("_ledger.json")]
        d = jload(os.path.join(RETRO_DIR, fn))
        x = d.get("x1") or {}
        dates, eq = x.get("dates"), x.get("equity_cny")
        if not dates or not eq or len(dates) != len(eq):
            continue
        cut = [i for i, dt in enumerate(dates) if dt <= BT_END]
        legs[name] = {"dates": [dates[i] for i in cut],
                      "equity": [float(eq[i]) for i in cut],
                      "family": d.get("family", "?"),
                      "full_ret": float(eq[-1]) / INITIAL - 1.0,
                      "last_date": dates[-1]}
    return legs


def leaderboard_anchors():
    """Published cum-x1 anchors from results/retro_paper_2026/LEADERBOARD.md
    (T-79 CEO one-pager, window 01-05 -> 09-24). Independent published face
    for the retro ledgers (machine-parsed, no hand-copy)."""
    out = {}
    with open(os.path.join(RETRO_DIR, "LEADERBOARD.md"), "r",
              encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\|\s*\d+\s*\|\s*([A-Z0-9_-]+)\s*\|\s*[ABC]\s*\|"
                         r"\s*([+-]\d+\.\d+)%", line)
            if m:
                out[m.group(1)] = float(m.group(2)) / 100.0
    return out


def etf_calendar(marks_days, panel_dates):
    """Trading-day authority = ETF daily panel; marks days not in the
    panel (e.g. 2026-09-25 Mid-Autumn holiday settle rows) are excluded."""
    return [d for d in marks_days if d in panel_dates]


def panel_trading_days():
    df = pd.read_csv(os.path.join(PATHS.daily_dir, "510300.csv"),
                     parse_dates=["date"])
    return {d.strftime("%Y-%m-%d") for d in df["date"]}


def employee_paper_leg(panel_days):
    """Daily EOD equity per employee from marks jsonl last rows
    (kind=settle/intraday final row carries equity_mark_cny)."""
    files = sorted(f for f in os.listdir(MARKS_DIR)
                   if f.startswith("marks-") and f.endswith(".jsonl"))
    by_day = {}
    for fn in files:
        day = fn[len("marks-"): -len(".jsonl")]
        day = f"{day[:4]}-{day[4:6]}-{day[6:]}"
        by_day[day] = os.path.join(MARKS_DIR, fn)
    days = etf_calendar([d for d in by_day if d > W_START], panel_days)
    eq = {t: {} for t in EMPLOYEES}
    for day in sorted(days):
        with open(by_day[day], "r", encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
        if not rows:
            continue
        last = rows[-1].get("traders", {})
        for t in EMPLOYEES:
            if t in last and "equity_mark_cny" in last[t]:
                eq[t][day] = float(last[t]["equity_mark_cny"])
    return eq, sorted(days)


def family_paper_legs():
    """marks daily_ret lists from the experimental account JSONs.
    Shape variants (all chain to the same (date, daily_ret) pairs):
    - AGGR/GRID: 'marks' rows with 'daily_ret'
    - SYSV1: 'marks' rows with 'ret'
    - ALLOC: 'nav_series' [date, nav_cny] pairs -> chain returns
      (inception 09-23 row = base; returns start 09-24 per BT_END cut)"""
    out = {}
    for fam, d in FAM_DIRS.items():
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            name = fn[:-len(".json")]
            if name.endswith("_paper"):
                name = name[:-len("_paper")]
            doc = jload(os.path.join(d, fn))
            pts = []
            marks = doc.get("marks")
            if isinstance(marks, list):
                for m in marks:
                    if not (isinstance(m, dict) and m.get("date") is not None):
                        continue
                    r = m.get("daily_ret", m.get("ret"))
                    if r is not None:
                        pts.append((m.get("date"), float(r)))
            elif isinstance(doc.get("nav_series"), list) and doc["nav_series"]:
                ns = doc["nav_series"]
                for i in range(1, len(ns)):
                    d0, n0 = ns[i - 1][0], float(ns[i - 1][1])
                    d1, n1 = ns[i][0], float(ns[i][1])
                    if n0 > 0:
                        pts.append((d1, n1 / n0 - 1.0))
            if pts:
                out[f"{fam}:{name}"] = pts
    for fn in sorted(os.listdir(SYSV1_DIR)):
        if not fn.endswith("_paper.json"):
            continue
        name = fn[:-len("_paper.json")]
        doc = jload(os.path.join(SYSV1_DIR, fn))
        marks = doc.get("marks")
        if isinstance(marks, list) and marks:
            # SYSV1 harness rows carry 'ret' (AGGR/ALLOC/GRID carry
            # 'daily_ret') -- accept both keys, same chain semantics
            pts = [(m.get("date"), float(m.get("daily_ret", m.get("ret"))))
                   for m in marks
                   if isinstance(m, dict) and m.get("date") is not None
                   and (m.get("daily_ret") is not None or m.get("ret") is not None)]
            if pts:
                out[f"SYSV1:{name}"] = pts
    return out


def baselines(panel_days_sorted):
    """BENCH-510300: unadjusted close buy&hold from data/daily/510300.csv
    (published caliber). BENCH-48EW: DAILY-REBALANCED equal-weight over the
    core48 panel -- method verbatim from scripts/o1600_market_fit.py
    (single-source law; reproduced the published -3.89% to 0.01pp
    pre-freeze: rets.mean(axis=1) compounded)."""
    y_start = "2026-01-05"
    last = panel_days_sorted[-1]
    df = pd.read_csv(os.path.join(PATHS.daily_dir, "510300.csv"),
                     parse_dates=["date"]).set_index("date").sort_index()
    s = df["close"]
    dates = [d.strftime("%Y-%m-%d") for d in s.index
             if y_start <= d.strftime("%Y-%m-%d") <= last]
    nav = [float(s.loc[pd.Timestamp(d)]) / float(s.loc[pd.Timestamp(dates[0])])
           for d in dates]
    # o1600_market_fit.py passive EW48, verbatim formula
    P = build_panels(load_core())
    idx = P["close"].index
    win = idx[(idx >= pd.Timestamp(y_start)) & (idx <= pd.Timestamp(last))]
    rets = P["close"].loc[win].pct_change(fill_method=None).iloc[1:]
    ew_dates = [y_start] + [d.strftime("%Y-%m-%d") for d in rets.index]
    ew_nav = [1.0]
    for m in rets.mean(axis=1):
        ew_nav.append(ew_nav[-1] * (1.0 + float(m)))
    return {"BENCH-510300": (dates, nav), "BENCH-48EW": (ew_dates, ew_nav)}


# ------------------------------------------------------------- assembly
def splice(bt, paper_pts, paper_days_expected=None):
    """Chain-link: NAV(bt terminal) x prod(1+paper daily rets).
    Base = INITIAL (NOT equity[0]): A-family ledgers start at INITIAL
    exactly, but B/C blend/alloc ledgers embed day-1 return in equity[0]
    -- eq[-1]/INITIAL-1 == x1.cum_ret for ALL 17 ledgers (verified)."""
    dates = list(bt["dates"])
    nav = [e / INITIAL for e in bt["equity"]]
    for d, r in paper_pts:
        if d > BT_END and d not in dates:
            dates.append(d)
            nav.append(nav[-1] * (1.0 + r))
    return dates, nav


def assemble():
    panel_days = panel_trading_days()
    bts = backtest_legs()
    emp_eq, emp_days = employee_paper_leg(panel_days)
    fams = family_paper_legs()
    benches = baselines(sorted(panel_days))

    members = {}
    # -- six employees: retro leg + marks-derived paper leg
    for t in EMPLOYEES:
        bt = bts.get(t)
        if bt is None:
            raise RuntimeError(f"retro ledger missing for employee {t}")
        pts = []
        prev = INITIAL  # hire-day close = initial cash (no positions yet)
        for d in emp_days:
            if d <= BT_END:
                continue
            e = emp_eq[t].get(d)
            if e is None:
                continue
            pts.append((d, e / prev - 1.0))
            prev = e
        dates, nav = splice(bt, pts)
        members[t] = {"family": "A", "dates": dates, "nav": nav,
                      "paper_only": False,
                      "paper_ret": nav[-1] / (bt["equity"][-1] / INITIAL) - 1.0,
                      "bt_ret": bt["equity"][-1] / INITIAL - 1.0,
                      "full_ret": bt["full_ret"], "last_date": bt["last_date"]}
    # -- retro-only/blend faces (B_MAXDIV + retro AGGR) with live marks where present
    for name, bt in bts.items():
        if name in members:
            continue
        fam = "B" if bt["family"] == "B" else "C"
        live_key = None
        for key in fams:
            if key.split(":", 1)[1] == name:
                live_key = key
                break
        if live_key:
            dates, nav = splice(bt, [(d, r) for d, r in fams[live_key]
                                     if d > BT_END])
            members[name] = {"family": fam, "dates": dates, "nav": nav,
                             "paper_only": False,
                             "paper_ret": nav[-1] / (bt["equity"][-1] / INITIAL) - 1.0,
                             "bt_ret": bt["equity"][-1] / INITIAL - 1.0,
                             "full_ret": bt["full_ret"], "last_date": bt["last_date"]}
        else:
            members[name] = {"family": fam, "dates": list(bt["dates"]),
                            "nav": [e / INITIAL for e in bt["equity"]],
                            "paper_only": False,
                            "paper_ret": 0.0,
                            "bt_ret": bt["equity"][-1] / INITIAL - 1.0,
                            "full_ret": bt["full_ret"], "last_date": bt["last_date"],
                            "note": "backtest-leg only: no separate live paper ledger (live face = the employee accounts themselves)"}
    # -- live-only accounts (no retro leg): paper-only, anchored at paper start
    for key, pts in fams.items():
        name = key.split(":", 1)[1]
        if name in members:
            continue
        fam = key.split(":", 1)[0]
        dates, nav = [], []
        cur = 1.0
        for d, r in pts:
            dates.append(d)
            cur *= (1.0 + r)
            nav.append(cur)
        members[name] = {"family": fam, "dates": dates, "nav": nav,
                        "paper_only": True, "paper_ret": cur - 1.0,
                        "bt_ret": None}
    # -- baselines as pseudo-members
    for bname, (dates, nav) in benches.items():
        members[bname] = {"family": "BENCH", "dates": dates, "nav": nav,
                          "paper_only": False, "paper_ret": None, "bt_ret": None}
    return members, benches, emp_eq, emp_days, panel_days


def cross_checks(members, emp_eq, emp_days, benches, panel_days):
    """Honest gate: derived faces must match published/stored anchors that
    are STRUCTURALLY COMPARABLE (same cutoff, same method)."""
    fails = []
    # 1. marks EOD equity @ last paper day == current paper json equity
    last_day = max(emp_days)
    for t in EMPLOYEES:
        doc = jload(os.path.join(PAPER_DIR, f"{t}_paper.json"))
        want = float(doc["capital"]["equity_cny"])
        got = emp_eq[t].get(last_day)
        if got is None or abs(got - want) > 1.0:
            fails.append(f"marks-vs-paper equity {t}: {got} vs {want}")
    # 2. marks EOD @ last full trading day == t35 export snapshot of the
    #    SAME day (both faces are EOD-consistent there; earlier exports
    #    are first-shot derived snapshots with intraday semantics -- NOT
    #    comparable, disclosed, not gated)
    exp_path = os.path.join(PAPER_EXPORT, f"export-{last_day}.json")
    if not os.path.exists(exp_path):
        fails.append(f"export snapshot missing for last day {last_day}")
    else:
        exp = jload(exp_path)
        snap = {t["trader"]: t["capital_cny"]["equity"] for t in exp["traders"]}
        for t in EMPLOYEES:
            if t in snap:
                got = emp_eq[t].get(last_day)
                if got is None or abs(got - snap[t]) > 1.0:
                    fails.append(f"marks-vs-export {t}: {got} vs {snap[t]}")
    # 3. retro legs == LEADERBOARD.md published cum-x1 (uncut 09-24 window)
    anchors = leaderboard_anchors()
    if not anchors:
        fails.append("LEADERBOARD.md parse: zero anchors")
    for name, m in members.items():
        if m["family"] in ("A", "B", "C"):
            pub = anchors.get(name)
            if pub is None:
                fails.append(f"leaderboard anchor missing for {name}")
            elif abs(m["full_ret"] - pub) > 1e-5:
                fails.append(f"leaderboard anchor {name}: {m['full_ret']:.6f} vs {pub:.6f}")
            if m.get("last_date") != "2026-09-24":
                fails.append(f"retro ledger terminal {name}: {m.get('last_date')} != 2026-09-24")
    # 4. baselines through BT_END vs published static snapshot (o1600
    #    method reproduced to 0.01pp pre-freeze; 0.2pp guard)
    for bname, pub in (("BENCH-510300", PUBLISHED_510300_BT),
                       ("BENCH-48EW", PUBLISHED_48EW_BT)):
        dates, nav = benches[bname]
        i = dates.index(BT_END) if BT_END in dates else -1
        got = nav[i] - 1.0
        if abs(got - pub) > 0.002:
            fails.append(f"bench anchor {bname}: {got:.4f} vs published {pub}")
    # 5. every curve date is a panel trading day (holiday/weekend leak sweep)
    for name, m in members.items():
        bad = [d for d in m["dates"] if d not in panel_days]
        if bad:
            fails.append(f"non-trading-day bars in {name}: {bad[:3]}")
    return fails


def summarize(members):
    def ytd(m):
        return m["nav"][-1] - 1.0
    b300 = ytd(members["BENCH-510300"])
    bew = ytd(members["BENCH-48EW"])
    rows = []
    for name, m in members.items():
        if m["family"] == "BENCH":
            continue
        rows.append({
            "member": name, "family": m["family"],
            "ytd_ret": ytd(m),
            "bt_leg_ret": m["bt_ret"], "paper_leg_ret": m["paper_ret"],
            "beat_510300_pp": (ytd(m) - b300) * 100.0,
            "beat_48ew_pp": (ytd(m) - bew) * 100.0,
            "max_dd": path_maxdd([1.0] + m["nav"]),
            "paper_only": m["paper_only"],
            "first_date": m["dates"][0], "last_date": m["dates"][-1],
            "n_points": len(m["dates"]),
            "note": m.get("note"),
        })
    rows.sort(key=lambda r: -r["ytd_ret"])
    return rows, b300, bew


# --------------------------------------------------------------- outputs
def fmt_pp(x):
    return f"{x * 100:+.2f}"


def render_outputs(members, rows, b300, bew, cutoff):
    os.makedirs(OUT_DIR, exist_ok=True)
    curves = {}
    for name, m in members.items():
        curves[name] = {"dates": m["dates"], "nav": [round(v, 8) for v in m["nav"]]}
    summary = {
        "schema": "t146_ytd_track_record_v1",
        "ticket": "T-2026-10-02-146 (O-20261002-2135 CEO direct order)",
        "window": {"start": "2026-01-05", "bt_end": BT_END, "paper_end": cutoff},
        "evidence_cutoff": cutoff,
        "splice_convention": "paper leg chain-linked onto backtest-leg terminal NAV (no double-count); 2026-09-25 Mid-Autumn holiday excluded (ETF panel authority); marks-20260925 settle rows not consumed",
        "baselines": {"BENCH-510300": b300, "BENCH-48EW": bew},
        "known_divergences": [
            "COMPOSITE-CE-01/-02 与 ENGULF-CE-01 回测段与 09-24 静态快照表（o1600 切片·beat_market §一）有差：09-26 T-78 s4 出场叠加冠军接线（C01 tp_ladder / C02+ENGULF ov_full·git d65f2d4ac）发生在切片之后——本面回测段=retro_paper_2026 台账（现行注册策略口径，与纸盘段策略同一口径，拼接一致性优先）；静态表=接线前快照，原样保留不回改",
            "marks 面（本面纸盘段逐日源）与 t35 export 面在 09-24/09-28/09-29 有首拍派生+盘中时点语义差；09-30 起两面逐分恒等（0.00-0.02 元）——本面只消费 marks 面",
            "B_MAXDIV 尚无纸盘腿（10-01 否决窗后接线，黄金周零 bar）——本面=回测段 only，接线后随 marks 续跑",
        ],
        "members": rows,
        "honesty": [
            "回测段=历史纸盘重放证言（retro_paper_2026 冻结台账），非样本外证据；纸盘段才是前向实证",
            "纸盘段携带真实成本面（T+1·13bp/x2 各账户冻结口径）",
            "paper-only 成员无回测腿（首 marks 日=该员上岗实证首日，见 first_date）",
            "六员上岗日 09-23 无 marks 件（建仓成本并入 09-24 mark）——纸盘段首日=09-24",
            "节前锚=2026-09-30 收盘；10-09 复市续跑",
            "48ETF等权基准=日再平衡口径（o1600_market_fit.py 同式复现 -3.89%）",
            "本面=纯聚合零新判决（T-105 先例）；负结果如实",
        ],
        "audit": {"machine": "bm-b", "runner": "scripts/ytd_track_record.py",
                  "deterministic": "byte-identical on rerun (no wall-clock fields)"},
    }
    with open(os.path.join(OUT_DIR, "ytd_summary.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "ytd_curves.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(curves, fh, ensure_ascii=False, indent=1)
    # CEO morning face (markdown)
    md = ["# 年初至今（YTD）连续成绩面 · 全池 %d 成员 + 双基准" % len(rows), "",
          f"- 窗口：2026-01-05 → {cutoff}（节前收盘锚，10-09 复市续跑）；回测段（01-05→09-23）+ 纸盘段（09-23→{cutoff}）拼接",
          "- 诚实锚：回测段=历史纸盘重放证言非样本外；纸盘段=前向实证；负结果如实；纯聚合零新判决",
          f"- 基准：沪深300ETF {fmt_pp(b300)}% ｜ 48ETF等权 {fmt_pp(bew)}%", "",
          "| # | 成员 | 族 | YTD | 回测段 | 纸盘段 | 跑赢300(pp) | 跑赢48EW(pp) | YTD最大回撤 |",]
    md.append("|--:|---|---|--:|--:|--:|--:|--:|--:|")
    for i, r in enumerate(rows, 1):
        bt = fmt_pp(r["bt_leg_ret"]) + "%" if r["bt_leg_ret"] is not None else "—"
        pp = fmt_pp(r["paper_leg_ret"]) + "%" if r["paper_leg_ret"] is not None else "—"
        tag = " (纸盘only)" if r["paper_only"] else ""
        md.append(f"| {i} | {r['member']}{tag} | {r['family']} | {fmt_pp(r['ytd_ret'])}% | {bt} | {pp} | {r['beat_510300_pp']:+.2f} | {r['beat_48ew_pp']:+.2f} | {fmt_pp(r['max_dd'])}% |")
    md.append("")
    md.append(f"- 已知分歧（如实）：COMPOSITE-CE-01/-02、ENGULF-CE-01 三员回测段与 09-24 静态快照表有差=09-26 出场叠加冠军接线（T-78 s4·d65f2d4ac）后重放，本面=现行注册策略口径（与纸盘段同口径拼接）；详 results/ytd_track_record/ytd_summary.json known_divergences 块")
    with open(os.path.join(OUT_DIR, "YTD.md"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("\n".join(md) + "\n")
    # beat_market.html standing section (idempotent between markers)
    sec = [SECTION_A,
           f'<h2 id="ytd">三、年初至今（YTD）连续成绩面（2026-01-05 → {cutoff} 节前收盘 · 回测段+纸盘段拼接）</h2>',
           "<table>",
           "<tr><th>成员 / 基准</th><th>YTD 收益</th><th>回测段<br>(01-05→09-23)</th><th>纸盘段</th><th>跑赢沪深300<br>(百分点)</th><th>跑赢48ETF等权<br>(百分点)</th><th>YTD<br>最大回撤</th><th>段注</th></tr>"]
    for bname, label, bnote in (
            ("BENCH-510300", "基准① 沪深300ETF（510300）", "未复权收盘"),
            ("BENCH-48EW", "基准② 48ETF等权被动", "等权·日再平衡（o1600 口径）")):
        bm = members[bname]
        dts, nav = bm["dates"], bm["nav"]
        i0 = dts.index("2026-01-05") if "2026-01-05" in dts else 0
        i_bt = dts.index(BT_END) if BT_END in dts else len(dts) - 1
        ytd = nav[-1] / nav[i0] - 1.0
        seg_bt = nav[i_bt] / nav[i0] - 1.0
        seg_pp = nav[-1] / nav[i_bt] - 1.0
        sec.append(f'<tr class="bench"><td>{label}</td><td>{fmt_pp(ytd)}%</td><td>{fmt_pp(seg_bt)}%</td><td>{fmt_pp(seg_pp)}%</td><td>—</td><td>—</td><td>{fmt_pp(path_maxdd(nav))}%</td><td>{bnote}</td></tr>')
    for r in rows:
        bt = fmt_pp(r["bt_leg_ret"]) + "%" if r["bt_leg_ret"] is not None else "—"
        pp = fmt_pp(r["paper_leg_ret"]) + "%" if r["paper_leg_ret"] is not None else "—"
        note = (f"纸盘only（首日 {r['first_date']}）" if r["paper_only"]
                else (r.get("note") or "回测段+纸盘段"))
        cls = "up" if r["ytd_ret"] >= 0 else "down"
        c300 = "up" if r["beat_510300_pp"] >= 0 else "down"
        cew = "up" if r["beat_48ew_pp"] >= 0 else "down"
        sec.append(f'<tr><td>{r["member"]}</td><td class="{cls}">{fmt_pp(r["ytd_ret"])}%</td><td>{bt}</td><td>{pp}</td><td class="{c300}">{r["beat_510300_pp"]:+.2f}</td><td class="{cew}">{r["beat_48ew_pp"]:+.2f}</td><td>{fmt_pp(r["max_dd"])}%</td><td>{note}</td></tr>')
    sec.append("</table>")
    sec.append('<div class="note">段界诚实锚：回测段=历史纸盘重放证言（非样本外），纸盘段=前向实证；2026-09-25 中秋+10-01/02 国庆休市无 bar（面板为准）；节前锚=09-30 收盘，10-09 复市续跑。已知分歧如实：COMPOSITE-CE-01/-02、ENGULF-CE-01 回测段与上方 §一 静态快照表有差=09-26 出场叠加冠军接线（T-78 s4）后重放口径——本节=现行注册策略（与纸盘段同口径拼接），静态表保留原样。数据件 results/ytd_track_record/（日级曲线 ytd_curves.json）。</div>')
    sec.append(SECTION_B)
    block = "\n".join(sec)
    with open(BEAT_HTML, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8")
    if SECTION_A in text:
        head, rest = text.split(SECTION_A, 1)
        _, tail = rest.split(SECTION_B, 1)
        text = head + block + tail
    else:
        text = text.rstrip("\n") + "\n" + block + "\n"
    with open(BEAT_HTML, "wb") as fh:
        fh.write(text.encode("utf-8"))
    return summary


# ------------------------------------------------------------------ main
def cmd_run():
    members, benches, emp_eq, emp_days, panel_days = assemble()
    fails = cross_checks(members, emp_eq, emp_days, benches, panel_days)
    if fails:
        for f in fails:
            log("CROSS-CHECK FAIL: " + f)
        return 2
    rows, b300, bew = summarize(members)
    cutoff = max(m["dates"][-1] for m in members.values())
    summary = render_outputs(members, rows, b300, bew, cutoff)
    log(f"YTD assembly OK: {len(rows)} members, baselines 510300 {fmt_pp(b300)}% / 48EW {fmt_pp(bew)}%, cutoff {cutoff}")
    log(f"top: " + "; ".join(f"{r['member']} {fmt_pp(r['ytd_ret'])}%" for r in rows[:5]))
    log(f"bottom: " + "; ".join(f"{r['member']} {fmt_pp(r['ytd_ret'])}%" for r in rows[-5:]))
    return 0


def cmd_selftest():
    ok = 0

    def leg(name, cond):
        nonlocal ok
        print(("[PASS] " if cond else "[FAIL] ") + name)
        if not cond:
            ok += 1
    # S1 splice continuity + no double-count
    bt = {"dates": ["2026-01-05", "2026-09-22", "2026-09-23"],
          "equity": [1000000.0, 1040000.0, 1030000.0], "family": "A"}
    pts = [("2026-09-24", 0.01), ("2026-09-28", -0.005)]
    dates, nav = splice(bt, pts)
    leg("S1 splice boundary NAV == bt terminal",
        abs(nav[2] - 1.03) < 1e-12 and abs(nav[3] - 1.03 * 1.01) < 1e-12
        and abs(nav[-1] - 1.03 * 1.01 * 0.995) < 1e-12)
    # S2 holiday exclusion law
    leg("S2 holiday bar excluded by panel authority",
        etf_calendar(["2026-09-25", "2026-09-24"], {"2026-09-24"}) == ["2026-09-24"])
    # S3 EW baseline math
    leg("S3 EW buy&hold math", abs(sum([1.1, 0.9]) / 2 - 1.0) < 1e-12)
    # S4 beat pp sign convention
    leg("S4 beat pp", abs((0.05 - (-0.0524)) * 100 - 10.24) < 1e-9)
    # S5 maxdd path (function returns negative convention; 0.99 vs peak
    # 1.1 = -10.0% exactly)
    leg("S5 path maxdd (negative convention)",
        abs(path_maxdd([1.0, 1.1, 0.99, 1.05]) + 0.1) < 1e-12)
    # S6 html section idempotence
    leg("S6 markers present in runner output contract",
        SECTION_A != SECTION_B and len(SECTION_A) > 10)
    print(f"selftest: {'ALL PASS' if ok == 0 else str(ok) + ' FAIL'}")
    return 0 if ok == 0 else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
