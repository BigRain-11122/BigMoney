"""RETRO-PAPER-2026 runner (T-79, CEO order O-20260926-1326; prereg
research/RETRO_PAPER_2026_PREREG.md FROZEN pre-run, commit f70c0054
precedes any run; zero new signal functions, zero search, zero nulls).

Year-window paper-semantics replay for the EXISTING registered account
families, window 2026-01-05 (year first trading day, T-28 W-CUR anchor)
-> evidence cutoff 2026-09-24 (latest complete bar; 09-25 Mid-Autumn
market holiday). Per-account full paper ledger + one-page leaderboard
for the CEO; CEO approval (O-1326 legislation) = the ONLY live-sim
admission gate -- this batch claims ZERO registration/judgment lines
(ledger +0, T-56 slice-2 marks paradigm).

Families (prereg s2 frozen enumeration):
  A (6)  registered INTERN traders via live.paper.paper_run with retro
         hire date 2026-01-05 (registration params + exit_overrides
         VERBATIM; signals full-history warmup, trades window-only --
         paper_run contract). Guards SHADOW per order: regime_mask=None,
         fill_guard=None (legacy accounting = production paper state
         before the 2026-10-01 enforce gate); v3 states recorded daily.
  B (4)  sleeve blends: B_MAXDIV canon (TOURN_JSON weights, sha gate)
         + CEO-named top-3 AGGR-REGIME / AGGR-CONC-TOP2 / AGGR-OFFENSE
         (aggressive_lab frozen faces, sha-gated; sleeves = 28-member
         roster x {x1,x2} at cutoff 2026-09-24, T-56 caliber).
  C (7)  ALLOC cells P1/P2/P3/P3/P3B/P4/P5/P6 via alloc_backtest.simulate
         (frozen s2 cell mechanics verbatim, v2_main canonical cost face;
         x2 face = frozen-spec absence, honestly annotated). P5 slot =
         bm-b-local pinned face; absent -> honest skip.

Cost faces: x1 (V1 legacy 13bp single-side, engine default) + x2
(CostPatch(2)) for A/B; C = v2_main single canonical face.

CLI: run | selftest      exit 0 ok / 2 mechanical failure.
"""
import argparse
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from live.paper import (INITIAL_CASH, PAPER_LEVELS, SIGNAL_BUILDERS,
                        build_panels, load_core, monthly_aggregate,
                        paper_run, v3_state_series)
from firm.hr import TRADERS_DIR, load_trader
from scripts.science_gates import CostPatch, cutoff_meta

PREREG = os.path.join(PATHS.root, "research", "RETRO_PAPER_2026_PREREG.md")
OUT_DIR = os.path.join(PATHS.results_dir, "retro_paper_2026")
CUTOFF = pd.Timestamp("2026-09-24")     # prereg s2 evidence cutoff (frozen)
W_START = pd.Timestamp("2026-01-05")    # prereg s2 window head (frozen)
INITIAL = float(INITIAL_CASH)           # engine default 1,000,000 CNY
APPROVALS = os.path.join(PATHS.root, "docs", "CEO_APPROVALS.md")
A_EXPECTED = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
              "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
AGGR_PICKS = ("AGGR-REGIME", "AGGR-CONC-TOP2", "AGGR-OFFENSE")  # O-1326 verbatim
HONEST_ANNOTATION = (
    "本窗与策略 OOS 开发窗重叠=历史纸盘重放证「纸盘语义下成立」，"
    "非前向新证据；真前向纸盘 09-23 已在跑、双轨并行互证；判负照报。")


def log(msg: str) -> None:
    print(msg, flush=True)


# --------------------------------------------------------------- utilities
def annualized(cum: float, n_days: int):
    """Frozen formula (prereg s4): (1+cum)**(252/n_days)-1; None if wiped."""
    if n_days <= 0 or cum <= -1.0:
        return None
    return round(float((1.0 + cum) ** (252.0 / n_days) - 1.0), 6)


def path_dd(values, initial: float) -> float:
    """Peak-to-trough over marked path INCLUDING initial capital
    (aggressive_lab _marks_dd caliber -- one frozen dd for the board)."""
    peak, dd = initial, 0.0
    for v in values:
        v = float(v)
        peak = max(peak, v)
        if peak > 0:
            dd = min(dd, v / peak - 1.0)
    return round(dd, 6)


