"""The re-buy's cash sleeve lost 902.58 CNY in 9 sessions -- what would the repo market have paid?

r1984 (`scripts/regime_cap_breach_pnl.py`) priced the re-buy leg by leg: 1.2261 m CNY of the
1.4635 m bought back on 2026-11-10 was government-bond ETFs (quasi-cash), and those legs were
worth 902.58 CNY LESS by 2026-11-20, while the single equity leg (512800) made 6,063 CNY. It
also left one item explicitly unmeasured: the quasi-cash legs' -0.0736 % was never compared
with what the repo market paid over the same days, because that face does not read the repo
panel.

This face closes that item and nothing else. It answers one question:

    the same 1.2261 m CNY, rolled through the repo market from the re-buy session to the mark
    session under the exchange's own fee schedule, would have been worth how much?

Why it matters: the 20 % cap's own wording is "现金/逆回购 >= 80 %". So the rule does not only
cap the level, it names the vehicle -- repo for the cash, not a bond ETF that marks to market.
Whether the breach is only a level violation or also a vehicle violation is a question with a
number on it, and the number belongs on the reader's page next to the level.

Rules this face keeps (each has a selftest leg):

  * the re-buy legs and their amounts are NOT re-invented: they are read from the published
    face, then re-derived from the same daily export and gated to the fen (r1934: an input
    that moved is STALE, never a zero and never a silent overwrite);
  * the repo arithmetic is NOT re-implemented: it calls `bench_repo_ladder.run_bucket` with
    that cell's own fee schedule and its own "interest is paid on actual calendar days held,
    idle days earn nothing" convention;
  * the fee is charged once per lend by the engine, so gross and net are both printed and the
    commission in CNY is the difference -- no annualised rate is invented for a 10-day window;
  * a leg marked by a close price carries no distribution, so the comparison is
    "repo carry net of commission" against "price move only" -- the doc says so out loud;
  * no panel, no quote on the re-buy session, no published face = refuse and name the reason.

Verdicts (frozen before the first run):

  CANNOT_READ_PUBLISHED_PNL_FACE          the r1984 face is missing or unreadable
  CANNOT_READ_WINDOW                      that face carries no back_day / mark_day
  NO_QUASI_CASH_SLEEVE                    the face holds no bond legs to compare
  FACES_ARE_ONE_GENERATION_APART          the export cutoff and the face cutoff differ
  LEG_AMOUNTS_DO_NOT_REPRODUCE_THE_PUBLISHED_FACE   cross-gate failed -> STALE, no ruling
  CANNOT_PRICE_THE_REPO_ALTERNATIVE       no panel, or no quote on the re-buy session
  CASH_SLEEVE_TRAILED_THE_REPO_ROLL_BY_X_CNY        the point (X printed, per account too)
  CASH_SLEEVE_BEAT_THE_REPO_ROLL                    the quasi-cash legs paid more than repo

Reads published faces + the repo panel only. Writes its own json + md. Books nothing, changes
no rule, edits no page, and is not an instruction to sell or to buy.

Usage:
  python scripts/regime_cap_breach_cash_vs_repo.py run
  python scripts/regime_cap_breach_cash_vs_repo.py check
  python scripts/regime_cap_breach_cash_vs_repo.py --selftest
"""

import copy
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bench_repo_ladder as BRL                                     # noqa: E402  (fee table + engine)
from bench_core import RESULTS, RESEARCH                            # noqa: E402

SCHEMA = "regime-cap-breach-cash-vs-repo/v1"
ARTIFACT = "results/regime_cap_breach_cash_vs_repo.json"
DOC = "research/REGIME-CAP-BREACH-CASH-VS-REPO.md"

OUT = os.path.join(RESULTS, "regime_cap_breach_cash_vs_repo.json")
DOC_PATH = os.path.join(RESEARCH, "REGIME-CAP-BREACH-CASH-VS-REPO.md")
PNL_FACE = os.path.join(RESULTS, "regime_cap_breach_pnl.json")
EXPORTS = os.path.join(RESULTS, "paper_export")
REPO_DIR = os.path.join(_ROOT, "data", "repo_daily")
BENCH_FACE = os.path.join(RESULTS, "bench_repo_ladder.json")

MONEY_TOL = 0.01          # one fen: the published faces print cents
RATE_TOL = 1e-9

