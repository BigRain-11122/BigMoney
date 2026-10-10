"""REGIME-MATRIX P0 runner -- strategy x regime zero-burn reslice (T-2026-10-10-182).

Order source: O-20261010-1725-bm-a.md (CEO direct, four-market dispatch law)
  + O-20261010-1825 sec.2.4 early start (bm-a lane, zero-burn v1 reslice, 10-13/14 delivery).
Axis: REGIME-5 v1.0 labels (results/regime5_labels/REGIME5-2026-09-30.json)
  + canonical panic column results/regime_axis_m1/panic_windows.json
  (25 days / 12 windows, bm-b face = reconciliation canonical per
  research/REGIME_AXIS_PANIC_RECONCILIATION.md).
Streams v1: LOWAMP-P3 judged continuous streams (deep axis, base face = net of
  x1 cost) -- the P0 row "low-vol defensive family" (four cells + equal-weight composite).
  All other P0 rows are registered as pending (stream pinning = next slice) or
  insufficient-history (SYSTEM-V1 paper since 2026-09-24).
Baseline: 5y deposit 1.30%/yr (major-bank posted rate 2026-09,
  research/DIRECTION_REVIEW_BM_INPUT.md; O-1705 CEO law "minimum floor = beat the
  current 5-year fixed deposit rate"; numeric line disclosed in every report).

Verdicts (v1 proxy, disclosed as attribution slice -- NOT a new criterion claim):
  home_pass      home-regime 12m window median return >= deposit baseline
  away_unhurt    non-home regimes: median window return >= 0 (n>=30 windows)
  gate_off       non-home regimes: median window return <  0 (n>=30 windows)
  Significance testing (t/block-bootstrap) is deferred to the 10-17~24
  dispatch-law prereg slice; this slice is attribution-only per order sec.4.

Usage:
  python scripts/regime_matrix_p0.py run        # produce matrix json + md
  python scripts/regime_matrix_p0.py selftest   # hermetic offline checks
Exit codes: 0 normal, 2 mechanism failure.
"""
import argparse
import datetime as _dt
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "regime_matrix_p0")

REGIME5_LABELS = os.path.join(ROOT, "results", "regime5_labels",
                             "REGIME5-2026-09-30.json")
PANIC_WINDOWS = os.path.join(ROOT, "results", "regime_axis_m1",
                             "panic_windows.json")
LOWAMP_CONT = os.path.join(ROOT, "results", "lowamp_p3", "cont_{cell}_deep_base.json")
LOWAMP_CELLS_JSONL = os.path.join(ROOT, "results", "lowamp_p3",
                                  "cells_{cell}_deep_base.jsonl")
SYSTEM_V1_PAPER = os.path.join(ROOT, "results", "system_v1_paper",
                               "SYSTEM-V1_paper.json")

LOWAMP_CUTOFF = pd.Timestamp("2026-09-22")   # LOWAMP-P3 D2 lockbox, prereg sec.2
W12M = 252                                    # t22/lowamp frozen window bars
DEPOSIT_BASELINE_5Y = 0.0130                  # 1.30%/yr, disclosed source
STATES = ["BULL", "CHOP", "GRIND", "BEAR", "SUPPORT"]
MIN_WINDOWS_VERDICT = 30                      # n>=30 floors a verdict column

# theme wave-rider stream: THEME-JUDGE-P1 (T-173) adjudicated artifact, cell
# TJ-FULL-x1 -- pooled equal-weight per-date returns over full cluster rides,
# x1 cost, cash (0 return) on non-ride days, 2014-12-05..2026-09-22 (= evidence
# cutoff). Declared bull-market home weapon per O-1725 sec.2 P0.
THEME_SOURCE = os.path.join(ROOT, "results", "theme_judge_p1",
                            "theme_judge_p1_results.json")
THEME_CELL = "TJ-FULL-x1"
THEME_NET_TOL = 5e-6                          # nav reconstruction anchor tolerance

# P0 registry: declared home regime + stream status. Pending rows carry the
# candidate source so the next slice can pin them without re-research.
LOWAMP_HOME = "BEAR"   # defensive family declared home (REGIME_STYLE_MATRIX_V1
                       # sec.2 defensive_six/lowvol = bear-market home faces)