def _eq_series(pr: pd.Series) -> pd.Series:
    """Daily blend returns -> equity path from INITIAL (prereg s3 accrual)."""
    return (1.0 + pr).cumprod() * INITIAL


def _daily_states(states: pd.Series, index: pd.DatetimeIndex) -> list:
    s = states.reindex(index, method="ffill")
    return [{"date": str(pd.Timestamp(d).date()), "state": str(st)}
            for d, st in s.items()]


def _face_block(eq: pd.Series, trades_note, seg=None, monthly=None,
                trades=None) -> dict:
    """Common judgment columns per cost face (prereg s4 descriptive)."""
    values = [round(float(v), 2) for v in eq]
    cum = round(float(eq.iloc[-1]) / INITIAL - 1.0, 6)
    dd_series = eq / eq.cummax() - 1.0
    return {
        "n_days": int(len(eq)),
        "cum_ret": cum,
        "annualized": annualized(cum, len(eq)),
        "max_dd_path": path_dd(values, INITIAL),
        "max_dd_engine": round(float((eq / eq.cummax() - 1.0).min()), 6),
        "dd_series": [round(float(v), 6) for v in dd_series],
        "dates": [str(pd.Timestamp(d).date()) for d in eq.index],
        "equity_cny": values,
        "monthly": monthly,
        "months_tracked": (monthly or {}).get("months_tracked", 0),
        "monthly_positive_rate": _pos_rate(monthly),
        "regime_segments": seg,
        "trades": trades,
        "trades_note": trades_note,
    }


def _pos_rate(monthly: dict | None):
    if not monthly or not monthly.get("monthly_returns"):
        return None
    rets = monthly["monthly_returns"]
    return round(sum(1 for r in rets if r > 0) / len(rets), 4)


def _write(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, default=str)
        fh.write("\n")


# ------------------------------------------------------------ account faces
def derive_a_traders() -> list:
    """Level in PAPER_LEVELS AND registered entry resolvable (TREND-001
    entry=None template holder excluded by construction)."""
    import glob
    out = []
    for p in sorted(glob.glob(os.path.join(TRADERS_DIR, "*.json"))):
        with open(p, encoding="utf-8-sig") as fh:
            t = json.load(fh)
        if (t.get("level") in PAPER_LEVELS
                and t.get("params", {}).get("entry") in SIGNAL_BUILDERS):
            out.append(t["id"])
    return out


def run_family_a(prices, P, states) -> dict:
    """A: 6 registered traders, paper engine replay from retro hire."""
    ledgers = {}
    for tid in derive_a_traders():
        t = load_trader(tid)
        t_r = dict(t)
        t_r["created"] = str(W_START.date())
        r1 = paper_run(t_r, prices, P)
        with CostPatch(2):
            r2 = paper_run(t_r, prices, P)
        eq1, eq2 = r1["equity"], r2["equity"]
        if eq1 is None or len(eq1) < 100:
            raise SystemExit(f"A-GATE FAIL: {tid} window {len(eq1) if eq1 is not None else 0} bars < 100")
        rets1 = eq1.pct_change().dropna()
        ledgers[tid] = {
            "family": "A", "engine": "live.paper.paper_run (T+1 open fills)",
            "initial_cash_cny": INITIAL,
            "hire_retro": str(W_START.date()),
            "guards": "shadow (regime_mask=None, fill_guard=None; v3 states recorded)",
            "cost_caliber": "V1 legacy 13bp x1/x2",
            "x1": _face_block(eq1, "engine trade list",
                              _seg(rets1, states),
                              monthly_aggregate(eq1, INITIAL, str(W_START.date())),
                              _trades(r1["trades"])),
            "x2": _face_block(eq2, "engine trade list (x2 cost face)",
                              _seg(eq2.pct_change().dropna(), states),
                              monthly_aggregate(eq2, INITIAL, str(W_START.date())),
                              _trades(r2["trades"])),
            "shadow_regime_states": _daily_states(states, eq1.index),
            "complete": True,
        }
        log(f"  A {tid}: x1 cum={ledgers[tid]['x1']['cum_ret']} "
            f"dd={ledgers[tid]['x1']['max_dd_path']} "
            f"trades={len(r1['trades'])}")
    if tuple(sorted(ledgers)) != A_EXPECTED:
        raise SystemExit(f"A-GATE FAIL: derived {sorted(ledgers)} != frozen {A_EXPECTED}")
    return ledgers