# One-day roll is the tenor whose money is always available on the next session -- the
# comparison a cash sleeve should be held to. Seven days is printed beside it because the
# published bench cell's question is exactly "does lending longer pay", and this window can
# speak to that too.
BENCHMARKS = ((1, "GC001"), (7, "GC007"))


# --------------------------------------------------------------------------- inputs

def _rel(path):
    """A readable label even when the path sits on another drive (temp dirs)."""
    try:
        return _rel(path)
    except ValueError:
        return path


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _read_or(path, problem):
    """Return (payload, problem). Missing and unreadable are kept apart."""
    if not os.path.isfile(path):
        return None, "%s: missing %s" % (problem, _rel(path))
    try:
        return _load(path), None
    except Exception as exc:                                        # noqa: BLE001
        return None, "%s: unreadable %s (%s)" % (problem, _rel(path), exc)


def load_panels(tenors=None, repo_dir=None):
    """Close-quote series per tenor, or None for a tenor whose csv is not on disk."""
    tenors = BENCHMARKS if tenors is None else tenors
    repo_dir = repo_dir or REPO_DIR
    out = {}
    for tenor_days, code in tenors:
        path = os.path.join(repo_dir, code + ".csv")
        if not os.path.isfile(path):
            out[code] = None
            continue
        try:
            out[code] = BRL._read(code) if repo_dir == REPO_DIR else _read_csv(path)
        except Exception:                                            # noqa: BLE001
            out[code] = None
    return out


def _read_csv(path):
    """Same shape as bench_repo_ladder._read, for a panel pointed at elsewhere."""
    import pandas as pd
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.dropna(subset=["close"]).sort_values("date")
    close = df.set_index("date")["close"].astype(float)
    vol = pd.to_numeric(df.get("volume"), errors="coerce").median()
    return {"close": close, "median_volume": float(vol) if pd.notna(vol) else None}


# --------------------------------------------------------------------------- repo arithmetic

def window_calendar(close, start, end):
    """Trading days the panel actually carries inside [start, end], inclusive."""
    return [d for d in list(close.index) if start <= d <= end]


def roll(close, tenor_days, calendar, fee=None):
    """Net and gross multipliers for one tenor over the window, plus the engine's log."""
    if not calendar:
        return None
    net_eq, log = BRL.run_bucket(close, tenor_days, calendar, fee=fee)
    gross_eq, _ = BRL.run_bucket(close, tenor_days, calendar, fee=0.0)
    return {
        "net_mult": float(net_eq.iloc[-1]),
        "gross_mult": float(gross_eq.iloc[-1]),
        "net_pct": round(100.0 * (float(net_eq.iloc[-1]) - 1.0), 6),
        "gross_pct": round(100.0 * (float(gross_eq.iloc[-1]) - 1.0), 6),
        "fee_fraction_per_lend": (None if fee is None else float(fee)),
        "engine_log": dict(log),
    }


# --------------------------------------------------------------------------- measurement

def _pnl_accounts(face):
    acc = face.get("accounts") or {}
    return acc if isinstance(acc, dict) else {}


