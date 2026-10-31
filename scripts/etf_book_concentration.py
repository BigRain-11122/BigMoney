"""ETF book -- who actually earns the money, and does the edge survive without them?

Every published face of this book quotes one number (CAGR / Sharpe / max drawdown) for a
book that re-picks 12 of ~1,500 ETFs every 20 bars, and none of them answers the question
an allocator asks next: *how concentrated is that return?* A book whose profit comes from
four gold ETFs held in 45% of its decisions is a different object from one that earns
broadly, even when both print the same CAGR -- the first bet is on gold continuing, the
second is on the ranking rule.

Two measurements, both read off the engine's own decision stream (`diag`):

  * contribution -- replay the engine's P&L bar by bar with the weights it actually held
    and split each bar's return by symbol. This is arithmetic, not a second strategy, and
    the identity leg below refuses to publish if the replica does not reproduce the
    engine's equity curve: a face that measures its own arithmetic is worse than no face.
  * leave-out -- drop the top contributors from the *universe* and re-price the book. This
    is NOT "the same book minus those names": removing a name changes which names get
    picked (the substitution is real and is disclosed, E188/E293 class). It answers the
    allocator's question -- if the top names stop working, is there still a book? -- and
    the control leg (masking a name the book never held) must be bit-identical, or the
    experiment is measuring the panel build instead of the exclusion.

Criteria are frozen below, echoed into the payload, and the gate re-derives the verdict
from the published rows, so a later "small adjustment" cannot pass as the rule.

Usage:
    python scripts/etf_book_concentration.py run [--out=...]
    python scripts/etf_book_concentration.py --check
    python scripts/etf_book_concentration.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_book_production as P

OUT_JSON = ROOT / "results" / "etf_book_concentration.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_CONCENTRATION.md"

SCRIPT = "scripts/etf_book_concentration.py"
FACE = "results/etf_book_concentration.json"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run; the payload echoes them and the gate refuses a face whose
# echoed criteria differ.
N_HOLD = 12              # the book in force
REBAL = 20
COST = 0.0010            # 10 bp per side, the published convention
VOL_TARGET = P.TARGET_VOL
TOP_K = 3                # "the top names" = the three biggest contributors
TOP3_SHARE_BAND = 0.55   # at or below this share of the return sum = BROAD
EDGE_SURVIVES_CAGR_SHARE = 0.50   # leave-top-k must keep this share of baseline CAGR
EDGE_SURVIVES_SHARPE = 0.50       # and this Sharpe
MIN_DECISIONS = 8        # fewer decisions than this: refuse to judge (no number printed)

CRITERIA = {
    "n_hold": N_HOLD,
    "rebal": REBAL,
    "cost_bp_per_side": COST * 1e4,
    "vol_target": VOL_TARGET,
    "top_k": TOP_K,
    "top3_share_band": TOP3_SHARE_BAND,
    "edge_survives_cagr_share": EDGE_SURVIVES_CAGR_SHARE,
    "edge_survives_sharpe": EDGE_SURVIVES_SHARPE,
    "min_decisions": MIN_DECISIONS,
    "frozen": "constants above were written before the first run; the gate refuses a face that echoes others",
}
VERDICTS = ("BROAD", "CONCENTRATED", "INSUFFICIENT")


# --------------------------------------------------------------------------- core
def held_path(dates, diag, n_hold=N_HOLD):
    """Weights per bar, taken from the engine's own decision rows (never re-derived)."""
    by_date = {pd.Timestamp(row["date"]): row for row in diag}
    held = {}
    path = []
    for i in range(len(dates) - 1):
        d = dates[i]
        row = by_date.get(d) if i % REBAL == 0 else None
        if row is not None:
            scale = float(row["scale"])
            held = {p: scale / n_hold for p in row["book"]}
        path.append((d, dict(held)))
    return path