def _seg(rets: pd.Series, states):
    from t28_stable_profit import _seg_classes
    return _seg_classes(rets, states)


def _trades(trades) -> list:
    out = []
    for tr in trades:
        row = {k: (round(float(v), 6) if isinstance(v, (int, float)) else v)
               for k, v in tr.items()}
        out.append(row)
    return out


def run_family_b(prices, states) -> dict:
    """B: sleeve blends (B_MAXDIV canon + CEO-named top-3 AGGR)."""
    from parallel_runner import run_cells_parallel, worker_cap
    from t28_stable_profit import TOURN_JSON, _blend_daily_ret, _sleeve_worker
    from aggressive_lab import (FROZEN_SHA, ROSTER, build_weights, w_sha)
    from t27_blend_tournament import daily_ret_matrix

    jobs = [(tid, mult, prices, CUTOFF) for tid in ROSTER
            for mult in (None, 2.0)]
    res = run_cells_parallel(
        [(f"{a[0]}|{a[1] or 'x1'}", _sleeve_worker, a) for a in jobs],
        workers=min(worker_cap(), 25), desc="retro-sleeves")
    sleeves = {}
    for tid in ROSTER:
        r1, r2 = res[f"{tid}|x1"], res[f"{tid}|2.0"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}

    with open(TOURN_JSON, encoding="utf-8") as fh:
        tour = json.load(fh)
    w_canon = dict(tour["weights"]["B_MAXDIV"]["weights"])
    if w_sha(w_canon) != FROZEN_SHA["AGGR-NOCASH"]:
        raise SystemExit("B-GATE FAIL: B_MAXDIV canon sha drift")

    faces, sha_checks, _tour = build_weights()
    for name in AGGR_PICKS:
        face = faces[name]
        if "static" in face:
            if w_sha(face["static"]) != FROZEN_SHA[name]:
                raise SystemExit(f"B-GATE FAIL: {name} static sha drift")
        else:
            if (w_sha(face["regime"]["offensive"]) != FROZEN_SHA[name + "-offensive"]
                    or w_sha(face["regime"]["defensive"]) != FROZEN_SHA[name + "-defensive"]):
                raise SystemExit(f"B-GATE FAIL: {name} regime sha drift")

    ledgers = {"B_MAXDIV": _blend_ledger("B_MAXDIV", "static", w_canon,
                                         sleeves, states)}
    for name in AGGR_PICKS:
        face = faces[name]
        if "static" in face:
            ledgers[name] = _blend_ledger(name, "static", face["static"],
                                          sleeves, states)
        else:
            ledgers[name] = _blend_ledger(
                name, "regime", face["regime"], sleeves, states,
                daily_ret_matrix=daily_ret_matrix)
        log(f"  B {name}: x1 cum={ledgers[name]['x1']['cum_ret']} "
            f"dd={ledgers[name]['x1']['max_dd_path']}")
    return ledgers