def build(pnl_face=None, exports_dir=None, panels=None, back_day=None, mark_day=None):
    """Pure build. Returns (payload, rc). Never writes the published face."""
    payload = {
        "face": "regime_cap_breach_cash_vs_repo",
        "schema": SCHEMA,
        "generated": None,
        "evidence_cutoff": None,
        "window": {},
        "benchmarks": {},
        "accounts": {},
        "totals": {},
        "rule_cash_floor": {},
        "bench_context": {},
        "verdict": None,
        "gates": {},
        "not_measured": [],
        "basis": ("repo side = carry net of the exchange fee per lend, interest on actual "
                  "calendar days held, idle days earn nothing; ETF side = close-price move "
                  "only (a marked close carries no distribution), so the comparison is not "
                  "a long-run carry verdict"),
    }

    if pnl_face is None:
        pnl_face, problem = _read_or(PNL_FACE, "CANNOT_READ_PUBLISHED_PNL_FACE")
        if problem:
            payload["verdict"] = problem
            payload["gates"]["pnl_face"] = "unreadable"
            return payload, 2
    payload["gates"]["pnl_face"] = "ok"

    back_day = back_day or pnl_face.get("back_day")
    mark_day = mark_day or pnl_face.get("mark_day")
    if not back_day or not mark_day:
        payload["verdict"] = "CANNOT_READ_WINDOW: published face carries no back_day/mark_day"
        payload["gates"]["window"] = "missing"
        return payload, 2

    import pandas as pd
    back_ts = pd.Timestamp(back_day)
    mark_ts = pd.Timestamp(mark_day)
    if mark_ts < back_ts:
        payload["verdict"] = ("CANNOT_READ_WINDOW: mark_day %s is before back_day %s"
                              % (mark_day, back_day))
        payload["gates"]["window"] = "reversed"
        return payload, 2

    payload["window"] = {"back_day": back_day, "mark_day": mark_day,
                         "calendar_days": int((mark_ts - back_ts).days)}
    payload["evidence_cutoff"] = pnl_face.get("evidence_cutoff")

    # ---- the leg amounts, re-derived from the same export the published face used
    exports_dir = exports_dir or EXPORTS
    export_path = os.path.join(exports_dir, "export-%s.json" % back_day)
    export, problem = _read_or(export_path, "CANNOT_READ_BACK_EXPORT")
    payload["gates"]["back_export"] = "unreadable" if problem else "ok"
    mark_export, problem2 = _read_or(os.path.join(exports_dir, "export-%s.json" % mark_day),
                                     "CANNOT_READ_MARK_EXPORT")
    payload["gates"]["mark_export"] = "unreadable" if problem2 else "ok"
    if problem:
        payload["verdict"] = problem
        return payload, 2

    held = {}
    for trader in export.get("traders", []):
        held[trader.get("trader")] = {
            str(p.get("symbol")): p for p in trader.get("open_positions", [])
        }
    equity_now = {}
    for trader in (mark_export or {}).get("traders", []):
        cap = trader.get("capital_cny") or {}
        if cap.get("equity") is not None:
            equity_now[trader.get("trader")] = float(cap["equity"])

    accounts = _pnl_accounts(pnl_face)
    if not accounts:
        payload["verdict"] = "CANNOT_READ_PUBLISHED_PNL_FACE: no accounts block"
        return payload, 2

    bond_invested = 0.0
    gate_rows = {}
    for name, rec in accounts.items():
        mine = 0.0
        for sym in (rec.get("bond") or {}).get("legs") or {}:
            lot = held.get(name, {}).get(str(sym))
            if lot is None:
                continue                     # exited/absent: named below, never counted as 0
            mine += float(lot.get("quantity") or 0.0) * float(lot.get("cost_price") or 0.0)
        theirs = float(((rec.get("bond") or {}).get("invested")) or 0.0)
        gate_rows[name] = {"rederived_cny": round(mine, 2), "published_cny": round(theirs, 2),
                           "delta_cny": round(mine - theirs, 2)}
        bond_invested += theirs

    bad_gate = {k: v for k, v in gate_rows.items() if abs(v["delta_cny"]) > MONEY_TOL}
    payload["gates"]["cross_gate_leg_amounts"] = {
        "rows": gate_rows, "tolerance_cny": MONEY_TOL,
        "state": "STALE" if bad_gate else "ok",
    }

    face_cutoff = pnl_face.get("evidence_cutoff")
    export_cutoff = (mark_export or {}).get("evidence_cutoff")
    apart = bool(face_cutoff and export_cutoff and face_cutoff != export_cutoff)
    payload["gates"]["generation"] = {
        "published_face_cutoff": face_cutoff, "mark_export_cutoff": export_cutoff,
        "state": "one generation apart" if apart else "ok",
    }

    if bond_invested <= 0:
        payload["verdict"] = "NO_QUASI_CASH_SLEEVE: the published face holds no bond legs"
        return payload, 2
    if bad_gate:
        payload["verdict"] = ("LEG_AMOUNTS_DO_NOT_REPRODUCE_THE_PUBLISHED_FACE: %s -- "
                              "STALE, no ruling printed" % json.dumps(bad_gate, ensure_ascii=False))
        return payload, 3
    if apart:
        payload["verdict"] = ("FACES_ARE_ONE_GENERATION_APART: face cutoff %s vs export cutoff "
                              "%s -- no ruling printed" % (face_cutoff, export_cutoff))
        return payload, 3

    # ---- the repo alternative
    panels = load_panels() if panels is None else panels
    unpriced = []
    for tenor_days, code in BENCHMARKS:
        panel = panels.get(code)
        if not panel:
            unpriced.append("%s: panel missing" % code)
            continue
        cal = window_calendar(panel["close"], back_ts, mark_ts)
        if not cal:
            unpriced.append("%s: panel carries no session inside the window" % code)
            continue
        q = panel["close"].get(back_ts)
        if q is None:
            unpriced.append("%s: no quote on the re-buy session %s" % (code, back_day))
            continue
        payload["benchmarks"][code] = {
            "tenor_days": tenor_days,
            "sessions_in_window": [str(d.date()) for d in cal],
            "quote_on_back_day_pct": float(q),
            "quote_on_mark_day_pct": (None if panel["close"].get(mark_ts) is None
                                      else float(panel["close"].get(mark_ts))),
        }
        payload["benchmarks"][code].update(roll(panel["close"], tenor_days, cal))

    priced = [c for c, r in payload["benchmarks"].items() if r.get("net_mult") is not None]
    if not priced:
        payload["verdict"] = ("CANNOT_PRICE_THE_REPO_ALTERNATIVE: " + "; ".join(unpriced or
                                                                              ["no tenor priced"]))
        payload["gates"]["repo_panel"] = "unusable"
        return payload, 2
    payload["gates"]["repo_panel"] = "ok" if not unpriced else "partial"
    payload["not_measured"].extend(unpriced)

    primary = BENCHMARKS[0][1]
    if primary not in priced:
        primary = priced[0]

    # ---- per account
    tot = {"actual_pnl": 0.0, "invested": 0.0}
    for code in priced:
        tot["repo_net_%s" % code] = 0.0
        tot["repo_gross_%s" % code] = 0.0
        tot["commission_%s" % code] = 0.0
    for name, rec in accounts.items():
        bond = rec.get("bond") or {}
        invested = float(bond.get("invested") or 0.0)
        actual = float(bond.get("pnl") or 0.0)
        row = {"invested_cny": round(invested, 2), "actual_pnl_cny": round(actual, 2),
               "actual_ret_pct": (round(100.0 * actual / invested, 4) if invested else None),
               "equity_cny": (None if equity_now.get(name) is None
                              else round(equity_now[name], 2)),
               "legs": {sym: {"invested_cny": round(float(lot.get("quantity") or 0.0)
                                                    * float(lot.get("cost_price") or 0.0), 2),
                              "ret_pct": lot.get("ret_pct")}
                        for sym, lot in (bond.get("legs") or {}).items()},
               "repo": {}}
        for code in priced:
            b = payload["benchmarks"][code]
            net = invested * b["net_mult"]
            gross = invested * b["gross_mult"]
            row["repo"][code] = {
                "net_value_cny": round(net, 2),
                "gross_value_cny": round(gross, 2),
                "net_pnl_cny": round(net - invested, 2),
                "gross_pnl_cny": round(gross - invested, 2),
                "commission_cny": round(gross - net, 2),
                "gap_vs_actual_cny": round((net - invested) - actual, 2),
            }
            tot["repo_net_%s" % code] += net - invested
            tot["repo_gross_%s" % code] += gross - invested
            tot["commission_%s" % code] += gross - net
        tot["actual_pnl"] += actual
        tot["invested"] += invested
        payload["accounts"][name] = row

    payload["totals"] = {
        "invested_cny": round(tot["invested"], 2),
        "actual_pnl_cny": round(tot["actual_pnl"], 2),
        "actual_ret_pct": (round(100.0 * tot["actual_pnl"] / tot["invested"], 4)
                           if tot["invested"] else None),
        "primary_benchmark": primary,
    }
    for code in priced:
        payload["totals"]["repo_net_%s_cny" % code] = round(tot["repo_net_%s" % code], 2)
        payload["totals"]["repo_gross_%s_cny" % code] = round(tot["repo_gross_%s" % code], 2)
        payload["totals"]["commission_%s_cny" % code] = round(tot["commission_%s" % code], 2)
        payload["totals"]["gap_vs_actual_%s_cny" % code] = round(
            tot["repo_net_%s" % code] - tot["actual_pnl"], 2)

    # ---- the floor the rule's own wording guarantees (pure arithmetic at today's quote)
    three = [n for n in accounts if equity_now.get(n)]
    cash_equity = sum(equity_now[n] for n in three) if three else 0.0
    mark_rate = payload["benchmarks"][primary].get("quote_on_mark_day_pct")
    days = payload["window"]["calendar_days"]
    floor = {}
    if cash_equity and mark_rate is not None and days:
        cash_required = cash_equity * (1.0 - 0.20)          # the rule's own >=80% cash wording
        gross = cash_required * (float(mark_rate) / 100.0) * days / 365.0
        b = payload["benchmarks"][primary]
        fee_ratio = (1.0 - (b["net_mult"] - 1.0) / (b["gross_mult"] - 1.0)
                     if b["gross_mult"] > 1.0 else None)
        floor = {
            "accounts_measured": sorted(three),
            "equity_cny": round(cash_equity, 2),
            "cap": 0.20,
            "cash_the_rule_wants_cny": round(cash_required, 2),
            "quote_pct": float(mark_rate),
            "window_days": days,
            "gross_income_over_window_cny": round(gross, 2),
            "fee_share_of_gross_measured_in_this_window": (None if fee_ratio is None
                                                           else round(fee_ratio, 4)),
            "note": ("pure arithmetic at the mark-day quote and this window's measured fee "
                     "share; not a forecast and not a claim about the equity sleeve"),
        }
    payload["rule_cash_floor"] = floor

    bench, problem = _read_or(BENCH_FACE, "bench_face")
    if bench:
        payload["bench_context"] = {"headline": bench.get("headline"),
                                    "cell_cutoff": bench.get("ts"),
                                    "note": ("the published cell asks whether lending longer "
                                             "pays over 2015-2026; this window is one sample "
                                             "and is not re-judged here")}
    else:
        payload["not_measured"].append(problem)

    gap = payload["totals"]["gap_vs_actual_%s_cny" % primary]
    if gap > MONEY_TOL:
        payload["verdict"] = "CASH_SLEEVE_TRAILED_THE_REPO_ROLL_BY_%s_CNY" % (
            ("%.2f" % gap).replace(".", "_"))
    elif gap < -MONEY_TOL:
        payload["verdict"] = "CASH_SLEEVE_BEAT_THE_REPO_ROLL"
    else:
        payload["verdict"] = "CASH_SLEEVE_AND_THE_REPO_ROLL_ARE_THE_SAME_TO_THE_FEN"
    return payload, 0