def replay(close, openp, amt, score, diag, n_hold=N_HOLD, cost=COST):
    """Replay the engine's P&L with its own weights, split by symbol.

    Returns (equity Series, per-symbol contributions, per-decision turnovers, gross sum).
    `contrib` sums to the GROSS return sum, not to the net curve: the curve also carries the
    fee drag charged at each decision. Both are published, and the caller MUST check
    `equity` against the engine's own curve before anything is quoted.
    """
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp("2020-01-01")]
    path = held_path(dates, diag, n_hold)
    equity, out, turns = 1.0, [], []
    contrib = {}
    gross = 0.0
    prev = {}
    for i, (d, held) in enumerate(path):
        nxt = dates[i + 1]
        if held != prev:
            turn = sum(abs(held.get(k, 0.0) - prev.get(k, 0.0)) for k in set(held) | set(prev))
            equity *= (1.0 - cost * turn)
            turns.append(turn)
            prev = dict(held)
        r = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                rp = wt * (b / a - 1.0)
                r += rp
                contrib[p] = contrib.get(p, 0.0) + rp
        gross += r
        equity *= (1.0 + r)
        out.append((nxt, equity))
    return pd.Series(dict(out)).sort_index(), contrib, turns, gross


def exposure(diag, n_hold=N_HOLD):
    """How often each name was actually held -- the book's real universe, not the panel's."""
    cnt, first, last, wsum = {}, {}, {}, {}
    for row in diag:
        d = row["date"]
        scale = float(row["scale"])
        for p in row["book"]:
            cnt[p] = cnt.get(p, 0) + 1
            first.setdefault(p, d)
            last[p] = d
            wsum[p] = wsum.get(p, 0.0) + scale / n_hold
    rows = []
    n = len(diag) or 1
    for p, c in cnt.items():
        rows.append({"symbol": p, "decisions_held": c, "share_of_decisions": round(c / n, 4),
                     "first_held": first[p], "last_held": last[p],
                     "mean_weight_when_held": round(wsum[p] / c, 4)})
    rows.sort(key=lambda r: (-r["decisions_held"], r["symbol"]))
    return rows


def concentration(contrib, total_return_sum):
    """Share-of-return concentration. Shares are taken against the book's own return sum."""
    if not np.isfinite(total_return_sum) or total_return_sum == 0:
        return {"computable": False, "detail": "the book's return sum is zero"}
    rows = sorted(contrib.items(), key=lambda kv: -kv[1])
    share = {p: v / total_return_sum for p, v in rows}
    pos = [max(0.0, v) for _, v in rows]
    tot_pos = sum(pos) or 1.0
    hhi = sum((v / tot_pos) ** 2 for v in pos)
    out = {
        "computable": True,
        "symbols_with_any_contribution": len(rows),
        "top": [{"symbol": p, "contribution_sum": round(v, 6), "share_of_return_sum": round(share[p], 4)}
                for p, v in rows[:10]],
        "top1_share": round(share[rows[0][0]], 4) if rows else None,
        "top3_share": round(sum(share[p] for p, _ in rows[:TOP_K]), 4) if rows else None,
        "positive_contribution_hhi": round(hhi, 4),
        # all names, so a face can check it adds to 100% even when `top` is truncated
        "shares_sum_all_names": round(sum(share.values()), 6),
        "names_above_1pct_share": int(sum(1 for p, _ in rows if share[p] >= 0.01)),
        "names_negative": int(sum(1 for _, v in rows if v < 0)),
        "total_return_sum": round(float(total_return_sum), 6),
        "unit_note": ("shares are of the SUM of daily arithmetic returns, not of log growth; "
                      "they add to 100% by construction and are unit-free"),
    }
    return out


def leave_out(close, openp, amt, score, symbols, n_hold=N_HOLD):
    """Re-price the book with `symbols` removed from the universe (their score -> NaN)."""
    sc = score.copy()
    for p in symbols:
        if p not in sc.columns:
            raise KeyError("symbol %r is not in the panel -- refusing a silent no-op" % p)
        sc[p] = np.nan
    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, sc, REBAL, n_hold, COST,
                                      vol_target=VOL_TARGET, diag=diag)
    return ser, turn, diag


def _stats(ser):
    row = {}
    for lbl, sl in (("full", ser), ("is", ser[ser.index <= pd.Timestamp(P.IS_END)]),
                    ("oos", ser[ser.index > pd.Timestamp(P.IS_END)])):
        m = A.stats2(sl, lbl)
        row[lbl] = {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}
    return row