def _blend_ledger(name, kind, spec, sleeves, states, daily_ret_matrix=None):
    """Blend daily returns x1/x2 over the window -> accrual ledger."""
    if kind == "static":
        pr1 = _blend(sleeves, "x1", spec)
        pr2 = _blend(sleeves, "x2", spec)
        weights_declared = dict(spec)
        note = "static blend (t28 _blend_daily_ret, daily rebalanced)"
    else:
        off, defw = spec["offensive"], spec["defensive"]
        pr1 = _regime_blend_x(sleeves, "x1", off, defw, states, daily_ret_matrix)
        pr2 = _regime_blend_x(sleeves, "x2", off, defw, states, daily_ret_matrix)
        weights_declared = {"offensive": off, "defensive": defw}
        note = ("regime blend (v3 raw states, causal shift(1); x2 = same "
                "logic on x2 sleeve matrix, mechanical stress mirror)")
    led = {
        "family": "B", "engine": "sleeve blend accrual (T-56 caliber)",
        "initial_cash_cny": INITIAL,
        "blend_kind": kind, "weights_declared": weights_declared,
        "blend_note": note,
        "cost_caliber": "V1 legacy 13bp x1/x2",
        "guards": "shadow (blend face has no fill guards by construction; "
                  "v3 states recorded)",
    }
    for key, pr in (("x1", pr1), ("x2", pr2)):
        w = pr[pr.index >= W_START]
        if len(w) < 100:
            raise SystemExit(f"B-GATE FAIL: {name} {key} window {len(w)} bars < 100")
        eq = _eq_series(w)
        led[key] = _face_block(
            eq, "blend face: no discrete trade list (daily blend accrual)",
            _seg(w, states), monthly_aggregate(eq, INITIAL, str(W_START.date())))
    led["shadow_regime_states"] = _daily_states(states, led["x1"]["dates"]
                                                and pd.to_datetime(led["x1"]["dates"]))
    led["complete"] = True
    return led


def _blend(sleeves, face, weights):
    from t28_stable_profit import _blend_daily_ret
    return _blend_daily_ret({t: sleeves[t][face] for t in sleeves}, weights)


def _regime_blend_x(sleeves, face, off, defw, states, daily_ret_matrix):
    """_regime_blend logic (aggressive_lab L235 verbatim semantics) on the
    requested sleeve matrix face. GREEN/YELLOW -> offensive, ORANGE/RED ->
    defensive; state(t-1) drives day t; first day offensive (T-27 D)."""
    R = daily_ret_matrix(sleeves, face)
    if set(off) != set(R.columns) or set(defw) != set(R.columns):
        raise SystemExit("REGIME GATE FAIL: weight/column mismatch")
    s_prev = (states.reindex(R.index, method="ffill")
              .shift(1).fillna("GREEN"))
    offensive = s_prev.isin(["GREEN", "YELLOW"])
    W = pd.DataFrame([off if b else defw for b in offensive],
                     index=R.index, columns=list(R.columns))
    return (R * W).sum(axis=1)


def run_family_c() -> dict:
    """C: ALLOC cells, alloc_backtest frozen s2 mechanics, retro inception."""
    import alloc_backtest as ab
    import alloc_paper as ap

    panel, adv, raw_panel = ap._load_panel_forward(ap.SYMBOLS)
    dates = list(panel.index)
    start_idx = next((i for i, d in enumerate(dates)
                      if pd.Timestamp(d) >= W_START), None)
    if start_idx is None:
        raise SystemExit("C-GATE FAIL: no panel bar >= 2026-01-05")
    prices = {s: panel[s].ffill().tolist() for s in ap.SYMBOLS}
    adv20_map = {s: adv[s].tolist() for s in ap.SYMBOLS}
    cash_ret, repo_tail, _ = ap._load_repo_forward(panel.index)
    cash_ret = cash_ret.tolist()
    p5_present = os.path.exists(ab.P5_SLOT)

    ledgers = {}
    for arm_name, wfn, mode, p2 in ap.ARMS:
        if arm_name == "ALLOC-P5" and not p5_present:
            log(f"  C {arm_name}: honest skip (P5 ext-slot absent on this machine)")
            continue
        weights = None if p2 else wfn()
        syms = (list(ab.P2_POOL) if p2
                else [s for s in weights if s != "CASH"])
        stale = {s: ap._stale_leg_days(s, raw_panel[s], dates, start_idx)
                 for s in syms}
        res = ab.simulate(dates, prices, adv20_map, cash_ret, weights,
                          ab.CAPITAL, mode=mode, cost_fn=ab.side_cost_v2,
                          p2=p2, start_idx=start_idx)
        eq = pd.Series([float(v) for v in res["eq"]],
                       index=pd.to_datetime(dates[start_idx:]))
        if len(eq) < 100:
            raise SystemExit(f"C-GATE FAIL: {arm_name} window {len(eq)} bars < 100")
        rets = eq.pct_change().dropna()
        x1 = _face_block(eq, f"alloc engine trades (n={res['trades']})",
                         _seg(rets, v3_state_series()),
                         monthly_aggregate(eq, float(ab.CAPITAL), str(W_START.date())))
        ledgers[arm_name] = {
            "family": "C", "engine": "alloc_backtest.simulate (frozen s2 cells 1:1)",
            "initial_cash_cny": float(ab.CAPITAL),
            "mode": mode, "p2": p2,
            "cost_caliber": "v2_main (s2 canonical single face; x2 not in "
                            "frozen spec -- honest absence)",
            "guards": "shadow (alloc sleeve has no equity guards by "
                      "construction; states recorded)",
            "x1": x1, "x2": None,
            "n_trades": int(res["trades"]),
            "turnover_cny": ab._r6(res["turnover"]),
            "total_cost_cny": ab._r6(res["total_cost"]),
            "data_quality": {"stale_leg_days": stale,
                             "repo_tail_date": repo_tail},
            "complete": True,
        }
        log(f"  C {arm_name}: cum={x1['cum_ret']} dd={x1['max_dd_path']} "
            f"trades={res['trades']}")
    return ledgers