# --------------------------------------------------------------------------- check

def check(payload):
    """Re-derive from the faces on disk and compare the ruling's own numbers."""
    problems = []
    fresh, rc = build()
    if rc not in (0, 3):
        return 3, ["rebuild failed rc=%s verdict=%r" % (rc, fresh.get("verdict"))]
    for key in ("verdict", "totals", "window"):
        if payload.get(key) != fresh.get(key):
            problems.append("%s differs: face=%r disk=%r"
                            % (key, payload.get(key), fresh.get(key)))
    for code in fresh.get("benchmarks", {}):
        a = (payload.get("benchmarks", {}).get(code) or {}).get("net_mult")
        b = fresh["benchmarks"][code].get("net_mult")
        if a is None or b is None or abs(a - b) > RATE_TOL:
            problems.append("%s net_mult differs: face=%r disk=%r" % (code, a, b))
    for name, row in (fresh.get("accounts") or {}).items():
        mine = (payload.get("accounts") or {}).get(name) or {}
        for code, r in row.get("repo", {}).items():
            theirs = (mine.get("repo", {}).get(code) or {}).get("gap_vs_actual_cny")
            if theirs is None or abs(theirs - r["gap_vs_actual_cny"]) > MONEY_TOL:
                problems.append("%s/%s gap differs: face=%r disk=%r"
                                % (name, code, theirs, r["gap_vs_actual_cny"]))
    if not problems and not os.path.isfile(DOC_PATH):
        problems.append("doc missing: %s" % _rel(DOC_PATH))
    return (0 if not problems else 3), problems


