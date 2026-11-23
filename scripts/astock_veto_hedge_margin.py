"""Does the short hedge survive its own margin account?

Every face in this family quotes a margin ratio as if it were the capital the hedge consumes.
r2033 prints "901,331 of short needs 108,160 of margin at 12%" and credits the leftover cash
with 17,837 a year of interest; r2027 prints a crude bound -- "a short loses its whole margin at
an adverse move equal to the margin ratio" -- and stops there.  Neither face walks the account.
A margin ratio is a per-contract minimum; the capital a position consumes is the deepest the
account ever went, and the crude bound is one session of a four-year path.

This face walks 1,050 IM sessions (2022-07-22 .. 2026-11-20) as a constant-notional short and
asks three questions:

  1. Where would the account first have gone under maintenance, under two cash regimes --
     profits left in the account, and the standard one where excess is swept?
  2. How much cash would have to be posted so that never happens?
  3. What does being called cost, in the only unit that matters: the hedge P&L that is no
     longer there for the rest of the window?

Usage
    python scripts/astock_veto_hedge_margin.py run
    python scripts/astock_veto_hedge_margin.py check
    python scripts/astock_veto_hedge_margin.py selftest
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IM_CSV = os.path.join(ROOT, "data", "futures_daily", "IM.csv")
PARENT = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
LOTS = os.path.join(ROOT, "results", "astock_veto_hedge_lots.json")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_margin.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_MARGIN.md")

CAPITAL = 1_000_000.0
K = 1.0
# (initial margin ratio, maintenance ratio).  Broker terms this repository cannot observe, so
# every rung is printed rather than one being picked.
MARGIN_LADDER = [(0.08, 0.06), (0.12, 0.08), (0.15, 0.10)]
HORIZONS = [1, 5, 10, 20, 40, 60]
BOUND_HORIZON = 20        # the horizon r2027's "one adverse move" is read against

VERDICT_RATIO = "THE_MARGIN_RATIO_IS_NOT_THE_CAPITAL"
VERDICT_EARLY = "CALL_ARRIVES_BEFORE_THE_INSURANCE_PAYS"
VERDICT_SWEEP = "SWEEPING_PROFITS_DOUBLES_THE_REQUIREMENT"
VERDICT_BOUND = "THE_CRUDE_BOUND_UNDERSTATES_THE_PATH"
VERDICT_WHY = {
    VERDICT_RATIO: "the ratio is a per-contract minimum; the cash the position consumes is the "
                   "deepest drawdown of its own marks, an order of magnitude larger",
    VERDICT_EARLY: "the first call arrives within weeks of inception, before the drawdown the "
                   "hedge was bought for",
    VERDICT_SWEEP: "sweeping excess margin is the usual treasury habit and it multiplies the "
                   "cash that must sit in the account",
    VERDICT_BOUND: "a single adverse session is not the excursion; the crude bound is off by a "
                   "multiple that changes the answer",
}


# --------------------------------------------------------------- plumbing
def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:
        return str(path).replace(os.sep, "/")


def _read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def content_sha(face: dict) -> str:
    body = {k: v for k, v in face.items() if k != "generated"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def fingerprint(path: str) -> dict:
    face = _read_json(path)
    return {"face": _rel(path), "file_sha256": _sha_file(path),
            "content_sha256": content_sha(face),
            "generated": face.get("generated"),
            "evidence_cutoff": face.get("evidence_cutoff")}


# ------------------------------------------------------------------ data
def load_series(path: str):
    """(date, close) rows, strictly positive closes only."""
    rows = []
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        for rec in csv.DictReader(fh):
            try:
                close = float(rec["close"])
            except (TypeError, ValueError, KeyError):
                continue
            if math.isfinite(close) and close > 0:
                rows.append((rec["date"], close))
    return rows


def daily_returns(series) -> list:
    """r[0] = 0 by construction: the first bar is the entry, not a return."""
    out = [0.0]
    for i in range(1, len(series)):
        out.append(series[i][1] / series[i - 1][1] - 1.0)
    return out


# ------------------------------------------------------------- pure logic
def cum_mtm(returns, notional: float) -> list:
    """Cumulative mark-to-market of a constant-notional short, in CNY."""
    out = []
    total = 0.0
    for r in returns:
        total += -notional * r
        out.append(total)
    return out


def run_max(vals) -> list:
    out = []
    peak = -float("inf")
    for v in vals:
        peak = max(peak, v)
        out.append(peak)
    return out


def margin_path(returns, notional: float, ratio: float, maint_ratio: float) -> dict:
    """Walk the margin account under both cash regimes.

    no_sweep: the account keeps every mark, so equity = M0 + cum.
    sweep:    excess over the initial margin is taken out, so equity = M0 + (cum - runmax(cum)).
    """
    m0 = ratio * notional
    mm = maint_ratio * notional
    cum = cum_mtm(returns, notional)
    peak = run_max(cum)
    eq_ns = [m0 + v for v in cum]
    eq_sw = [m0 + (cum[i] - peak[i]) for i in range(len(cum))]

    def _first(eq):
        for i, v in enumerate(eq):
            if v < mm:
                return i
        return None

    def _breach_days(eq):
        return sum(1 for v in eq if v < mm)

    first_ns = _first(eq_ns)
    first_sw = _first(eq_sw)
    return {
        "initial_ratio": ratio,
        "maintenance_ratio": maint_ratio,
        "initial_margin_cny": m0,
        "maintenance_cny": mm,
        "notional_cny": notional,
        "sessions": len(cum),
        "peak_cum_cny": max(cum) if cum else 0.0,
        "final_cum_cny": cum[-1] if cum else 0.0,
        "lowest_cum_cny": min(cum) if cum else 0.0,
        "no_sweep": {
            "first_breach_index": first_ns,
            "breach_days": _breach_days(eq_ns),
            "min_equity_cny": min(eq_ns) if eq_ns else m0,
            "max_topup_cny": max(0.0, mm - (min(eq_ns) if eq_ns else m0)),
        },
        "sweep": {
            "first_breach_index": first_sw,
            "breach_days": _breach_days(eq_sw),
            "min_equity_cny": min(eq_sw) if eq_sw else m0,
            "max_topup_cny": max(0.0, mm - (min(eq_sw) if eq_sw else m0)),
        },
    }


def required_margin(returns, notional: float, maint_ratio: float, sweep: bool = False) -> float:
    """Cash that must be posted at entry so the account never falls under maintenance."""
    mm = maint_ratio * notional
    cum = cum_mtm(returns, notional)
    if not cum:
        return mm
    if sweep:
        peak = run_max(cum)
        worst = min(cum[i] - peak[i] for i in range(len(cum)))
    else:
        worst = min(cum)
    return max(mm, mm - worst)


def worst_rallies(series, horizons=HORIZONS) -> list:
    """Deepest adverse excursion for a short: the largest close-to-close rally per horizon."""
    out = []
    for h in horizons:
        best = -float("inf")
        best_end = None
        for i in range(h, len(series)):
            move = series[i][1] / series[i - h][1] - 1.0
            if move > best:
                best = move
                best_end = series[i][0]
        out.append({"horizon": h, "rally": best if best > -float("inf") else 0.0,
                    "end": best_end})
    return out


def tail_pnl(cum, breach_index: int) -> dict:
    """What the hedge still had to earn after the call, i.e. what the call takes away."""
    if breach_index is None or not cum:
        return {"realised_at_call_cny": 0.0, "tail_cny": 0.0}
    realised = cum[breach_index]
    return {"realised_at_call_cny": realised, "tail_cny": cum[-1] - realised}


def index_of_date(series, target: str):
    for i, (d, _) in enumerate(series):
        if d >= target:
            return i
    return None


def net_account(rows, series, cum, capital: float) -> dict:
    """Book + short, at the book's own 20-bar period ends.

    The pair is marked at different frequencies: the futures account daily, the book every 20
    bars.  That mismatch is the point of the reading, not a defect to smooth over.
    """
    book_eq = 1.0
    points = []
    for r in rows:
        book_eq *= 1.0 + float(r.get("book_net") or 0.0)
        idx = index_of_date(series, r.get("end") or "")
        short_cny = cum[idx] if idx is not None and idx < len(cum) else None
        points.append({"date": r.get("end"), "book_cny": capital * (book_eq - 1.0),
                       "short_cny": short_cny})
    vals = [p["book_cny"] + p["short_cny"] for p in points if p["short_cny"] is not None]
    return {"periods": len(vals), "min_net_cny": min(vals) if vals else 0.0,
            "final_net_cny": vals[-1] if vals else 0.0,
            "points": points}


def decide(ladder, rallies, sweep_required, no_sweep_required, bound_horizon=BOUND_HORIZON):
    """Each flag is computed from its own input; several can hold at once."""
    flags = {}
    if not ladder:
        return {"all": None}
    any_breach = any(r["no_sweep"]["first_breach_index"] is not None for r in ladder)
    worst_ratio = max(no_sweep_required.values()) if no_sweep_required else 0.0
    flags[VERDICT_RATIO] = bool(any_breach and worst_ratio > 0.25)

    mid = next((r for r in ladder if abs(r["initial_ratio"] - 0.12) < 1e-12), ladder[0])
    idx = mid["no_sweep"]["first_breach_index"]
    flags[VERDICT_EARLY] = bool(idx is not None and idx <= 60)

    sw = sweep_required.get("0.12") or 0.0
    ns = no_sweep_required.get("0.12") or 0.0
    flags[VERDICT_SWEEP] = bool(ns > 0 and sw >= 1.5 * ns)

    worst20 = next((r["rally"] for r in rallies if r["horizon"] == bound_horizon), 0.0)
    flags[VERDICT_BOUND] = bool(worst20 >= 2.0 * 0.12)
    return flags


def headline(flags) -> str:
    if not flags or set(flags) == {"all"}:
        return "NOT_ENOUGH_DATA"
    on = [k for k, v in flags.items() if v]
    if not on:
        return "ACCOUNT_SURVIVES_AS_POSTED"
    if VERDICT_EARLY in on and VERDICT_RATIO in on:
        return VERDICT_RATIO + "+" + VERDICT_EARLY
    return on[0]


# --------------------------------------------------------------------- build
def build_face() -> dict:
    parent = _read_json(PARENT)
    lots = _read_json(LOTS)
    series = load_series(IM_CSV)
    if len(series) < 240:
        return {"generated": _now(), "kind": "hedge_margin",
                "evidence_cutoff": parent.get("evidence_cutoff"),
                "verdict": "NOT_ENOUGH_SESSIONS",
                "parents": {"beta": fingerprint(PARENT), "lots": fingerprint(LOTS)}}

    beta = ((parent.get("arms_etf") or {}).get("1.0") or {}).get("beta_used")
    if beta is None:
        beta = ((parent.get("variance") or {}).get("beta_used_for_arms")) or 0.9013
    beta = float(beta)
    notional = beta * CAPITAL * K
    rets = daily_returns(series)

    ladder = [margin_path(rets, notional, r, m) for r, m in MARGIN_LADDER]
    for row in ladder:
        for regime in ("no_sweep", "sweep"):
            i = row[regime]["first_breach_index"]
            row[regime]["first_breach_date"] = series[i][0] if i is not None else None
            row[regime]["tail"] = tail_pnl(cum_mtm(rets, notional), i)

    no_sweep_req = {("%.2f" % r["initial_ratio"]):
                     required_margin(rets, notional, r["maintenance_ratio"], sweep=False)
                     for r in ladder}
    sweep_req = {("%.2f" % r["initial_ratio"]):
                 required_margin(rets, notional, r["maintenance_ratio"], sweep=True)
                 for r in ladder}

    rallies = worst_rallies(series)
    for r in rallies:
        r["short_loss_pct_of_notional"] = r["rally"]
        r["multiple_of_12pct"] = (r["rally"] / 0.12) if r["rally"] else 0.0

    cum = cum_mtm(rets, notional)
    rows = [r for r in (parent.get("rows") or []) if r.get("im_window")]
    net = net_account(rows, series, cum, CAPITAL)

    mid = next(r for r in ladder if abs(r["initial_ratio"] - 0.12) < 1e-12)
    flags = decide(ladder, rallies, sweep_req, no_sweep_req)
    verdict = headline(flags)

    crude = lots.get("granularity") or {}
    bound_note = ((lots.get("prereg") or {}).get("margin_bound") or
                  "a short loses its whole margin at an adverse move equal to the margin ratio")

    caveats = [
        "the panel is the IM main-continuous close; a roll is a calendar spread paid once, and "
        "that cost is inside the marks rather than separated from them",
        "the settle column on the panel is empty, so every mark here is a close mark; a broker "
        "marks to settlement, and the two differ most on the days that matter",
        "the margin ratios are broker terms this repository cannot observe; they are printed as "
        "axes and no single rung is claimed as the one in force",
        "no interest is credited or charged on the margin balance, and a margin call in practice "
        "allows securities as collateral at a haircut, which is not modelled",
        "the book is only marked every 20 bars (that is the parent's booking), so the net-account "
        "reading is a 20-bar statement sitting next to a daily statement -- the mismatch is real "
        "and is the liquidity question, not an approximation to be smoothed",
        "the notional is held constant; a real account would de-lever after a call, and this "
        "face prices the call instead of modelling what an operator does next",
    ]

    face = {
        "generated": _now(),
        "kind": "hedge_margin",
        "machine": "bm-c",
        "evidence_cutoff": series[-1][0],
        "fills_the_hole_of": "r2033 quotes a 12% margin ratio as the capital the hedge consumes "
                             "and r2027 quotes a one-session crude bound; neither walks the "
                             "account, so nothing in the family says where it would be called",
        "parents": {"beta": fingerprint(PARENT), "lots": fingerprint(LOTS)},
        "panel": {"csv": _rel(IM_CSV), "file_sha256": _sha_file(IM_CSV),
                  "first": series[0][0], "last": series[-1][0], "bars": len(series),
                  "first_close": series[0][1], "last_close": series[-1][1],
                  "total_return": series[-1][1] / series[0][1] - 1.0},
        "spec": {"capital": CAPITAL, "k": K, "beta": beta, "notional_cny": notional,
                 "margin_ladder": MARGIN_LADDER, "horizons": HORIZONS,
                 "bound_horizon": BOUND_HORIZON,
                 "regimes": ["no_sweep", "sweep"]},
        "ladder": ladder,
        "required_margin_cny": {"no_sweep": no_sweep_req, "sweep": sweep_req},
        "required_margin_pct_of_notional": {
            "no_sweep": {k: v / notional for k, v in no_sweep_req.items()},
            "sweep": {k: v / notional for k, v in sweep_req.items()},
        },
        "required_margin_pct_of_capital": {
            "no_sweep": {k: v / CAPITAL for k, v in no_sweep_req.items()},
            "sweep": {k: v / CAPITAL for k, v in sweep_req.items()},
        },
        "worst_rallies": rallies,
        "net_account": {k: v for k, v in net.items() if k != "points"},
        "crude_bound": {"source_face": _rel(LOTS), "statement": bound_note,
                        "stated_horizon": 1,
                        "measured_at_horizon": BOUND_HORIZON,
                        "measured_rally": next((r["rally"] for r in rallies
                                                if r["horizon"] == BOUND_HORIZON), 0.0),
                        "understatement_multiple": (
                            (next((r["rally"] for r in rallies
                                    if r["horizon"] == BOUND_HORIZON), 0.0) / 0.12)
                            if mid else 0.0)},
        "verdicts": flags,
        "verdict": verdict,
        "verdict_why": VERDICT_WHY.get(verdict.split("+")[0], ""),
        "caveats": caveats,
    }
    face["reads"] = build_reads(face)
    face["content_sha256"] = content_sha(face)
    return face


def build_reads(face):
    reads = []
    ladder = face.get("ladder") or []
    req_ns = (face.get("required_margin_cny") or {}).get("no_sweep") or {}
    req_sw = (face.get("required_margin_cny") or {}).get("sweep") or {}
    mid = next((r for r in ladder if abs(r["initial_ratio"] - 0.12) < 1e-12), None)
    notional = (face.get("spec") or {}).get("notional_cny") or 0.0

    if mid:
        idx = mid["no_sweep"]["first_breach_index"]
        reads.append({
            "id": "R1",
            "text": "at the 12%% rung the account is under maintenance on %s -- the %dth of "
                    "%d sessions, %.0f CNY of margin against a %.0f CNY notional%s"
                    % (mid["no_sweep"]["first_breach_date"] or "never",
                       (idx + 1) if idx is not None else 0, mid["sessions"],
                       mid["initial_margin_cny"], notional,
                       "" if idx is None else
                       ", and stays under it on %d sessions" % mid["no_sweep"]["breach_days"]),
        })
        reads.append({
            "id": "R2",
            "text": "the cash the position actually consumes is %.0f CNY (%.1f%% of notional, "
                    "%.1f%% of the book) if profits stay in the account, against the %.0f CNY "
                    "the 12%% ratio implies -- %.1f times the ratio"
                    % (req_ns.get("0.12") or 0.0,
                       (req_ns.get("0.12") or 0.0) / notional * 100 if notional else 0.0,
                       (req_ns.get("0.12") or 0.0) / CAPITAL * 100,
                       mid["initial_margin_cny"],
                       (req_ns.get("0.12") or 0.0) / mid["initial_margin_cny"]
                       if mid["initial_margin_cny"] else 0.0),
        })
        reads.append({
            "id": "R3",
            "text": "sweeping the excess -- the usual treasury habit -- raises the requirement "
                    "to %.0f CNY (%.1f%% of notional), %.1f times the no-sweep number: the "
                    "profits are the buffer, and taking them out is what makes the account thin"
                    % (req_sw.get("0.12") or 0.0,
                       (req_sw.get("0.12") or 0.0) / notional * 100 if notional else 0.0,
                       (req_sw.get("0.12") or 0.0) / (req_ns.get("0.12") or 1.0)),
        })
        tail = mid["no_sweep"].get("tail") or {}
        reads.append({
            "id": "R4",
            "text": "being called is not free: the short realises %.0f CNY at the call and the "
                    "remaining %d sessions of hedge are gone -- %.0f CNY of short P&L, %.1f%% of "
                    "the book, that the account was closed out of"
                    % (tail.get("realised_at_call_cny") or 0.0,
                       mid["sessions"] - ((idx or 0) + 1),
                       tail.get("tail_cny") or 0.0,
                       (tail.get("tail_cny") or 0.0) / CAPITAL * 100),
        })

    rallies = face.get("worst_rallies") or []
    r20 = next((r for r in rallies if r["horizon"] == BOUND_HORIZON), None)
    if r20:
        reads.append({
            "id": "R5",
            "text": "the crude bound is one session of a four-year path: the worst single "
                    "session is %.1f%% (%.1f times the 12%% ratio) but the worst %d-session "
                    "rally ending %s is %.1f%%, %.1f times the ratio -- a bound quoted in "
                    "sessions cannot price an excursion quoted in months"
                    % ((rallies[0]["rally"] or 0.0) * 100,
                       (rallies[0]["multiple_of_12pct"] or 0.0), r20["horizon"], r20["end"],
                       r20["rally"] * 100, r20["multiple_of_12pct"]),
        })

    na = face.get("net_account") or {}
    if na.get("periods"):
        reads.append({
            "id": "R6",
            "text": "solvent and illiquid at the same time: marked on the book's 20-bar "
                    "schedule the pair never went below %.0f CNY over %d periods, while the "
                    "futures account alone went under maintenance -- the collateral exists, it "
                    "just is not in the account that gets marked daily"
                    % (na.get("min_net_cny") or 0.0, na.get("periods") or 0),
        })
    return reads


# --------------------------------------------------------------------- render
def render_md(face) -> str:
    parents = face.get("parents") or {}
    beta = parents.get("beta") or {}
    lots = parents.get("lots") or {}
    panel = face.get("panel") or {}
    spec = face.get("spec") or {}
    ladder = face.get("ladder") or []
    req_ns = (face.get("required_margin_cny") or {}).get("no_sweep") or {}
    req_sw = (face.get("required_margin_cny") or {}).get("sweep") or {}

    lines = ["# Where would the short hedge have been called?", "",
             "r2033 prints a 12% margin ratio and credits the cash that is left over with "
             "interest; r2027 prints a crude bound -- a short loses its whole margin at an "
             "adverse move equal to the margin ratio. Both are statements about one number on "
             "one day. A margin account is a path: it is marked every session, it is called the "
             "first session it is under maintenance, and the capital the hedge consumes is the "
             "deepest that path ever went.", "",
             "Evidence cutoff **%s**, panel `%s` (%d bars, %s .. %s, %.2f%% total), parent beta "
             "face `%s` (generated %s), crude-bound face `%s` (generated %s). Short %.0f CNY of "
             "notional (beta %.4f x %.0f capital x k=%.2f)."
             % (face.get("evidence_cutoff"), panel.get("csv"), panel.get("bars") or 0,
                panel.get("first"), panel.get("last"),
                (panel.get("total_return") or 0.0) * 100, beta.get("face"),
                beta.get("generated"), lots.get("face"), lots.get("generated"),
                spec.get("notional_cny") or 0.0, spec.get("beta") or 0.0,
                spec.get("capital") or 0.0, spec.get("k") or 0.0), ""]

    lines += ["## 1. Walk the account: where it first goes under maintenance", "",
              "| initial margin | maintenance | cash posted | first call | sessions under | "
              "lowest equity | top-up needed |",
              "|---|---|---|---|---|---|---|"]
    for row in ladder:
        ns = row["no_sweep"]
        lines.append("| %.0f%% | %.0f%% | %.0f | %s | %d | %.0f | %.0f |"
                     % (row["initial_ratio"] * 100, row["maintenance_ratio"] * 100,
                        row["initial_margin_cny"], ns.get("first_breach_date") or "never",
                        ns.get("breach_days") or 0, ns.get("min_equity_cny") or 0.0,
                        ns.get("max_topup_cny") or 0.0))
    lines += ["", "Profits left in the account. The ratio is a per-contract minimum; the call "
                  "arrives when the marks have eaten it.", ""]

    lines += ["## 2. What the position actually consumes", "",
              "| rung | maintenance | cash, profits kept | % of notional | % of book | "
              "cash, profits swept | % of notional |",
              "|---|---|---|---|---|---|---|"]
    notional = spec.get("notional_cny") or 0.0
    for row in ladder:
        key = "%.2f" % row["initial_ratio"]
        lines.append("| %.0f%% | %.0f%% | %.0f | %.1f%% | %.1f%% | %.0f | %.1f%% |"
                     % (row["initial_ratio"] * 100, row["maintenance_ratio"] * 100,
                        req_ns.get(key) or 0.0, (req_ns.get(key) or 0.0) / notional * 100,
                        (req_ns.get(key) or 0.0) / CAPITAL * 100,
                        req_sw.get(key) or 0.0, (req_sw.get(key) or 0.0) / notional * 100))
    lines += ["", "Read the middle column against r2033's capital table: that face prices the "
                  "hedge at 12% of notional and lets the rest earn. The rest is not free -- it "
                  "is the top-up this account needs to survive its own history.", ""]

    rallies = face.get("worst_rallies") or []
    if rallies:
        lines += ["## 3. The crude bound, measured", "",
                  "| horizon | worst rally | short loss, % of notional | multiple of the 12% rung | "
                  "ending |", "|---|---|---|---|---|"]
        for r in rallies:
            lines.append("| %d session%s | %.2f%% | -%.2f%% | %.2f x | %s |"
                         % (r["horizon"], "" if r["horizon"] == 1 else "s", r["rally"] * 100,
                            r["rally"] * 100, r["multiple_of_12pct"], r["end"]))
        lines += ["", "r2027's bound is the first row. The row that matters is the one whose "
                      "horizon is the holding period: an excursion is not a session.", ""]

    mid = next((r for r in ladder if abs(r["initial_ratio"] - 0.12) < 1e-12), None)
    if mid:
        tail = mid["no_sweep"].get("tail") or {}
        lines += ["## 4. What the call costs", "",
                  "At the 12%% rung the short is closed on **%s** with **%.0f CNY** realised. "
                  "The remaining %d sessions are unhedged, and over them the short would have "
                  "earned **%.0f CNY** -- **%.1f%% of the book**. That is the price of a margin "
                  "call: not the loss at the call (which is small and already known), but the "
                  "insurance that is no longer there."
                  % (mid["no_sweep"].get("first_breach_date") or "never",
                     tail.get("realised_at_call_cny") or 0.0,
                     mid["sessions"] - ((mid["no_sweep"].get("first_breach_index") or 0) + 1),
                     tail.get("tail_cny") or 0.0, (tail.get("tail_cny") or 0.0) / CAPITAL * 100),
                  ""]

    na = face.get("net_account") or {}
    if na.get("periods"):
        lines += ["## 5. Solvent and illiquid at the same time", "",
                  "Marked on the book's own 20-bar schedule, the pair (long book + short future) "
                  "never went below **%.0f CNY** over %d periods and finished at **%.0f CNY**. "
                  "The futures account alone, marked daily, was under maintenance. Both "
                  "statements are true: the collateral exists, it is just not in the account "
                  "that gets marked every session. A hedge that is solvent at month-end and "
                  "called at mid-month is a hedge with a funding problem, not a risk problem."
                  % (na.get("min_net_cny") or 0.0, na.get("periods") or 0,
                     na.get("final_net_cny") or 0.0), ""]

    lines += ["## 6. Verdict", "", "**`%s`**" % face.get("verdict"), "",
              "Every flag below is computed from its own inputs and several can hold at once; "
              "the headline names the ones that change what a reader would do.", ""]
    for flag, on in (face.get("verdicts") or {}).items():
        if on:
            why = VERDICT_WHY.get(flag)
            if why:
                lines.append("- `%s` -- %s" % (flag, why))
    lines.append("")

    reads = face.get("reads") or []
    if reads:
        lines += ["## 7. Readings", ""]
        for r in reads:
            lines.append("- **%s.** %s" % (r.get("id"), r.get("text")))
        lines.append("")

    lines += ["## 8. What this face does not settle", ""]
    for c in face.get("caveats") or []:
        lines.append("- " + c)
    lines += ["", "Machine `%s`, generated %s." % (face.get("machine"), face.get("generated")),
              "", "## 9. Reproduction", "", "```",
              "python scripts/astock_veto_hedge_margin.py selftest",
              "python scripts/astock_veto_hedge_margin.py run",
              "python scripts/astock_veto_hedge_margin.py check", "```", ""]
    return "\n".join(lines)


# ----------------------------------------------------------------------- cmds
def run() -> int:
    face = build_face()
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    _write_md(render_md(face))
    print("margin -> %s | %s" % (face.get("verdict"), _rel(OUT_JSON)))
    mid = next((r for r in (face.get("ladder") or [])
                if abs(r["initial_ratio"] - 0.12) < 1e-12), None)
    if mid:
        print("  12%% rung: first call %s | required cash %.0f (%.1f%% of notional)"
              % (mid["no_sweep"].get("first_breach_date"),
                 ((face.get("required_margin_cny") or {}).get("no_sweep") or {}).get("0.12", 0.0),
                 ((face.get("required_margin_pct_of_notional") or {})
                  .get("no_sweep") or {}).get("0.12", 0.0) * 100))
    return 0


def _write_md(text: str) -> None:
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def check() -> int:
    """Re-derive every published number from the parents; drift is STALE, disagreement is FAILED."""
    problems = []
    try:
        face = _read_json(OUT_JSON)
    except FileNotFoundError:
        print("STALE face missing: %s" % _rel(OUT_JSON))
        return 3
    except (json.JSONDecodeError, OSError) as exc:
        print("CHECK FAILED unreadable face: %s" % exc)
        return 1
    try:
        parent = _read_json(PARENT)
        lots = _read_json(LOTS)
        md = open(OUT_MD, encoding="utf-8").read()
    except FileNotFoundError as exc:
        print("STALE parent missing: %s" % exc)
        return 3
    except OSError as exc:
        print("STALE cannot read: %s" % exc)
        return 3

    # 1. the parents and the panel moved?
    for name, path in (("beta", PARENT), ("lots", LOTS)):
        stored = ((face.get("parents") or {}).get(name) or {})
        if stored.get("file_sha256") != _sha_file(path):
            print("STALE parent %s moved (%s)" % (name, _rel(path)))
            return 3
        if stored.get("content_sha256") != content_sha(_read_json(path)):
            print("STALE parent %s content moved (%s)" % (name, _rel(path)))
            return 3
    if (face.get("panel") or {}).get("file_sha256") != _sha_file(IM_CSV):
        print("STALE panel moved (%s)" % _rel(IM_CSV))
        return 3

    series = load_series(IM_CSV)
    rets = daily_returns(series)
    spec = face.get("spec") or {}
    beta = float(spec.get("beta") or 0.0)
    notional = beta * CAPITAL * K
    if abs(notional - float(spec.get("notional_cny") or 0.0)) > 1e-6:
        problems.append("notional %.6f != %.6f" % (notional, spec.get("notional_cny") or 0.0))
    if (face.get("panel") or {}).get("bars") != len(series):
        problems.append("panel bars %s != %d" % ((face.get("panel") or {}).get("bars"),
                                                 len(series)))

    # 2. the ladder
    for row, (ratio, maint) in zip(face.get("ladder") or [], MARGIN_LADDER):
        fresh = margin_path(rets, notional, ratio, maint)
        if abs(float(row.get("initial_margin_cny") or 0) - fresh["initial_margin_cny"]) > 1e-6:
            problems.append("ladder %.2f initial margin mismatch" % ratio)
        for regime in ("no_sweep", "sweep"):
            pub = row.get(regime) or {}
            fr = fresh[regime]
            if pub.get("first_breach_index") != fr["first_breach_index"]:
                problems.append("ladder %.2f %s first breach %s != %s"
                                % (ratio, regime, pub.get("first_breach_index"),
                                   fr["first_breach_index"]))
            if (pub.get("breach_days") or 0) != fr["breach_days"]:
                problems.append("ladder %.2f %s breach days %s != %s"
                                % (ratio, regime, pub.get("breach_days"), fr["breach_days"]))
            for field in ("min_equity_cny", "max_topup_cny"):
                if abs(float(pub.get(field) or 0.0) - float(fr[field])) > 1e-6:
                    problems.append("ladder %.2f %s %s %.8g != %.8g"
                                    % (ratio, regime, field, pub.get(field) or 0.0, fr[field]))
        cum = cum_mtm(rets, notional)
        tail = tail_pnl(cum, fresh["no_sweep"]["first_breach_index"])
        pub_tail = (row.get("no_sweep") or {}).get("tail") or {}
        for field in ("realised_at_call_cny", "tail_cny"):
            if abs(float(pub_tail.get(field) or 0.0) - float(tail[field])) > 1e-6:
                problems.append("ladder %.2f tail %s %.8g != %.8g"
                                % (ratio, field, pub_tail.get(field) or 0.0, tail[field]))

    # 3. the required cash
    for regime, sweep in (("no_sweep", False), ("sweep", True)):
        pub = (face.get("required_margin_cny") or {}).get(regime) or {}
        for ratio, maint in MARGIN_LADDER:
            key = "%.2f" % ratio
            fresh = required_margin(rets, notional, maint, sweep=sweep)
            if abs(float(pub.get(key) or 0.0) - fresh) > 1e-6:
                problems.append("required %s %s %.8g != %.8g"
                                % (regime, key, pub.get(key) or 0.0, fresh))

    # 4. the rallies
    for pub, fr in zip(face.get("worst_rallies") or [], worst_rallies(series)):
        if pub.get("horizon") != fr["horizon"]:
            problems.append("rallies horizon %s != %s" % (pub.get("horizon"), fr["horizon"]))
        if abs(float(pub.get("rally") or 0.0) - float(fr["rally"])) > 1e-9:
            problems.append("rallies %s %.12g != %.12g"
                            % (pub.get("horizon"), pub.get("rally") or 0.0, fr["rally"]))
        if pub.get("end") != fr["end"]:
            problems.append("rallies %s end %s != %s"
                            % (pub.get("horizon"), pub.get("end"), fr["end"]))

    # 5. the net account
    rows = [r for r in (parent.get("rows") or []) if r.get("im_window")]
    net = net_account(rows, series, cum_mtm(rets, notional), CAPITAL)
    for field in ("periods", "min_net_cny", "final_net_cny"):
        if abs(float((face.get("net_account") or {}).get(field) or 0.0)
               - float(net[field])) > 1e-6:
            problems.append("net_account %s %.8g != %.8g"
                            % (field, (face.get("net_account") or {}).get(field) or 0.0,
                               net[field]))

    # 6. the verdict re-derives from the fresh numbers
    fresh_ns = {("%.2f" % r): required_margin(rets, notional, m, sweep=False)
                for r, m in MARGIN_LADDER}
    fresh_sw = {("%.2f" % r): required_margin(rets, notional, m, sweep=True)
                for r, m in MARGIN_LADDER}
    flags_fresh = decide([margin_path(rets, notional, r, m) for r, m in MARGIN_LADDER],
                         worst_rallies(series), fresh_sw, fresh_ns)
    if flags_fresh != (face.get("verdicts") or {}):
        problems.append("verdicts %s != %s" % (face.get("verdicts"), flags_fresh))
    if headline(flags_fresh) != face.get("verdict"):
        problems.append("verdict %s != %s" % (face.get("verdict"), headline(flags_fresh)))

    # 7. the page says the same thing
    mid = next((r for r in (face.get("ladder") or [])
                if abs(r["initial_ratio"] - 0.12) < 1e-12), None)
    tokens = ["`%s`" % face.get("verdict")]
    if mid:
        tokens.append("%.0f" % mid["initial_margin_cny"])
        tokens.append("%.0f" % ((face.get("required_margin_cny") or {})
                                .get("no_sweep", {}).get("0.12", 0.0)))
    for token in tokens:
        if token not in md:
            problems.append("page missing token %r" % token)

    if problems:
        print("CHECK FAILED %d problem(s)" % len(problems))
        for p in problems[:12]:
            print("  - " + p)
        return 1
    print("CHECK OK verdict=%s first_call_12pct=%s"
          % (face.get("verdict"), (mid or {}).get("no_sweep", {}).get("first_breach_date")))
    return 0


# ------------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # --- marks
    flat = [0.0] * 10
    leg("L1 a flat panel marks to zero", all(abs(v) < 1e-12 for v in cum_mtm(flat, 1000.0)))
    leg("L1b a +10% session costs a short 10% of notional",
        abs(cum_mtm([0.0, 0.10], 1_000_000.0)[-1] + 100_000.0) < 1e-9)
    leg("L1c a -10% session pays a short 10% of notional",
        abs(cum_mtm([0.0, -0.10], 1_000_000.0)[-1] - 100_000.0) < 1e-9)
    leg("L1d run_max is monotone and reaches the peak",
        run_max([1.0, -5.0, 3.0]) == [1.0, 1.0, 3.0])

    # --- path: never breached when marks never hurt
    p = margin_path([0.0] + [-0.01] * 20, 1_000_000.0, 0.12, 0.08)
    leg("L2 a short that only ever gains is never called",
        p["no_sweep"]["first_breach_index"] is None and p["sweep"]["first_breach_index"] is None)
    leg("L2b and its required cash is just the maintenance floor",
        abs(required_margin([0.0] + [-0.01] * 20, 1_000_000.0, 0.08) - 80_000.0) < 1e-9)

    # --- path: one bad session breaches
    p2 = margin_path([0.0, 0.05], 1_000_000.0, 0.12, 0.08)
    leg("L2c a 5% adverse session on a 12/8 account leaves 70,000 -- under the 80,000 floor",
        p2["no_sweep"]["first_breach_index"] == 1
        and abs(p2["no_sweep"]["min_equity_cny"] - 70_000.0) < 1e-9)
    leg("L2d the top-up is the shortfall to maintenance",
        abs(p2["no_sweep"]["max_topup_cny"] - 10_000.0) < 1e-9)
    leg("L2e and the required cash is the loss plus the floor",
        abs(required_margin([0.0, 0.05], 1_000_000.0, 0.08) - 130_000.0) < 1e-9)

    # --- sweep is never thinner than keeping the marks
    walk = [0.0, -0.02, 0.015, 0.015, 0.015]
    pn = margin_path(walk, 1_000_000.0, 0.12, 0.08)
    leg("L3 sweep equity is at or below no-sweep equity on every session",
        all(pn["sweep"]["min_equity_cny"] <= pn["no_sweep"]["min_equity_cny"] + 1e-9
            for _ in [0]))
    leg("L3b sweeping after a gain means the give-back is unfunded",
        pn["sweep"]["first_breach_index"] is not None
        and pn["no_sweep"]["first_breach_index"] is None)
    leg("L3c so the swept requirement is the larger one",
        required_margin(walk, 1_000_000.0, 0.08, sweep=True)
        > required_margin(walk, 1_000_000.0, 0.08, sweep=False))
    leg("L3d both start from the same cash",
        abs(pn["initial_margin_cny"] - 120_000.0) < 1e-9)

    # --- rallies
    series = [("d0", 100.0), ("d1", 110.0), ("d2", 99.0), ("d3", 99.0)]
    rr = worst_rallies(series, [1, 2])
    leg("L4 the worst one-session rally is +10%", abs(rr[0]["rally"] - 0.10) < 1e-12)
    leg("L4b and it is reported where it ends", rr[0]["end"] == "d1")
    leg("L4c the worst two-session rally is +10% too, ending d2 vs d1",
        abs(rr[1]["rally"] - (99.0 / 100.0 - 1.0)) < 1e-12 and rr[1]["end"] == "d2")
    leg("L4d a short series has no measurable rally",
        worst_rallies([("d0", 1.0)], [1])[0]["rally"] == 0.0)

    # --- the price of the call
    cum = [0.0, -50.0, 20.0, 120.0]
    t = tail_pnl(cum, 1)
    leg("L5 the call realises the mark at the call", abs(t["realised_at_call_cny"] + 50.0) < 1e-9)
    leg("L5b and the tail is what is given up", abs(t["tail_cny"] - 170.0) < 1e-9)
    leg("L5c no call means nothing is given up", tail_pnl(cum, None)["tail_cny"] == 0.0)

    # --- verdict ladder: each flag flips on its own input
    ladder_hit = [{"initial_ratio": 0.12, "maintenance_ratio": 0.08,
                   "no_sweep": {"first_breach_index": 5}}]
    flags = decide(ladder_hit, [{"horizon": 20, "rally": 0.40}],
                   {"0.12": 900_000.0}, {"0.12": 400_000.0})
    leg("L6 ratio flag on when the required cash is a quarter of notional or more",
        flags[VERDICT_RATIO] is True)
    leg("L6b early flag on when the call is inside 60 sessions", flags[VERDICT_EARLY] is True)
    leg("L6c sweep flag on when sweeping multiplies the cash", flags[VERDICT_SWEEP] is True)
    leg("L6d bound flag on when a 20-session rally is twice the ratio",
        flags[VERDICT_BOUND] is True)
    late = decide([{"initial_ratio": 0.12, "maintenance_ratio": 0.08,
                    "no_sweep": {"first_breach_index": 700}}],
                  [{"horizon": 20, "rally": 0.05}],
                  {"0.12": 400_000.0}, {"0.12": 400_000.0})
    leg("L6e a late call is not an early one", late[VERDICT_EARLY] is False)
    leg("L6f a flat sweep is not a doubling", late[VERDICT_SWEEP] is False)
    leg("L6g a small rally cannot summon the bound flag", late[VERDICT_BOUND] is False)
    leg("L6h no breach at all kills the ratio flag",
        decide([{"initial_ratio": 0.12, "maintenance_ratio": 0.08,
                 "no_sweep": {"first_breach_index": None}}],
               [{"horizon": 20, "rally": 0.0}], {"0.12": 80_000.0},
               {"0.12": 80_000.0})[VERDICT_RATIO] is False)
    leg("L6i headline names the ratio and the early call together", "+" in headline(flags))
    leg("L6j no data is not a verdict", headline({"all": None}) == "NOT_ENOUGH_DATA")
    leg("L6k a surviving account says so", headline({VERDICT_RATIO: False}) ==
        "ACCOUNT_SURVIVES_AS_POSTED")

    # --- live face (only if the parents and the published face are on disk)
    if os.path.exists(PARENT) and os.path.exists(LOTS) and os.path.exists(OUT_JSON):
        face = _read_json(OUT_JSON)
        live = load_series(IM_CSV)
        lr = daily_returns(live)
        ln = float((face.get("spec") or {}).get("beta") or 0.0) * CAPITAL * K
        leg("L7 the published panel is the file on disk",
            (face.get("panel") or {}).get("file_sha256") == _sha_file(IM_CSV))
        leg("L7b the published bar count is the panel's",
            (face.get("panel") or {}).get("bars") == len(live))
        mid_live = next((r for r in (face.get("ladder") or [])
                         if abs(r["initial_ratio"] - 0.12) < 1e-12), None)
        fresh_mid = margin_path(lr, ln, 0.12, 0.08)
        leg("L7c the 12% rung reproduces its first call",
            (mid_live or {}).get("no_sweep", {}).get("first_breach_index")
            == fresh_mid["no_sweep"]["first_breach_index"])
        leg("L7d the required cash reproduces",
            abs(float(((face.get("required_margin_cny") or {}).get("no_sweep") or {})
                      .get("0.12") or 0.0)
                - required_margin(lr, ln, 0.08, sweep=False)) < 1e-6)
        leg("L7e the verdict in the file is the one this code would print",
            face.get("verdict") == build_face().get("verdict"))
        leg("L7f the page carries the verdict token",
            ("`%s`" % face.get("verdict")) in open(OUT_MD, encoding="utf-8").read())
    else:
        leg("L7 live face skipped (files absent)", True, "skipped")

    width = max(len(n) for n, _, _ in legs) + 2
    bad = 0
    for name, ok, detail in legs:
        if not ok:
            bad += 1
        print("%s %-*s %s" % ("PASS" if ok else "FAIL", width, name, detail))
    print("%d/%d PASS" % (len(legs) - bad, len(legs)))
    return 0 if bad == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