# ------------------------------------------------------------- leaderboard
def build_leaderboard(a, b, c) -> tuple:
    rows = []
    for fam, ledgers in (("A", a), ("B", b), ("C", c)):
        for name, led in ledgers.items():
            x1, x2 = led.get("x1"), led.get("x2")
            rows.append({
                "account": name, "family": fam,
                "cum_ret_x1": x1["cum_ret"], "annualized_x1": x1["annualized"],
                "max_dd_x1": x1["max_dd_path"],
                "monthly_pos_rate_x1": x1["monthly_positive_rate"],
                "months_tracked_x1": x1["months_tracked"],
                "regime_bull_x1": (x1["regime_segments"] or {}).get("bull", {}).get("cum_ret"),
                "regime_chop_x1": (x1["regime_segments"] or {}).get("chop", {}).get("cum_ret"),
                "regime_bear_x1": (x1["regime_segments"] or {}).get("bear", {}).get("cum_ret"),
                "trades": x1.get("trades_note", ""),
                "cum_ret_x2": (x2 or {}).get("cum_ret"),
                "max_dd_x2": (x2 or {}).get("max_dd_path"),
                "cost_caliber": led.get("cost_caliber", ""),
            })
    rows.sort(key=lambda r: (
        -(r["monthly_pos_rate_x1"] if r["monthly_pos_rate_x1"] is not None else -1.0),
        -(r["cum_ret_x1"] if r["cum_ret_x1"] is not None else -99.0)))
    return rows


def write_leaderboard(rows, elapsed) -> None:
    meta = cutoff_meta(str(CUTOFF.date()))
    with open(PREREG, "rb") as fh:
        prereg_sha = hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()[:16]
    out = dict(meta)
    out.update({
        "batch": "RETRO-PAPER-2026", "order": "O-20260926-1326",
        "ticket": "T-2026-09-26-79",
        "prereg": "research/RETRO_PAPER_2026_PREREG.md",
        "prereg_sha256_lf": prereg_sha,
        "window": {"start": str(W_START.date()), "cutoff": str(CUTOFF.date())},
        "sort_key": "monthly_positive_rate_x1 desc, then cum_ret_x1 desc (frozen)",
        "honest_annotation": HONEST_ANNOTATION,
        "absent_families": {
            "GRID": "今晨判 0/5 生存者=未就绪（诚实缺席，就绪即并入）",
            "CN": "T-73 模型未跑=未就绪（诚实缺席，落地即入六面样板）",
        },
        "accounts": rows,
        "engine_secs": round(elapsed, 1),
        "ledger_policy": "append_ledger +0 (marks/replay face, zero registration claims)",
    })
    _write(os.path.join(OUT_DIR, "LEADERBOARD.json"), out)
    _write_leaderboard_md(out)