P0_REGISTRY = [
    {"id": "lowamp-LA-EQ", "group": "lowvol-defensive", "home": LOWAMP_HOME,
     "status": "stream_wired", "source": "results/lowamp_p3/cont_LA-EQ_deep_base.json"},
    {"id": "lowamp-LA-EDGE", "group": "lowvol-defensive", "home": LOWAMP_HOME,
     "status": "stream_wired", "source": "results/lowamp_p3/cont_LA-EDGE_deep_base.json"},
    {"id": "lowamp-LA-REP", "group": "lowvol-defensive", "home": LOWAMP_HOME,
     "status": "stream_wired", "source": "results/lowamp_p3/cont_LA-REP_deep_base.json"},
    {"id": "lowamp-LA-T3", "group": "lowvol-defensive", "home": LOWAMP_HOME,
     "status": "stream_wired", "source": "results/lowamp_p3/cont_LA-T3_deep_base.json"},
    {"id": "lowamp-FAMILY-EW", "group": "lowvol-defensive", "home": LOWAMP_HOME,
     "status": "stream_wired", "source": "equal-weight daily mean of the four lowamp cells"},
    {"id": "four-asset-corebook", "group": "four-asset", "home": None,
     "status": "awaiting_stream",
     "source": "candidate: results/cross_start_robustness/face_b.json (summary only, Jan starts); daily stream not materialized in-library"},
    {"id": "six-members", "group": "defensive-six", "home": LOWAMP_HOME,
     "status": "awaiting_stream",
     "source": "candidate: corebook_closeout_p1 faces reference source artifacts by sha; sleeve stream files not pinned this slice"},
    {"id": "SYSTEM-V1", "group": "system-v1", "home": None,
     "status": "insufficient_history",
     "source": "results/system_v1_paper/SYSTEM-V1_paper.json -- paper since 2026-09-24, 12m windows exist only after 2027-09"},
    {"id": "dip-rebound-trio", "group": "dip-rebound", "home": "BEAR",
     "status": "awaiting_stream",
     "source": "declared bear-market weapon (O-1725 sec.2 P0); refine_bench rev_p2 artifacts are trade-level (entries/trades/exits) -- daily-stream reconstruction = next slice"},
    {"id": "theme-wave-rider", "group": "theme", "home": "BULL",
     "status": "stream_wired",
     "source": "results/theme_judge_p1/theme_judge_p1_results.json cell TJ-FULL-x1 (pooled equal-weight daily stream, x1 cost, cash on non-ride days; nav anchor = pooled_net; O-1725 sec.2 declared bull weapon)"},
]


def _d(ts):
    return str(pd.Timestamp(ts).date())


def load_regime_axis():
    with open(REGIME5_LABELS, encoding="utf-8") as fh:
        lab = json.load(fh)
    labels = {}
    for row in lab["labels"]:
        labels[str(row["date"])] = str(row["state"])
    with open(PANIC_WINDOWS, encoding="utf-8") as fh:
        pan = json.load(fh)
    panic_days = set()
    for d in pan["days"]:
        panic_days.add(str(d["date"]) if isinstance(d, dict) else str(d))
    return {"labels": labels, "n_labels": len(labels),
            "label_cutoff": lab.get("cutoff"),
            "panic_days": panic_days,
            "panic_n_days": pan.get("n_days"),
            "panic_n_windows": pan.get("n_windows"),
            "panic_source": "bm-b canonical per REGIME_AXIS_PANIC_RECONCILIATION.md"}


def load_panel_dates():
    """Deep-axis panel trading dates truncated at the LOWAMP-P3 cutoff,
    loaded through the same repo loaders the engine used (import reuse,
    zero engine rewrite). Read-only on Money02 cache."""
    from live.paper import build_panels
    from t22_virtual_timepoints import _load_axis_prices
    prices = _load_axis_prices("deep")
    prices = {s: df[df.index <= LOWAMP_CUTOFF] for s, df in prices.items()}
    close = build_panels(prices)["close"]
    return [_d(x) for x in close.index]