def verdict_of(base_cagr, base_sharpe, leave3, top3_share, n_decisions):
    """The published decision rule, recomputed by the gate from the face's own numbers."""
    if n_decisions < MIN_DECISIONS:
        return "INSUFFICIENT"
    shape = "CONCENTRATED" if (top3_share is not None and top3_share > TOP3_SHARE_BAND) else "BROAD"
    if base_cagr is None or base_cagr <= 0:
        return shape
    if leave3 is None:
        return shape
    ok_cagr = leave3.get("cagr") is not None and leave3["cagr"] >= EDGE_SURVIVES_CAGR_SHARE * base_cagr
    ok_sharpe = leave3.get("sharpe") is not None and leave3["sharpe"] >= EDGE_SURVIVES_SHARPE
    return shape + "|SURVIVES_WITHOUT_TOP%d" % TOP_K if (ok_cagr and ok_sharpe) \
        else shape + "|DEPENDS_ON_TOP%d" % TOP_K


# ---------------------------------------------------------------------- run
def run(out_path=None, verbose=True):
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    names = P.load_names()
    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                      vol_target=VOL_TARGET, diag=diag)
    if not diag:
        raise RuntimeError("panel too short for one decision on the grid")
    rep, contrib, turns, gross = replay(close, openp, amt, score, diag)
    common = rep.index.intersection(ser.index)
    worst = float(np.max(np.abs(rep.reindex(common) - ser.reindex(common)))) if len(common) else None
    scale = float(np.max(np.abs(ser.reindex(common)).max() or 1.0))
    if worst is None or worst / max(scale, 1e-12) > 1e-10:
        raise RuntimeError("replica does not reproduce the engine's equity (max abs %.3g of %.3g) "
                           "-- refusing to publish a contribution split of its own arithmetic"
                           % (worst, scale))
    # shares are of the GROSS return sum (what the picks earned); the fee drag is published
    # beside it, because the net curve is gross minus the toll, not gross itself.
    total = float(sum(contrib.values()))
    toll = float(sum(turns) * COST)   # arithmetic sum of the fee drag charged at decisions
    conc = concentration(contrib, gross)
    expo = exposure(diag)
    base = _stats(ser)

    # control: masking a name the book never held must not move a single number
    held_names = {r["symbol"] for r in expo}
    never = [c for c in close.columns if c not in held_names]
    control = None
    if never:
        cser, _, _ = leave_out(close, openp, amt, score, [never[0]])
        cc = cser.index.intersection(ser.index)
        diff = float(np.max(np.abs(cser.reindex(cc) - ser.reindex(cc))))
        control = {"symbol": never[0], "max_abs_diff": diff,
                   "inert": bool(diff < 1e-12),
                   "detail": "masking a name the book never held must be bit-identical"}

    topk = [r["symbol"] for r in (conc.get("top") or [])[:TOP_K]]
    base_cagr = (base["full"] or {}).get("cagr")
    base_sharpe = (base["full"] or {}).get("sharpe")
    legs = {}
    for p in topk:
        ser_p, turn_p, diag_p = leave_out(close, openp, amt, score, [p])
        legs[p] = {"solo": _stats(ser_p), "turnover": round(turn_p, 3),
                   "book_changed": [sorted(r["book"]) for r in diag_p[-1:]] != [sorted(diag[-1]["book"])]
                   if diag_p else None}
    ser_k, turn_k, diag_k = leave_out(close, openp, amt, score, topk) if topk else (ser, turn, diag)
    leave_k = _stats(ser_k)

    # The leave-top-k arm can be flattered by substitution inside the same class: the top
    # names here are four gold ETFs, so dropping three of them leaves the fourth in the
    # slot. The class arm removes the whole sleeve, which is the question an allocator
    # actually asks ("if gold stops working, what is left?"). Disclosed, not a verdict input.
    class_arm = None
    if topk:
        top_class = str(cls.get(topk[0])) if hasattr(cls, "get") else None
        if top_class:
            c_syms = [c for c in close.columns if str(cls.get(c)) == top_class]
            if c_syms:
                ser_c, turn_c, diag_c = leave_out(close, openp, amt, score, c_syms)
                cs = _stats(ser_c)
                class_arm = {
                    "class": top_class,
                    "symbols_removed": len(c_syms),
                    "contains_top_k": set(topk) <= set(c_syms),
                    "stats": cs,
                    "turnover": round(turn_c, 3),
                    "delta_cagr_pp": round(100 * ((cs["full"] or {}).get("cagr", 0) - base_cagr), 3),
                    "delta_sharpe": round(((cs["full"] or {}).get("sharpe") or 0) - (base_sharpe or 0), 3),
                    "detail": ("removing the whole %s sleeve (%d ETFs); a top-k leave-out of names "
                               "that share a class is partly a redundancy test, not a sleeve test"
                               % (top_class, len(c_syms))),
                }

    verdict = verdict_of(base_cagr, base_sharpe, leave_k.get("full"), conc.get("top3_share"),
                         len(diag))
    deltas = {}
    for p, row in legs.items():
        deltas[p] = {
            "cagr_pp": round(100 * ((row["solo"]["full"] or {}).get("cagr", 0) - base_cagr), 3),
            "sharpe": (row["solo"]["full"] or {}).get("sharpe"),
            "maxdd": (row["solo"]["full"] or {}).get("maxdd"),
        }

    payload = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "script": SCRIPT,
        "face": FACE,
        "evidence_cutoff": str(close.index[-1].date()),
        "criteria": CRITERIA,
        "execution": "decide at close t -> fill at open t+1 -> hold to next decision",
        "panel": {"columns": int(close.shape[1]), "bars": int(close.shape[0]),
                  "flips_repaired": n_flip,
                  "digest": (P.PANEL_DIGEST or {}).get("digest")},
        "book": {"n_hold": N_HOLD, "rebal": REBAL, "vol_target": VOL_TARGET,
                 "cost_bp_per_side": COST * 1e4, "decisions": len(diag),
                 "turnover_per_decision": round(turn, 3)},
        "identity": {"replica_vs_engine_max_abs": worst,
                     "bars_compared": int(len(common)),
                     "passes": True},
        "return_sum": {"gross": round(float(gross), 6),
                       "sum_of_symbol_contributions": round(total, 6),
                       "fee_toll": round(toll, 6),
                       "unit_note": ("gross and contributions are sums of daily arithmetic "
                                     "returns; the net curve = compounded gross minus the fee "
                                     "charged at each decision, and is what `baseline` quotes")},
        "baseline": base,
        "concentration": conc,
        "exposure": {"distinct_names_held": len(expo), "top": expo[:12]},
        "control": control,
        "leave_one_out": {p: {"solo": v["solo"], "turnover": v["turnover"],
                              "delta_vs_base": deltas[p]} for p, v in legs.items()},
        "leave_top_k_out": {"k": TOP_K, "symbols": topk, "stats": leave_k,
                            "turnover": round(turn_k, 3),
                            "delta_cagr_pp": round(100 * ((leave_k["full"] or {}).get("cagr", 0) - base_cagr), 3),
                            "delta_sharpe": round(((leave_k["full"] or {}).get("sharpe") or 0) - (base_sharpe or 0), 3)},
        "leave_class_out": class_arm,
        "verdict": verdict,
        "names": {p: names.get(p, "") for p in topk},
    }
    if verbose:
        print("baseline", base["full"])
        print("top3 share of return sum", conc.get("top3_share"),
              "| top1", conc.get("top1_share"), "| hhi", conc.get("positive_contribution_hhi"))
        print("top names", [(t["symbol"], names.get(t["symbol"], ""), t["share_of_return_sum"])
                            for t in (conc.get("top") or [])[:5]])
        print("leave top%d out" % TOP_K, leave_k["full"], "delta_cagr_pp",
              payload["leave_top_k_out"]["delta_cagr_pp"])
        if class_arm:
            print("leave the whole %s sleeve out (%d ETFs)" % (class_arm["class"],
                                                               class_arm["symbols_removed"]),
                  class_arm["stats"]["full"], "delta_cagr_pp", class_arm["delta_cagr_pp"])
        print("control inert:", (control or {}).get("inert"))
        print("verdict", verdict)
    p = Path(out_path) if out_path else OUT_JSON
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    if verbose:
        print("saved", p)
    return payload