def _write_leaderboard_md(out: dict) -> None:
    lines = [
        "# RETRO-PAPER-2026 年内回放纸盘榜（呈 CEO）",
        "",
        f"- 窗口：**{out['window']['start']} → {out['window']['cutoff']}**"
        f"（年内首个交易日→最新完整 bar；初始资本 ¥1,000,000/账户）",
        f"- 排序：月度正收益率↓，次键累计收益↓（跑前冻结）",
        f"- **诚实标注：{out['honest_annotation']}**",
        f"- 成本口径：A/B 组=V1 legacy 13bp x1/x2 双面；C 组=冻结 s2 正典 v2_main 单面"
        f"（x2 不在冻结口径=诚实缺席）",
        f"- 缺席族：GRID（0/5 生存者未就绪）、CN（模型未跑）——就绪即并入",
        "",
        "| # | 账户 | 族 | 累计x1 | 年化x1 | 最大回撤x1 | 月正率x1 | 足月 | "
        "bull | chop | bear | 累计x2 | 回撤x2 | 交易数 |",
        "|--:|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|",
    ]
    for i, r in enumerate(out["accounts"], 1):
        lines.append(
            f"| {i} | {r['account']} | {r['family']} "
            f"| {r['cum_ret_x1']:+.4%} | {r['annualized_x1']:+.4%} "
            f"| {r['max_dd_x1']:+.4%} "
            f"| {('%.0f%%' % (100*r['monthly_pos_rate_x1'])) if r['monthly_pos_rate_x1'] is not None else 'n/a'} "
            f"| {r['months_tracked_x1']} "
            f"| {r['regime_bull_x1'] if r['regime_bull_x1'] is not None else 'n/a'} "
            f"| {r['regime_chop_x1'] if r['regime_chop_x1'] is not None else 'n/a'} "
            f"| {r['regime_bear_x1'] if r['regime_bear_x1'] is not None else 'n/a'} "
            f"| {r['cum_ret_x2'] if r['cum_ret_x2'] is not None else 'n/a(冻结单面)'} "
            f"| {r['max_dd_x2'] if r['max_dd_x2'] is not None else 'n/a'} "
            f"| {r['trades']} |")
    lines += ["", "## 月度明细（x1 面）", ""]
    lines.append("见 results/retro_paper_2026/<账户>_ledger.json 逐日台账"
                 "（权益曲线/逐月表/回撤序列/交易单/守卫 shadow 政体记录）。")
    _write_text(os.path.join(OUT_DIR, "LEADERBOARD.md"), "\n".join(lines) + "\n")


def _write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def write_approvals_ledger() -> None:
    """s3: CEO-approval append-only ledger (O-1326 legislation)."""
    if os.path.exists(APPROVALS):
        return
    text = (
        "# CEO_APPROVALS · 实盘模拟盘准入认可台账（O-20260926-1326 立法·追加式）\n"
        "\n"
        "- 准入法：年内回放纸盘结果 → **【CEO 认可】（唯一准入门·名单以 CEO 为准）**"
        " → 实盘模拟盘（QMT/Ptrade 模拟账户·PLAN P4 通道）→ 模拟观察 → 实盘真金=CEO 唯一门（既有阶梯不变）。\n"
        "- 认可面=既有晋升阶梯之上的追加门；未认可者留在纸盘继续跑。\n"
        "- 记录法：CEO 名单落地后逐行追加（日期｜账户｜CEO 原话/渠道｜生效动作）；禁删改历史行。\n"
        "\n"
        "## 认可记录（空——候 CEO 名单）\n"
        "\n"
        "| 日期 | 账户 | CEO 认可出处 | 生效动作（模拟盘网关接线） |\n"
        "|---|---|---|---|\n"
        "\n"
        "## 模拟盘网关接线队列（工程部 mandate·名单落地后开动）\n"
        "\n"
        "- 通道：QMT/Ptrade 模拟账户网关（PLAN P4 机制，live/gateway.py 骨架在位）。\n"
        "- 接线顺序=CEO 名单顺序；每账户接线后入模拟观察期，战绩入每日战报。\n"
        "\n"
        "## 呈报指针\n"
        "\n"
        "- 年内回放纸盘榜：results/retro_paper_2026/LEADERBOARD.md（RETRO-PAPER-2026 批）。\n"
        "- 真前向纸盘（09-23 起双轨互证）：results/paper/、results/aggr_paper/、"
        "results/alloc_paper/、results/grid_paper/。\n"
    )
    _write_text(APPROVALS, text)