def load_cont_stream(cell, panel_dates):
    """Load one lowamp cont stream and map returns onto panel dates.

    Returns (dates, rets, nav) with verification anchors:
      A1 len(returns) == n_days - 1  -> rets[i] is the return INTO panel_dates[i+1]
      A2 nav reconstruction hits nav_last
      A3 panel anchor: jsonl pos 1599 == 2020-01-02 date mapping
    Note (honesty): the lowamp cells-*.jsonl per-start windows (ret_12m etc.) are
    FRESH-RUN virtual-timepoint backtests, NOT slices of this continuous stream,
    so they are a date-mapping anchor only -- never a return-value anchor.
    """
    path = LOWAMP_CONT.format(cell=cell)
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    rets = [float(x) for x in d["returns"]]
    n_days = int(d["n_days"])
    if len(rets) != n_days - 1:
        raise SystemExit(f"matrix p0 mechanism: cont {cell} len {len(rets)} != n_days-1 {n_days-1}")
    if len(panel_dates) != n_days:
        raise SystemExit(f"matrix p0 mechanism: panel {len(panel_dates)} != n_days {n_days} (cutoff mismatch)")
    nav = [float(d["nav_first"])]
    for r in rets:
        nav.append(nav[-1] * (1.0 + r))
    recon_err = abs(nav[-1] - float(d["nav_last"])) / float(d["nav_last"])
    if recon_err > 1e-6:
        raise SystemExit(f"matrix p0 mechanism: cont {cell} nav recon err {recon_err}")
    jpath = LOWAMP_CELLS_JSONL.format(cell=cell)
    anchor_pos = None
    with open(jpath, encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("face") == "base" and str(row.get("start")) == "2020-01-02":
                anchor_pos = int(row["pos"])
                break
    if anchor_pos is None:
        raise SystemExit(f"matrix p0 mechanism: no jsonl anchor row for {cell}")
    if panel_dates[anchor_pos] != "2020-01-02":
        raise SystemExit(f"matrix p0 mechanism: panel pos {anchor_pos} -> {panel_dates[anchor_pos]} != 2020-01-02")
    return panel_dates[1:], rets, nav[1:]


def window_metrics(rets, nav, s, w):
    """In-window return, sharpe, worst drawdown for a window entered at the
    close of dates[s]: captures the next w returns rets[s+1..s+w] =
    nav[s+w]/nav[s]-1 (authoritative NAV ratio; sharpe/dd from the same span)."""
    seg = rets[s + 1:s + w + 1]
    r = nav[s + w] / nav[s] - 1.0
    peak = nav[s]
    worst = 0.0
    for i in range(s, s + w + 1):
        if nav[i] > peak:
            peak = nav[i]
        dd = nav[i] / peak - 1.0
        if dd < worst:
            worst = dd
    arr = np.asarray(seg, dtype=float)
    sd = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    mean = float(arr.mean())
    sharpe = (mean / sd) * math.sqrt(252.0) if sd > 0 else 0.0
    return r, sharpe, worst


def _dist(vals):
    if not vals:
        return {"n": 0}
    a = sorted(vals)
    n = len(a)

    def q(p):
        k = (n - 1) * p
        f = int(math.floor(k))
        c = min(f + 1, n - 1)
        return a[f] + (a[c] - a[f]) * (k - f)
    return {"n": n, "median": q(0.5), "p25": q(0.25), "p75": q(0.75),
            "min": a[0], "max": a[-1],
            "pos_share": sum(1 for v in a if v > 0) / n}


def slice_stream(sid, home, dates, rets, nav, axis):
    """All-start 12m rolling windows, grouped by regime-at-start (+ panic overlay)."""
    labels = axis["labels"]
    panic = axis["panic_days"]
    per = {st: {"ret": [], "sharpe": [], "dd": []} for st in STATES}
    extreme = {"ret": [], "sharpe": [], "dd": []}
    n_unlabeled = 0
    w = W12M
    for s in range(0, len(rets) - w):
        state = labels.get(dates[s])
        if state is None or state not in per:
            n_unlabeled += 1
            continue
        r, sharpe, dd = window_metrics(rets, nav, s, w)
        per[state]["ret"].append(r)
        per[state]["sharpe"].append(sharpe)
        per[state]["dd"].append(dd)
        if any(d in panic for d in dates[s:s + w + 1]):
            extreme["ret"].append(r)
            extreme["sharpe"].append(sharpe)
            extreme["dd"].append(dd)
    cells = {}
    for st in STATES:
        cells[st] = {"ret": _dist(per[st]["ret"]),
                     "sharpe_median": (lambda v: sorted(v)[len(v)//2] if v else None)(per[st]["sharpe"]),
                     "worst_dd": min(per[st]["dd"]) if per[st]["dd"] else None}
    cells["EXTREME"] = {"ret": _dist(extreme["ret"]),
                        "sharpe_median": (lambda v: sorted(v)[len(v)//2] if v else None)(extreme["sharpe"]),
                        "worst_dd": min(extreme["dd"]) if extreme["dd"] else None,
                        "note": "overlay: windows containing >=1 canonical panic day (regime-agnostic)"}
    verdicts = {"home": home, "home_pass": None, "away_unhurt": {},
                "gate_off": [], "n_unlabeled_starts": n_unlabeled,
                "verdict_floor_n": MIN_WINDOWS_VERDICT,
                "proxy_disclosure": "v1 proxy: home_pass=median>=deposit baseline; away/gate use median sign at n>=30; significance tests deferred to dispatch-law prereg slice"}
    if home in cells and cells[home]["ret"].get("n", 0) >= MIN_WINDOWS_VERDICT:
        verdicts["home_pass"] = bool(cells[home]["ret"]["median"] >= DEPOSIT_BASELINE_5Y)
    for st in STATES:
        if st == home:
            continue
        n = cells[st]["ret"].get("n", 0)
        if n < MIN_WINDOWS_VERDICT:
            verdicts["away_unhurt"][st] = {"n": n, "verdict": "insufficient_n"}
            continue
        med = cells[st]["ret"]["median"]
        ok = med >= 0.0
        verdicts["away_unhurt"][st] = {"n": n, "median": med,
                                       "verdict": "unhurt" if ok else "harmed"}
        if not ok:
            verdicts["gate_off"].append(st)
    return {"id": sid, "cells": cells, "verdicts": verdicts}


def _pending_row(spec):
    return {"id": spec["id"], "group": spec["group"], "home": spec["home"],
            "status": spec["status"], "source": spec["source"],
            "cells": {}, "verdicts": None}


def load_theme_stream():
    """Load the THEME-JUDGE-P1 TJ-FULL-x1 pooled daily stream.

    Returns (dates, rets, nav) in the matrix convention (rets[i] = return
    INTO dates[i]; nav[i] = cumulative NAV at close of dates[i]) with
    verification anchors:
      A1 len(dates) == len(returns) (1:1 per-date pooled return)
      A2 nav reconstruction: prod(1+r)-1 == pooled_net within THEME_NET_TOL
    """
    with open(THEME_SOURCE, encoding="utf-8") as fh:
        d = json.load(fh)
    cell = d["cells"][THEME_CELL]
    dates = [str(x) for x in cell["dates"]]
    rets = [float(x) for x in cell["returns"]]
    if len(dates) != len(rets):
        raise SystemExit(f"matrix p0 mechanism: theme stream len mismatch "
                         f"{len(dates)} dates vs {len(rets)} returns")
    nav = [1.0]
    for r in rets:
        nav.append(nav[-1] * (1.0 + r))
    nav = nav[1:]
    net_recon = nav[-1] - 1.0
    net_claim = float(cell["pooled_net"])
    if abs(net_recon - net_claim) > THEME_NET_TOL:
        raise SystemExit(f"matrix p0 mechanism: theme nav anchor "
                         f"{net_recon:.6f} != pooled_net {net_claim:.6f}")
    return dates, rets, nav


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    axis = load_regime_axis()
    panel_dates = load_panel_dates()
    loaded = {}
    for cell in ["LA-EQ", "LA-EDGE", "LA-REP", "LA-T3"]:
        dates, rets, nav = load_cont_stream(cell, panel_dates)
        loaded[cell] = (dates, rets, nav)
    n_ret = len(next(iter(loaded.values()))[1])
    fam_rets = []
    for i in range(n_ret):
        fam_rets.append(sum(loaded[c][1][i] for c in loaded) / len(loaded))
    fam_nav = [1.0]
    for r in fam_rets:
        fam_nav.append(fam_nav[-1] * (1.0 + r))
    fam_nav = fam_nav[1:]
    fam_dates = loaded["LA-EQ"][0]
    # duplicate-stream disclosure (upstream LOWAMP-P3 property: distinct cells
    # can materialize identical return streams; family EW then overweights them)
    dup_groups = []
    seen = {}
    for c in loaded:
        key = hash(tuple(loaded[c][1]))
        seen.setdefault(key, []).append(c)
    for g in seen.values():
        if len(g) > 1:
            dup_groups.append(g)
    dup_note = ("upstream duplicate streams: " + "; ".join(
        "==".join(g) for g in dup_groups) +
        " -- family EW overweights these; disclosed per honesty law"
    ) if dup_groups else None

    rows = []
    for spec in P0_REGISTRY:
        if spec["status"] != "stream_wired":
            rows.append(_pending_row(spec))
            continue
        if spec["id"] == "lowamp-FAMILY-EW":
            rows.append(slice_stream(spec["id"], spec["home"], fam_dates,
                                     fam_rets, fam_nav, axis))
        elif spec["id"] == "theme-wave-rider":
            t_dates, t_rets, t_nav = load_theme_stream()
            rows.append(slice_stream(spec["id"], spec["home"], t_dates,
                                     t_rets, t_nav, axis))
        else:
            cell = spec["id"].replace("lowamp-", "")
            dates, rets, nav = loaded[cell]
            rows.append(slice_stream(spec["id"], spec["home"], dates,
                                     rets, nav, axis))

    cutoff = axis["label_cutoff"]
    out = {
        "schema": "regime_matrix_p0_v1",
        "batch": "REGIME-MATRIX-P0-V1",
        "ticket": "T-2026-10-10-182",
        "order_ref": "O-20261010-1725-bm-a.md + O-20261010-1825 sec.2.4",
        "generated": _dt.datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": "2026-09-22",
        "zero_burn": True,
        "adjudication_nature": "attribution reslice of judged streams; NOT a new criterion claim (order sec.4)",
        "window": {"bars": W12M, "convention": "regime at window start (all starts)"},
        "deposit_baseline_5y": DEPOSIT_BASELINE_5Y,
        "deposit_baseline_source": "major-bank 5y posted rate 2026-09 ~1.30%/yr (research/DIRECTION_REVIEW_BM_INPUT.md); CEO law O-1705",
        "regime_axis": {"labels_file": "results/regime5_labels/REGIME5-2026-09-30.json",
                        "n_label_days": axis["n_labels"],
                        "label_cutoff": cutoff,
                        "panic_file": "results/regime_axis_m1/panic_windows.json",
                        "panic_n_days": axis["panic_n_days"],
                        "panic_n_windows": axis["panic_n_windows"],
                        "panic_canonical": axis["panic_source"]},
        "small_sample_disclosure": ("EXTREME column spans only ~25 panic days over full "
                                    "history -> low power, honest disclosure per order sec.4"),
        "dup_stream_disclosure": dup_note,
        "rows": rows,
    }
    jpath = os.path.join(OUT_DIR, f"P0-MATRIX-v1-{cutoff}.json")
    with open(jpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    mpath = os.path.join(OUT_DIR, f"P0-MATRIX-v1-{cutoff}.md")
    with open(mpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(out))
    latest = os.path.join(OUT_DIR, "latest.json")
    with open(latest, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"matrix": jpath, "md": mpath, "cutoff": cutoff,
                   "generated": out["generated"]}, fh, indent=1)
    print(json.dumps({"matrix": jpath, "md": mpath, "rows": len(rows),
                      "wired": sum(1 for r in rows if r.get("verdicts"))},
                     ensure_ascii=False))


def render_md(out):
    L = []
    L.append("# P0 矩阵 v1 — 策略×政体零烧切片（归因面·非判据宣称）")
    L.append("")
    L.append(f"- 令源：O-20261010-1725（策略×政体全量分阶段测试）·生成：{out['generated']}")
    L.append(f"- 政体轴：REGIME-5 v1.0 标签（{out['regime_axis']['n_label_days']} 日·cutoff {out['regime_axis']['label_cutoff']}）"
             f"+ 恐慌窗正典 25 日/12 窗（bm-b 面·对账定谳）")
    L.append(f"- 定存底线：5 年期 {out['deposit_baseline_5y']*100:.2f}%/年（{out['deposit_baseline_source']}）")
    L.append("- 窗口：12 月滚动（252 bar）·全起点口径·起点政体归属；EXTREME=含恐慌日窗（叠加列）")
    L.append("- 诚实边界：" + out["small_sample_disclosure"])
    L.append("")
    L.append("## 已接线行（12 月窗中位收益 ×各政体）")
    L.append("")
    L.append("| 行 | BULL | CHOP | GRIND | BEAR | SUPPORT | EXTREME | 主场判定 | 客场 |")
    L.append("|---|---|---|---|---|---|---|---|---|")

    def pct(v):
        return f"{v*100:.2f}%" if v is not None else "-"

    for r in out["rows"]:
        if not r.get("verdicts"):
            continue
        cells = r["cells"]
        vals = []
        for st in STATES + ["EXTREME"]:
            d = cells[st]["ret"]
            vals.append(f"{pct(d.get('median'))} (n={d.get('n',0)})" if d.get("n") else "-")
        v = r["verdicts"]
        home_txt = f"主场 {v['home']}：{'达标' if v['home_pass'] else '未达'}"
        away = "; ".join(f"{st}:{x.get('verdict','')}" for st, x in v["away_unhurt"].items())
        L.append(f"| {r['id']} | " + " | ".join(vals) + f" | {home_txt} | {away} |")
    L.append("")
    L.append("## 待接线行（下一切片钉流）")
    L.append("")
    for r in out["rows"]:
        if r.get("verdicts"):
            continue
        L.append(f"- **{r['id']}**（home={r.get('home')}·{r['status']}）：{r['source']}")
    L.append("")
    L.append("## 三判口径（v1 代理·披露）")
    L.append("")
    L.append("1. 主场达标 = 主场政体 12 月窗中位收益 ≥ 定存底线 1.30%（n≥30 才判）")
    L.append("2. 客场不伤 = 非主场政体中位收益 ≥ 0（n≥30 才判；不足=insufficient_n）")
    L.append("3. 需门控 = 非主场中位收益 < 0 → 调度律 off 候选")
    L.append("- 显著性检验（t/block-bootstrap）延后至 10-17~24 调度律预注册切片；本切片=归因非判据。")
    return "\n".join(L) + "\n"


def selftest():
    """Hermetic offline checks (no panel, no Money02, no network)."""
    ok = [0]
    def check(name, cond, detail=""):
        if cond:
            ok[0] += 1
            print(f"  PASS {name} {detail}")
        else:
            raise SystemExit(f"  FAIL {name} {detail}")

    # synthetic axis + stream
    base = _dt.date(2020, 1, 1)
    dates = []
    d = base
    while len(dates) < 3000:
        if d.weekday() < 5:
            dates.append(d.isoformat())
        d += _dt.timedelta(days=1)
    labels = {}
    for i, dt in enumerate(dates):
        labels[dt] = "BULL" if (i // 500) % 2 == 0 else "BEAR"
    panic = {dates[100], dates[101], dates[600]}
    axis = {"labels": labels, "panic_days": panic, "n_labels": len(labels)}
    rets = [0.001 if labels[dates[i]] == "BULL" else -0.0005 for i in range(len(dates))]
    nav = [1.0]
    for r in rets:
        nav.append(nav[-1] * (1 + r))
    nav = nav[1:]

    # t1 window metrics math (window at s captures rets[s+1..s+w])
    r, sharpe, dd = window_metrics(rets, nav, 0, W12M)
    check("t1 window ret compounding", abs(r - ((1.001) ** W12M - 1)) < 1e-9,
          f"ret={r:.6f}")
    # t2 regime assignment at start (all-start convention)
    row = slice_stream("synthetic", "BULL", dates, rets, nav, axis)
    c = row["cells"]
    # first 500 days starts are BULL windows; with W12M=252, starts 0..~249 in BULL
    check("t2 bull windows counted", c["BULL"]["ret"]["n"] > 0,
          f"n={c['BULL']['ret']['n']}")
    # t3 home verdict: bull median >= baseline -> home_pass
    check("t3 home_pass true for synthetic bull",
          row["verdicts"]["home_pass"] is True)
    # t4 away verdict: BEAR away & median<0 -> gate_off candidate
    check("t4 gate_off contains BEAR", "BEAR" in row["verdicts"]["gate_off"],
          f"gate_off={row['verdicts']['gate_off']}")
    # t5 panic overlay counts windows whose span (entry day .. last capture day) contains panic days
    n_extreme_expect = sum(1 for s in range(len(rets) - W12M)
                            if any(d2 in panic for d2 in dates[s:s + W12M + 1]))
    check("t5 panic overlay window count",
          c["EXTREME"]["ret"]["n"] == n_extreme_expect,
          f"n={c['EXTREME']['ret']['n']} expect={n_extreme_expect}")
    # t6 unlabeled starts skipped
    labels2 = dict(labels)
    del labels2[dates[10]]
    axis2 = {"labels": labels2, "panic_days": panic, "n_labels": len(labels2)}
    row2 = slice_stream("syn2", "BULL", dates, rets, nav, axis2)
    check("t6 unlabeled start skipped",
          row2["verdicts"]["n_unlabeled_starts"] == 1)
    # t7 deposit baseline constant disclosed value
    check("t7 deposit baseline", DEPOSIT_BASELINE_5Y == 0.0130)
    # t8 registry covers the six P0 groups from the order
    groups = {r["group"] for r in P0_REGISTRY}
    need = {"lowvol-defensive", "four-asset", "defensive-six", "system-v1",
            "dip-rebound", "theme"}
    check("t8 P0 groups complete", need <= groups, f"missing={need - groups}")
    # t9 verdict floor n
    small_axis = {"labels": {dates[i]: "BULL" for i in range(5)},
                  "panic_days": set(), "n_labels": 5}
    row3 = slice_stream("tiny", "BULL", dates[:10], [0.0]*10, [1.0]*10, small_axis)
    check("t9 insufficient_n below floor",
          row3["verdicts"]["home_pass"] is None)
    # t10 window metrics drawdown (w=3: captures rets[1..3])
    rets_dd = [0.01, -0.02, 0.005, 0.004]
    nav_dd = [1.0]
    for r2 in rets_dd:
        nav_dd.append(nav_dd[-1] * (1 + r2))
    nav_dd = nav_dd[1:]
    _, _, dd2 = window_metrics(rets_dd, nav_dd, 0, 3)
    check("t10 worst dd", abs(dd2 - (1.01 * 0.98 / 1.01 - 1)) < 1e-9,
          f"dd={dd2:.6f}")
    # t11 label five states closed set in axis file
    with open(REGIME5_LABELS, encoding="utf-8") as fh:
        lab_states = {r["state"] for r in json.load(fh)["labels"]}
    check("t11 label states closed set", lab_states <= set(STATES),
          f"states={sorted(lab_states)}")
    # t12 panic canonical file honesty fields
    with open(PANIC_WINDOWS, encoding="utf-8") as fh:
        pan = json.load(fh)
    check("t12 panic canonical 25/12",
          pan.get("n_days") == 25 and pan.get("n_windows") == 12)
    # t13 panic days may be dict-shaped entries (live-fire 21:1x: empty EXTREME col)
    ax3 = load_regime_axis()
    check("t13 panic day strings extracted", all(
        isinstance(x, str) and len(x) == 10 for x in ax3["panic_days"]),
        f"n={len(ax3['panic_days'])} sample={sorted(ax3['panic_days'])[:1]}")
    print(f"selftest: {ok[0]}/13 PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    args = ap.parse_args()
    if args.cmd == "run":
        run()
    else:
        selftest()


if __name__ == "__main__":
    main()