# ---------------------------------------------------------------------- reader
def sentence(doc):
    """The one line a human reads, formatted from the face's own numbers (never a literal).

    Missing input is "unpublished", never "not concentrated": a reader that cannot see the
    face must not imply a reading of zero (E281 class).
    """
    conc = doc.get("concentration") or {}
    if not conc.get("computable"):
        return None
    top = conc.get("top") or []
    if not top:
        return None
    names = doc.get("names") or {}
    lead = names.get(top[0].get("symbol")) or top[0].get("symbol")
    veh = doc.get("leave_class_out") or {}
    parts = ["前三名只占毛收益 %.1f%%（第一 %s %.1f%%）"
             % (100 * (conc.get("top3_share") or 0), lead, 100 * (top[0]["share_of_return_sum"] or 0))]
    lk = doc.get("leave_top_k_out") or {}
    if lk.get("delta_cagr_pp") is not None:
        parts.append("删掉这三只年化 %+.2fpp" % lk["delta_cagr_pp"])
    if veh.get("delta_cagr_pp") is not None:
        parts.append("删掉整条 %s 袖（%d 只）年化 %+.2fpp、回撤 %+.1fpp"
                     % (veh.get("class"), veh.get("symbols_removed"), veh["delta_cagr_pp"],
                        100 * (((veh.get("stats") or {}).get("full") or {}).get("maxdd", 0)
                               - ((doc.get("baseline") or {}).get("full") or {}).get("maxdd", 0))))
    return "；".join(parts) + "（判 %s）" % (doc.get("verdict") or "?")