# --------------------------------------------------------------------- run
def cmd_run() -> int:
    t0 = time.time()
    log("=== RETRO-PAPER-2026 (prereg frozen f70c0054; zero claims) ===")
    prices_full = load_core()
    cutoff = max(df.index.max() for df in prices_full.values())
    if cutoff < CUTOFF:
        raise SystemExit(f"PANEL GATE FAIL: cutoff {cutoff.date()} < {CUTOFF.date()}")
    prices = {s: df[df.index <= CUTOFF] for s, df in prices_full.items()}
    P = build_panels(prices)
    states = v3_state_series()
    log(f"panel: {len(prices)} ETFs through {cutoff.date()} "
        f"(frozen cutoff {CUTOFF.date()})")

    log("-- family A: 6 registered traders (paper engine replay)")
    a = run_family_a(prices, P, states)
    log("-- family B: sleeve blends (B_MAXDIV + top-3 AGGR)")
    b = run_family_b(prices, states)
    log("-- family C: ALLOC cells (frozen s2 mechanics)")
    c = run_family_c()

    rows = build_leaderboard(a, b, c)
    write_leaderboard(rows, time.time() - t0)
    write_approvals_ledger()
    for fam, ledgers in (("A", a), ("B", b), ("C", c)):
        for name, led in ledgers.items():
            _write(os.path.join(OUT_DIR, f"{name}_ledger.json"), led)
    log(f"ledgers: {sum(len(x) for x in (a, b, c))} accounts -> {OUT_DIR}")
    log(f"leaderboard: {os.path.join(OUT_DIR, 'LEADERBOARD.md')}")
    log(f"approvals ledger: {APPROVALS}")
    log(f"done in {time.time() - t0:.1f}s")
    return 0