# --------------------------------------------------------------------------- doc

def write_doc(payload):
    w = payload["window"]
    t = payload["totals"]
    primary = t.get("primary_benchmark")
    prim = payload["benchmarks"].get(primary, {})
    lines = []
    lines.append("# 破帽回补的准现金腿 vs 滚逆回购\n")
    lines.append("生成 %s ｜ 窗口 %s → %s（%s 个日历日）｜ 判词 `%s`\n"
                 % (payload.get("generated") or "-", w.get("back_day"), w.get("mark_day"),
                    w.get("calendar_days"), payload.get("verdict")))
    lines.append("## 一句话\n")
    gap = t.get("gap_vs_actual_%s_cny" % primary)
    lines.append("回补的 **%s 元**准现金腿在这 %s 个日历日里记 **%s 元（%s%%）**；同一笔钱按交易所"
                 "费率滚 **%s** 净得 **%s 元**（毛 %s 元、手续费 %s 元）——两者差 **%s 元**。\n"
                 % (f"{t.get('invested_cny'):,.2f}", w.get("calendar_days"),
                    f"{t.get('actual_pnl_cny'):,.2f}", t.get("actual_ret_pct"),
                    primary, f"{t.get('repo_net_%s_cny' % primary):,.2f}",
                    f"{t.get('repo_gross_%s_cny' % primary):,.2f}",
                    f"{t.get('commission_%s_cny' % primary):,.2f}",
                    f"{gap:,.2f}"))
    lines.append("这不是「持有国债 ETF 长期跑不过回购」的结论：ETF 侧读的是收盘价变动"
                 "（分红不进 mark），回购侧是实打实的利息减手续费，10 天窗口里主导的是利率"
                 "波动而不是 carry。它回答的只是「同 10 天、同费率下这两条腿各留了多少钱」。\n")
    lines.append("## 逐账户\n")
    head = "| 账户 | 准现金腿投入 | 实际标记盈亏 | 实际%% | %s 净 | 手续费 | 差 |"
    lines.append(head % primary)
    lines.append("|---|---|---|---|---|---|---|")
    for name, row in sorted(payload["accounts"].items()):
        r = row["repo"].get(primary) or {}
        lines.append("| %s | %s | %s | %s | %s | %s | %s |"
                     % (name, f"{row['invested_cny']:,.2f}", f"{row['actual_pnl_cny']:,.2f}",
                        row.get("actual_ret_pct"), f"{r.get('net_pnl_cny', 0):,.2f}",
                        f"{r.get('commission_cny', 0):,.2f}",
                        f"{r.get('gap_vs_actual_cny', 0):,.2f}"))
    lines.append("")
    lines.append("## 两个期限并列（同一窗口）\n")
    lines.append("| 期限 | 净 % | 毛 % | 手续费元 | 出借次数 | 闲置日历日 | 利用率 |")
    lines.append("|---|---|---|---|---|---|---|")
    for code, b in payload["benchmarks"].items():
        log = b.get("engine_log") or {}
        if b.get("net_mult") is None:
            continue
        lines.append("| %s | %s | %s | %s | %s | %s | %s |"
                     % (code, b.get("net_pct"), b.get("gross_pct"),
                        f"{t.get('commission_%s_cny' % code, 0):,.2f}",
                        log.get("lends"), log.get("idle_days"), log.get("utilisation")))
    lines.append("")
    lines.append("## 规则自己要求的现金腿（纯算术，不是预测）\n")
    fl = payload.get("rule_cash_floor") or {}
    if fl:
        lines.append("三户权益合计 %s 元；规则原文要求现金/逆回购 ≥80%%，即 **%s 元**；按标记日 "
                     "%s 收盘 %s%% 与本周期的实测手续费占比，这 %s 个日历日毛收入约 **%s 元**。"
                     "（手续费占毛利息约 %s%%。）\n"
                     % (f"{fl['equity_cny']:,.2f}", f"{fl['cash_the_rule_wants_cny']:,.2f}",
                        primary, fl["quote_pct"], fl["window_days"],
                        f"{fl['gross_income_over_window_cny']:,.2f}",
                        (None if fl.get("fee_share_of_gross_measured_in_this_window") is None
                         else round(100 * fl["fee_share_of_gross_measured_in_this_window"], 1))))
    else:
        lines.append("*无法报价（缺面板或标记日无报价），不印数字。*\n")
    lines.append("## 与相邻面的分工（防重复）\n")
    lines.append("- `regime_cap_measure_sizes`：帽子的两种写法差多少钱（1,077,407 元）；")
    lines.append("- `regime_cap_breach_timeline`：这顶帽子被遵守过几次、被买回几次；")
    lines.append("- `regime_cap_breach_pnl`：这笔回补本身挣没挣（权益腿 +6,063 / 准现金腿 -902.58）；")
    lines.append("- `regime_cap_compliance_cost`：今天照做要花多少（13bp 摩擦与损失规避）；")
    lines.append("- **本面**：准现金腿 vs 同窗口滚逆回购——规则点名的是「现金/逆回购」，"
                 "本面把这个车种差换成钱。\n")
    lines.append("## 口径与未验证（如实）\n")
    lines.append("- 回购侧：调 `bench_repo_ladder.run_bucket`，利息按实际占款日历日计、手续费按笔；"
                 "窗口内最后一笔若跨过标记日则不计入（本窗口实际未发生，利用率已印）。")
    lines.append("- ETF 侧：`last_close` 是收盘价，分红/付息不进 mark；10 天窗口的差里含利率波动。")
    lines.append("- 未年化：9 个交易日的读数不外推成年化差。")
    for item in payload.get("not_measured") or []:
        lines.append("- %s" % item)
    lines.append("")
    lines.append("*本面只读已发布面与回购面板；不记账、不改规则、不改页面，也不构成买卖指令。*")
    os.makedirs(os.path.dirname(DOC_PATH), exist_ok=True)
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# --------------------------------------------------------------------------- run