def read_published(path=None):
    """Consumer entry point: {status, sentence, evidence_cutoff, verdict} or an honest gap."""
    p = Path(path) if path else OUT_JSON
    if not p.exists():
        return {"status": "absent", "sentence": None, "evidence_cutoff": None, "verdict": None}
    try:
        doc = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        return {"status": "unreadable: %s" % e, "sentence": None,
                "evidence_cutoff": None, "verdict": None}
    if not (doc.get("identity") or {}).get("passes"):
        return {"status": "no_identity", "sentence": None, "evidence_cutoff": None,
                "verdict": doc.get("verdict")}
    s = sentence(doc)
    if not s:
        return {"status": "no_reading", "sentence": None,
                "evidence_cutoff": doc.get("evidence_cutoff"), "verdict": doc.get("verdict")}
    return {"status": "ok", "sentence": s, "evidence_cutoff": doc.get("evidence_cutoff"),
            "verdict": doc.get("verdict")}


# ---------------------------------------------------------------------- check
def check(path=None):
    """Re-read the published face and recompute the verdict from its own rows."""
    p = Path(path) if path else OUT_JSON
    data = json.load(open(p, encoding="utf-8"))
    problems = []
    crit = data.get("criteria") or {}
    for k, v in CRITERIA.items():
        if crit.get(k) != v:
            problems.append("criteria %s: face says %r, code says %r" % (k, crit.get(k), v))
    if not (data.get("identity") or {}).get("passes"):
        problems.append("identity leg missing or not passing")
    conc = data.get("concentration") or {}
    top = conc.get("top") or []
    if conc.get("computable") and top:
        if abs(top[0]["share_of_return_sum"] - (conc.get("top1_share") or 0)) > 1e-6:
            problems.append("top1_share does not match the top row")
        t3 = sum(t["share_of_return_sum"] for t in top[:TOP_K])
        if abs(t3 - (conc.get("top3_share") or 0)) > 1e-3:
            problems.append("top3_share %.4f does not equal the sum of the top-%d rows %.4f"
                            % (conc.get("top3_share") or 0, TOP_K, t3))
    base = ((data.get("baseline") or {}).get("full") or {})
    leave = ((data.get("leave_top_k_out") or {}).get("stats") or {}).get("full") or {}
    want = verdict_of(base.get("cagr"), base.get("sharpe"), leave,
                      conc.get("top3_share"), (data.get("book") or {}).get("decisions") or 0)
    if want != data.get("verdict"):
        problems.append("verdict %r does not reproduce from the rows (%r)" % (data.get("verdict"), want))
    ctrl = data.get("control") or {}
    if ctrl and not ctrl.get("inert"):
        problems.append("control arm moved the book: %r" % (ctrl,))
    for msg in problems:
        print("CHECK FAIL:", msg)
    if not problems:
        print("CHECK OK: criteria echoed, identity exact (%.2g), control inert, verdict %s "
              "reproduces from the published rows" % (((data.get("identity") or {}).get(
                  "replica_vs_engine_max_abs") or 0.0), data.get("verdict")))
    return 1 if problems else 0