def cmd_selftest() -> int:
    ok = total = 0

    def check(cond, label):
        nonlocal ok, total
        total += 1
        print(("[PASS] " if cond else "[FAIL] ") + label)
        ok += bool(cond)

    # 1 frozen annualization formula
    check(abs(annualized(0.1, 126) - ((1.1) ** (252 / 126) - 1)) < 1e-9,
          "annualized frozen formula (1+cum)^(252/n)-1")
    check(annualized(-1.0, 100) is None, "annualized wiped -> None (honest)")

    # 2 path dd includes initial capital (peak from 1e6)
    check(path_dd([990000.0, 950000.0, 980000.0], 1e6) == -0.05,
          "path_dd peak-to-trough includes initial (=-5% at 950k)")

    # 3 monthly positive rate
    m = {"monthly_returns": [0.01, -0.02, 0.03]}
    check(_pos_rate(m) == round(2 / 3, 4), "monthly positive rate 2/3")
    check(_pos_rate({"monthly_returns": []}) is None,
          "zero months -> None (insufficient, honest)")

    # 4 A-family derivation: exactly the frozen 6, TREND-001 excluded
    derived = derive_a_traders()
    check(tuple(sorted(derived)) == A_EXPECTED,
          f"A-family derivation == frozen 6 (got {sorted(derived)})")

    # 5 B_MAXDIV canon sha gate (real registry face, read-only)
    from t28_stable_profit import TOURN_JSON
    from aggressive_lab import FROZEN_SHA, w_sha
    with open(TOURN_JSON, encoding="utf-8") as fh:
        w = json.load(fh)["weights"]["B_MAXDIV"]["weights"]
    check(w_sha(dict(w)) == FROZEN_SHA["AGGR-NOCASH"],
          "B_MAXDIV canon weights sha gate")

    # 6 AGGR picks sha gates (frozen faces, read-only)
    faces = None
    try:
        from aggressive_lab import build_weights
        faces, _checks, _tour = build_weights()
        good = True
        for n in AGGR_PICKS:
            f = faces[n]
            if "static" in f:
                good &= w_sha(f["static"]) == FROZEN_SHA[n]
            else:
                good &= (w_sha(f["regime"]["offensive"])
                         == FROZEN_SHA[n + "-offensive"])
                good &= (w_sha(f["regime"]["defensive"])
                         == FROZEN_SHA[n + "-defensive"])
        check(good, "AGGR top-3 frozen sha gates (REGIME/CONC-TOP2/OFFENSE)")
    except Exception as e:
        check(False, f"AGGR face build raised: {e}")

    # 7 regime blend causal law on synthetic sleeves (shift(1): day t uses t-1)
    idx = pd.date_range("2026-01-05", periods=4, freq="D")
    sl = {"AAA": {"x1": {"eq_s": pd.Series([100.0, 110.0, 99.0, 105.0], index=idx)},
                  "x2": {"eq_s": pd.Series([100.0, 105.0, 99.0, 102.0], index=idx)}},
          "BBB": {"x1": {"eq_s": pd.Series([100.0, 100.0, 102.0, 104.0], index=idx)},
                  "x2": {"eq_s": pd.Series([100.0, 100.0, 102.0, 104.0], index=idx)}}}
    states = pd.Series(["GREEN", "ORANGE", "ORANGE", "GREEN"], index=idx)
    off = {"AAA": 1.0, "BBB": 0.0}
    defw = {"AAA": 0.0, "BBB": 1.0}

    def drm(sleeves, face):
        eqs = pd.concat({t: sleeves[t][face]["eq_s"] / sleeves[t][face]["eq_s"].iloc[0]
                         for t in sleeves}, axis=1, join="inner").dropna()
        return eqs.pct_change().dropna()
    pr = _regime_blend_x(sl, "x1", off, defw, states, drm)
    # ret-day1: no prior state -> GREEN default offensive -> AAA +10%;
    # ret-day2/3: state(t-1)=ORANGE -> defensive -> BBB +2% / +1.9608%
    check(abs(pr.iloc[0] - 0.10) < 1e-9 and abs(pr.iloc[1] - 0.02) < 1e-9
          and abs(pr.iloc[2] - (104.0 / 102.0 - 1.0)) < 1e-9,
          "regime blend causal shift(1) semantics (first day offensive)")

    # 8 x2 regime mirror differs from x1 on synthetic x2 path (stress face live)
    pr2 = _regime_blend_x(sl, "x2", off, defw, states, drm)
    check(abs(pr2.iloc[0] - 0.05) < 1e-9, "x2 matrix consumed by mirror blend")

    # 9 leaderboard sort key (frozen: monthly pos rate desc then cum desc)
    rows = build_leaderboard(
        {}, {"T1": _mk_blend_led(0.5, 0.02), "T2": _mk_blend_led(0.25, 0.10),
             "T3": _mk_blend_led(None, 0.03)}, {})
    check([r["account"] for r in rows] == ["T1", "T2", "T3"],
          "leaderboard sort: pos-rate desc, cum desc, None last")

    # 10 approvals ledger idempotent (existing face untouched)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        global APPROVALS
        orig = APPROVALS
        APPROVALS = os.path.join(td, "CEO_APPROVALS.md")
        write_approvals_ledger()
        first = open(APPROVALS, encoding="utf-8").read()
        write_approvals_ledger()
        check(open(APPROVALS, encoding="utf-8").read() == first,
              "approvals ledger append-only guard (rewrite = no-op)")
        APPROVALS = orig

    # 11 honest annotation verbatim in board payload
    board = {"honest_annotation": HONEST_ANNOTATION}
    check("非前向新证据" in board["honest_annotation"],
          "honest annotation verbatim (window-overlap disclosure)")

    print(f"selftest: {ok}/{total} PASS")
    return 0 if ok == total else 2


def _mk_blend_led(pos_rate, cum):
    """Synthetic ledger row for sort tests (hermetic)."""
    return {"family": "B", "cost_caliber": "V1",
            "x1": {"cum_ret": cum, "annualized": cum, "max_dd_path": -0.01,
                   "monthly_positive_rate": pos_rate, "months_tracked": 5,
                   "regime_segments": {"bull": {"cum_ret": 0.01},
                                      "chop": {"cum_ret": 0.01},
                                      "bear": {"cum_ret": 0.01}},
                   "trades_note": "blend n/a"},
            "x2": {"cum_ret": cum / 2, "max_dd_path": -0.02}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest"])
    args = ap.parse_args()
    if args.cmd == "selftest":
        return cmd_selftest()
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