def run(write=True):
    import datetime
    payload, rc = build()
    if write and rc in (0, 3):
        payload["generated"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        write_doc(payload)
    print(json.dumps({"verdict": payload.get("verdict"), "rc": rc,
                      "totals": payload.get("totals")}, ensure_ascii=False))
    return rc


# --------------------------------------------------------------------------- selftest

def _selftest():
    ok = total = 0

    def leg(cond, msg):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL: " + msg)

    live, rc = build()
    leg(rc == 0, "live build must succeed, rc=%s verdict=%r" % (rc, live.get("verdict")))
    leg(str(live.get("verdict") or "").startswith(("CASH_SLEEVE_", "LEG_AMOUNTS_",
                                                   "FACES_ARE_")),
        "live verdict must be a ruling or an honest refusal, got %r" % live.get("verdict"))
    leg((live.get("gates", {}).get("cross_gate_leg_amounts", {}).get("state")) == "ok",
        "live leg-amount cross-gate must be ok, got %r"
        % (live.get("gates", {}).get("cross_gate_leg_amounts"),))
    prim = (live.get("totals") or {}).get("primary_benchmark")
    b = (live.get("benchmarks") or {}).get(prim) or {}
    leg(b.get("net_mult") is not None and b.get("gross_mult") is not None,
        "primary benchmark must price both net and gross")
    leg(b.get("net_mult", 1) < b.get("gross_mult", 1),
        "a fee-bearing roll must net less than gross (net=%r gross=%r)"
        % (b.get("net_mult"), b.get("gross_mult")))
    comm = (live.get("totals") or {}).get("commission_%s_cny" % prim)
    leg(comm is not None and comm > 0, "commission must be a positive CNY amount, got %r" % comm)
    leg(abs((live.get("totals") or {}).get("actual_pnl_cny", 0)
            - float(sum((a.get("bond") or {}).get("pnl") or 0.0
                        for a in _pnl_accounts(_load(PNL_FACE)).values()))) <= MONEY_TOL,
        "actual P&L must reproduce the published face to the fen")
    leg(((live.get("rule_cash_floor") or {}).get("cash_the_rule_wants_cny") or 0) > 0,
        "the rule's own 80% cash line must be printed when quotes exist")

    with tempfile.TemporaryDirectory() as td:
        # missing published face -> named refusal, no totals
        # (no window on a face -> refusal, driven through an injected face)
        p_missing, rc_missing = build(pnl_face={"accounts": {}}, exports_dir=td, panels={})
        leg(rc_missing == 2 and str(p_missing["verdict"]).startswith("CANNOT_READ_WINDOW"),
            "a face with no window must refuse, got %r" % p_missing.get("verdict"))

        # no quasi-cash sleeve
        p_zero, rc_zero = build(pnl_face={"back_day": "2026-11-10", "mark_day": "2026-11-20",
                                          "evidence_cutoff": "2026-11-20",
                                          "accounts": {"X": {"bond": {"invested": 0.0,
                                                                      "pnl": 0.0, "legs": {}}}}},
                                exports_dir=EXPORTS, panels={})
        leg(rc_zero == 2 and str(p_zero["verdict"]).startswith("NO_QUASI_CASH_SLEEVE"),
            "zero bond sleeve must be NO_QUASI_CASH_SLEEVE, got %r" % p_zero.get("verdict"))

        # cross-gate: move one published leg amount by 1 CNY -> STALE
        shifted = copy.deepcopy(_load(PNL_FACE))
        first = sorted(shifted["accounts"])[0]
        shifted["accounts"][first]["bond"]["invested"] = round(
            float(shifted["accounts"][first]["bond"]["invested"]) + 1.0, 2)
        p_stale, rc_stale = build(pnl_face=shifted)
        leg(rc_stale == 3 and str(p_stale["verdict"]).startswith("LEG_AMOUNTS_DO_NOT_REPRODUCE"),
            "a 1-CNY shift in a published leg must be STALE, got %r" % p_stale.get("verdict"))

        # one generation apart
        shifted2 = copy.deepcopy(_load(PNL_FACE))
        shifted2["evidence_cutoff"] = "2026-11-19"
        p_gen, rc_gen = build(pnl_face=shifted2)
        leg(rc_gen == 3 and str(p_gen["verdict"]).startswith("FACES_ARE_ONE_GENERATION_APART"),
            "a cutoff mismatch must be FACES_ARE_ONE_GENERATION_APART, got %r"
            % p_gen.get("verdict"))

        # no panel at all -> named refusal
        p_nopanel, rc_nopanel = build(panels={})
        leg(rc_nopanel == 2 and str(p_nopanel["verdict"]).startswith(
            "CANNOT_PRICE_THE_REPO_ALTERNATIVE"),
            "no panel must refuse and name it, got %r" % p_nopanel.get("verdict"))
        leg(not (p_nopanel.get("totals") or {}), "a refused build must not print totals")

        # no quote on the re-buy session -> that tenor is named, never ffilled
        import pandas as pd
        src = BRL._read("GC001")
        dropped = src["close"].drop(pd.Timestamp(live["window"]["back_day"]), errors="ignore")
        p_drop, rc_drop = build(panels={"GC001": {"close": dropped}, "GC007": BRL._read("GC007")})
        named = any("GC001" in x and "no quote" in x
                    for x in (p_drop.get("not_measured") or []))
        leg(rc_drop == 0 and named and "GC001" not in (p_drop.get("benchmarks") or {}),
            "a tenor with no quote on the re-buy session must be named, not ffilled (got %r)"
            % (p_drop.get("not_measured"),))

        # the ruling follows the money: make the cash sleeve win and the verdict must flip
        winner = copy.deepcopy(_load(PNL_FACE))
        for rec in winner["accounts"].values():
            if rec.get("bond"):
                rec["bond"]["pnl"] = float(rec["bond"].get("invested") or 0.0) * 0.05
        p_win, rc_win = build(pnl_face=winner)
        leg(rc_win == 0 and p_win["verdict"] == "CASH_SLEEVE_BEAT_THE_REPO_ROLL",
            "a cash sleeve that out-earns repo must flip the ruling, got %r"
            % p_win.get("verdict"))

    # selftest must never write the published face or its doc
    before = (os.path.getmtime(OUT) if os.path.isfile(OUT) else None,
              os.path.getmtime(DOC_PATH) if os.path.isfile(DOC_PATH) else None)
    _ = build()
    after = (os.path.getmtime(OUT) if os.path.isfile(OUT) else None,
             os.path.getmtime(DOC_PATH) if os.path.isfile(DOC_PATH) else None)
    leg(before == after, "selftest/build must not touch the published face or doc")

    print("%d/%d PASS" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "--selftest":
        return _selftest()
    if cmd == "run":
        return run(write=True)
    if cmd == "check":
        if not os.path.isfile(OUT):
            print("STALE: face missing at %s" % _rel(OUT))
            return 3
        rc, problems = check(_load(OUT))
        print(json.dumps({"rc": rc, "problems": problems}, ensure_ascii=False))
        return rc
    if cmd == "show":
        print(json.dumps(build()[0], ensure_ascii=False, indent=1))
        return 0
    print("usage: regime_cap_breach_cash_vs_repo.py [run|check|--selftest|show]")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