# -------------------------------------------------------------------- selftest
def _fixture(n=260, k=8, seed=11, rebal=REBAL, drift=None):
    """A synthetic panel shaped like the real one: close/openp/amt/score."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    cols = ["s%02d" % i for i in range(k)]
    drift = drift or {c: 0.0002 for c in cols}
    px = {}
    for c in cols:
        r = rng.normal(drift[c], 0.008, n)
        px[c] = 1.0 * np.cumprod(1.0 + r)
    close = pd.DataFrame(px, index=idx)
    openp = close.shift(1).bfill()
    amt = pd.DataFrame(1e9, index=idx, columns=cols)
    score = pd.DataFrame(rng.normal(0, 1, (n, k)), index=idx, columns=cols)
    return close, openp, amt, score


def selftest():
    ok = []

    def leg(name, cond, detail=""):
        ok.append((name, bool(cond), detail))
        print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

    close, openp, amt, score = _fixture(k=12)
    sc = score.copy()
    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, sc, REBAL, 4, COST, diag=diag)

    # L1 identity: the replica must be the engine, not a lookalike
    rep, contrib, turns, gross = replay(close, openp, amt, sc, diag, n_hold=4)
    common = rep.index.intersection(ser.index)
    worst = float(np.max(np.abs(rep.reindex(common) - ser.reindex(common)))) if len(common) else None
    leg("replica reproduces the engine's equity bit for bit",
        worst is not None and worst < 1e-12, "max abs diff %s over %d bars" % (worst, len(common)))

    # L2 the split adds up to the GROSS return sum the book actually earned
    total = float(sum(contrib.values()))
    leg("per-symbol contributions sum to the book's gross return sum",
        abs(total - gross) < 1e-10, "split %.12f vs replay %.12f" % (total, gross))

    # L3 concentration shares add to 100% (unit-free, of the gross sum)
    conc = concentration(contrib, gross)
    leg("shares of the gross return sum add to 100% over ALL names",
        conc.get("computable") and abs((conc.get("shares_sum_all_names") or 0) - 1.0) < 1e-6,
        "top1 %.3f, all-name shares sum %.6f (negative contributors make the truncated top "
        "rows sum past 1)" % (conc.get("top1_share") or 0, conc.get("shares_sum_all_names") or 0))

    # L4 control: masking a name the book never held changes nothing
    expo = exposure(diag, n_hold=4)
    held = {r["symbol"] for r in expo}
    never = [c for c in close.columns if c not in held]
    leg("a fixture that never holds some name exists for the control", bool(never))
    if never:
        cs, _, _ = leave_out(close, openp, amt, sc, [never[0]], n_hold=4)
        cc = cs.index.intersection(ser.index)
        d = float(np.max(np.abs(cs.reindex(cc) - ser.reindex(cc))))
        leg("control: masking a never-held name is bit-identical", d < 1e-12, "max abs %.2g" % d)

    # L5 masking a held name really changes the book (the leave-out is not a no-op)
    if held:
        hs, _, hd = leave_out(close, openp, amt, sc, [sorted(held)[0]], n_hold=4)
        leg("masking a held name changes the decision stream (substitution is disclosed)",
            bool(hd) and [sorted(r["book"]) for r in hd] != [sorted(r["book"]) for r in diag],
            "%d decisions after, %d before" % (len(hd), len(diag)))

    # L6 a blanked column is not a silent no-op: an unknown symbol raises
    try:
        leave_out(close, openp, amt, sc, ["nope"])
        raised = False
    except KeyError:
        raised = True
    leg("leaving out a symbol that is not in the panel raises instead of silently no-oping", raised)

    # L7 verdict: concentrated fixture -> CONCENTRATED, broad fixture -> BROAD
    conc_c = concentration({"a": 0.9, "b": 0.05, "c": 0.05}, 1.0)
    conc_b = concentration({("s%d" % i): 0.1 for i in range(10)}, 1.0)
    leg("a 90%-in-one-name book reads CONCENTRATED, a 10-name book reads BROAD",
        conc_c["top3_share"] > TOP3_SHARE_BAND and conc_b["top3_share"] <= TOP3_SHARE_BAND,
        "concentrated %.2f broad %.2f" % (conc_c["top3_share"], conc_b["top3_share"]))
    leg("verdict survives when the leave-out keeps the edge, depends when it does not",
        verdict_of(0.09, 0.9, {"cagr": 0.08, "sharpe": 0.8}, 0.4, 50).endswith("SURVIVES_WITHOUT_TOP3")
        and verdict_of(0.09, 0.9, {"cagr": 0.01, "sharpe": 0.2}, 0.7, 50).endswith("DEPENDS_ON_TOP3"),
        verdict_of(0.09, 0.9, {"cagr": 0.08, "sharpe": 0.8}, 0.4, 50))

    # L8 too few decisions -> INSUFFICIENT, never a number pretending to be a judgement
    leg("under the decision floor the verdict is INSUFFICIENT",
        verdict_of(0.09, 0.9, {"cagr": 0.08, "sharpe": 0.8}, 0.4, MIN_DECISIONS - 1) == "INSUFFICIENT")

    # L9 exposure census counts decision-days, not bars
    if expo:
        s = sum(r["decisions_held"] for r in expo)
        leg("exposure counts decision-days (each decision holds exactly n_hold names)",
            s == len(diag) * 4, "sum %d vs %d decisions x 4" % (s, len(diag)))

    # L10 the gate recomputes the verdict from the rows and refuses a doctored one
    payload = {"criteria": dict(CRITERIA), "identity": {"passes": True},
               "concentration": {"computable": True, "top1_share": 0.4, "top3_share": 0.7,
                                 "top": [{"symbol": "s1", "share_of_return_sum": 0.4},
                                         {"symbol": "s2", "share_of_return_sum": 0.2},
                                         {"symbol": "s3", "share_of_return_sum": 0.1}]},
               "baseline": {"full": {"cagr": 0.09, "sharpe": 0.9}},
               "leave_top_k_out": {"stats": {"full": {"cagr": 0.02, "sharpe": 0.3}}},
               "book": {"decisions": 50},
               "control": {"inert": True},
               "verdict": verdict_of(0.09, 0.9, {"cagr": 0.02, "sharpe": 0.3}, 0.7, 50)}
    bad = json.loads(json.dumps(payload))
    bad["criteria"]["top3_share_band"] = 0.99
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        good_p = Path(td) / "good.json"
        bad_p = Path(td) / "bad.json"
        json.dump(payload, open(good_p, "w", encoding="utf-8"))
        json.dump(bad, open(bad_p, "w", encoding="utf-8"))
        rc_good = check(good_p)
        rc_bad = check(bad_p)
    leg("gate accepts a faithful face and rejects one that moved a frozen criterion",
        rc_good == 0 and rc_bad == 1, "good rc=%d bad rc=%d" % (rc_good, rc_bad))

    # L11 the reader: a missing face is "absent" (never a reading of zero), and a present
    # face yields a sentence built from its own numbers
    with tempfile.TemporaryDirectory() as td:
        miss = read_published(Path(td) / "nope.json")
        doc_p = Path(td) / "face.json"
        json.dump(payload, open(doc_p, "w", encoding="utf-8"))
        pres = read_published(doc_p)
    leg("reader: absent face reads 'absent', present face quotes its own numbers",
        miss["status"] == "absent" and miss["sentence"] is None
        and pres["status"] == "ok" and "22.0%" not in (pres["sentence"] or "")
        and ("70.0%" in (pres["sentence"] or "")) and ("DEPENDS_ON_TOP3" in (pres["sentence"] or "")),
        "absent=%s present=%r" % (miss["status"], (pres["sentence"] or "")[:80]))

    n_pass = sum(1 for _, c, _ in ok if c)
    print("\nselftest: %d/%d PASS" % (n_pass, len(ok)))
    return 0 if n_pass == len(ok) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check or a.cmd == "check":
        return check(a.out)
    run(a.out)
    return check(a.out)


if __name__ == "__main__":
    sys.exit(main())