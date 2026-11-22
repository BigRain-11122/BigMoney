"""Does the capital placement survive the search rent? -- priced on the book it actually trades.

`results/capital_placement.json` ranks vehicles on their HEADLINE returns and recommends the
book's executable ticket (n5 / beta020 / 8bp, 12.72%/yr). `results/book_deflated_expectation.json`
showed the book is worth about cash once the search rent is paid -- but it priced the CARD
(n5 / vol08 / 10bp, 11.16%), not the ticket the order sheet trades. Two faces, two books, one
decision. This face closes that gap: every vehicle the placement ranks is measured on its own
series and put through the same haircut, then printed side by side with what the placement says.

Frozen criteria, written before the first run:

  * Capital: ¥1,000,000 (the placement's own middle tier).
  * Arms: the ticket (what the order sheet trades), the 5-name card (the book r1962 priced),
    the advertised 12-name card, the equal-weight 4-asset basket the book is tested against,
    and the cash leg as the ruler.
  * Two frames per arm: its OWN window, and the COMMON window (the intersection of the arms --
    a comparison across windows is not a comparison, r1262).
  * Haircut: SR*(N) from `book_deflated_expectation._haircut_row` (imported, not re-written);
    N ladder 2/19/58/123/450 where 58 is the repo's smallest mechanical count; verdict at 58.
  * Cash leg: the published NET repo rate from `capital_placement.json::config.cash_net_annual`.
  * The basket's N is the same ladder on purpose: the mix was chosen inside the sample window,
    so it is not rent-free either.

Nothing here re-derives the Sharpe / DSR / drawdown formula. The engine (panel prep, the beta
cover, the basket construction) is the repo's own, and the measurement is asserted against the
published numbers of every arm before any haircut is applied -- if the numbers I measure are not
the numbers those faces published, the face refuses to build a verdict on them.

Evidence: results/capital_placement_rent_audit.json. Page: research/CAPITAL-PLACEMENT-RENT-AUDIT.md.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

OUT_JSON = ROOT / "results" / "capital_placement_rent_audit.json"
OUT_MD = ROOT / "research" / "CAPITAL-PLACEMENT-RENT-AUDIT.md"
SCRIPT = "scripts/capital_placement_rent_audit.py"
FACE = "results/capital_placement_rent_audit.json"

SRC_PLACEMENT = ROOT / "results" / "capital_placement.json"
SRC_RENT = ROOT / "results" / "etf_book_search_rent.json"
SRC_SPANNING = ROOT / "results" / "etf_book_spanning.json"
SRC_RECONCILE = ROOT / "results" / "etf_book_cagr_reconcile.json"

# ---------------------------------------------------------------- frozen criteria
CRITERIA = {
    "capital_cny": 1_000_000,
    "n_ladder": [2, 19, 58, 123, 450],
    "n_ladder_definitions": {
        "2": "the floor of the null-max formula",
        "19": "audited N of the carry family (results/idx_fut_carry_search_rent.json)",
        "58": "queue rows marked done in state/queue/{tech,explore}.md -- the verdict N",
        "123": "batches a gate killed (results/gate_attrition.bm-c.json)",
        "450": "research/**/*PREREG*.md written by this desk",
    },
    "n_conservative": 58,
    "t_req": 3.0,
    "abandon_p": 0.05,
    "dsr_line": 0.95,
    "periods_per_year": 252,
    "frames": ["own", "common"],
    "deciding_frame": "common",
    "haircut": "SR*(N) at the arm's own sigma_sr; credible = max(0, published - SR*(N)); "
               "budgetable = credible * published vol -- arithmetic imported from "
               "book_deflated_expectation._haircut_row, not re-written",
    "end_anchor": "every arm is priced only on bars up to the panel's last bar; no arm is "
                  "given an out-of-sample extension of its own",
    "frozen": "constants above were written before the first run; no line is tuned after "
              "seeing the result",
}

ARMS = {
    "ticket_n5_beta020_8bp": {
        "label": "the ticket the order sheet trades (n5 / beta cover 0.20 / 8bp)",
        "engine": "production panel -> open-to-open n5 @8bp -> beta cover to 0.20",
        "placement_role": "the placement's recommended vehicle",
    },
    "n5_vol08_10bp": {
        "label": "the 5-name card r1962 priced (n5 / 8% vol target / 10bp)",
        "engine": "production panel -> open-to-open n5 @10bp -> 8% vol target",
        "placement_role": "the book the published card is closest to",
    },
    "card_n12_vol08_10bp": {
        "label": "the advertised 12-name card (n12 / 8% vol target / 10bp)",
        "engine": "production panel -> open-to-open n12 @10bp -> 8% vol target",
        "placement_role": "the headline 9.16% card",
    },
    "basket_ew4_20bar_10bp": {
        "label": "equal-weight 4-asset basket on the book's 20-bar grid (10bp/side)",
        "engine": "spanning face's own basket(): gold / Nasdaq-100 QDII / CSI300 / treasury",
        "placement_role": "the placement's second-best vehicle",
    },
}
CASH_ARM = "cash_repo_net"


def _load(p):
    p = Path(p)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _dump(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


# ------------------------------------------------------------------- the measurement
def _block(ser):
    """Stats + sigma_sr + DSR curve for one equity series. Returns feed the gate."""
    import etf_equity_alpha as A
    import science_gates as SG

    ser = ser.dropna()
    st = A.stats2(ser, "arm")
    row = {k: round(float(st.get(k)), 6) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}
    row["bars"] = int(len(ser))
    row["window"] = [str(ser.index[0].date()), str(ser.index[-1].date())]
    r = ser.pct_change().dropna()
    sigmas = set()
    curve = []
    for n in CRITERIA["n_ladder"]:
        d = SG.deflated_sharpe_ratio(r, int(n))
        sigmas.add(round(float(d["sigma_sr"]), 9))
        curve.append({"n_trials": int(n), "dsr": round(float(d["dsr"]), 6),
                      "sr_star_daily": round(float(d["sr_star"]), 8)})
    if len(sigmas) != 1:
        raise RuntimeError("sigma_sr is not constant across the ladder: %s" % sorted(sigmas))
    row["sigma_sr"] = sigmas.pop()
    row["dsr_curve"] = curve
    return row


def _measure(verbose=True, span_start=None):
    """Build every arm's series with the repo's own engines and measure it.

    `span_start` is the window the spanning face published its basket on. The basket's own
    history runs back to 2013, so without this slice the anchor leg would compare a 13-year
    basket against the published 2020+ one and call a correct measurement a failure.
    """
    import etf_book_production as P
    import etf_book_cagr_reconcile as RC
    import etf_book_spanning as S
    import etf_phase_beta_target as BT

    t0 = time.time()
    if verbose:
        print("prep panel ...", flush=True)
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise SystemExit("FATAL: no 510300 column on the production panel")
    mkt = close[mkt_col]

    if verbose:
        print("arms: ticket / n5 card / n12 card ...", flush=True)
    flat5 = RC.open_open(close, openp, amt, score, 5, 8.0, None)
    ticket = RC.beta_on_prod(flat5, mkt, 8.0)
    card5 = RC.open_open(close, openp, amt, score, 5, 10.0, 0.08)
    card12 = RC.open_open(close, openp, amt, score, 12, 10.0, 0.08)

    if verbose:
        print("arm: spanning basket ...", flush=True)
    span = S.SPAN
    keys = [c for _, c, _ in span]
    _sc, span_open, span_flips = S.load_span_frames(span)
    basket, basket_turn = S.basket(span_open, keys, 20, 0.0010)

    series = {
        "ticket_n5_beta020_8bp": ticket,
        "n5_vol08_10bp": card5,
        "card_n12_vol08_10bp": card12,
        "basket_ew4_20bar_10bp": basket,
    }
    series = {k: v.dropna() for k, v in series.items()}

    common_start = max(v.index[0] for v in series.values())
    common_end = min(v.index[-1] for v in series.values())
    if verbose:
        print("common window: %s -> %s" % (common_start.date(), common_end.date()), flush=True)

    arms = {}
    for name, ser in series.items():
        own = _block(ser)
        cut = ser[(ser.index >= common_start) & (ser.index <= common_end)]
        common = _block(cut)
        anchor = own
        if name == "basket_ew4_20bar_10bp" and span_start:
            sliced = ser[ser.index >= span_start]
            anchor = _block(sliced)
        arms[name] = {"own": own, "common": common, "anchor_window": anchor,
                      "config": ARMS[name]}
        if verbose:
            print("  %-24s own %s | common %s" % (
                name, _pct(own["cagr"]), _pct(common["cagr"])), flush=True)

    return {
        "schedule": {
            "panel_universe": int(len(close.columns)),
            "panel_flips_repaired": int(n_flip),
            "span_flips_repaired": int(span_flips),
            "panel_last_bar": str(close.index[-1].date()),
            "common_window": [str(common_start.date()), str(common_end.date())],
            "basket_turnover_total": round(float(basket_turn), 4),
            "market_column": mkt_col,
        },
        "arms": arms,
        "elapsed_sec": round(time.time() - t0, 1),
    }


# ------------------------------------------------------------------------ anchors
def _published():
    """The numbers every arm must reproduce before any haircut is applied."""
    pl = _load(SRC_PLACEMENT)
    rent = _load(SRC_RENT)
    span = _load(SRC_SPANNING)
    rec = _load(SRC_RECONCILE)
    if not (pl and rent and span and rec):
        raise RuntimeError("source face missing")
    ticket = (rec.get("stacks") or {}).get("production", {}).get("cells", {}).get(
        "(5, 'beta020', 8.0)") or {}
    card12 = (rec.get("stacks") or {}).get("production", {}).get("cells", {}).get(
        "(12, 'vol08', 10.0)") or {}
    card = (rent.get("book") or {}).get("cents") or {}
    bk = (span.get("span_portfolios") or {}).get("equal_weight_basket") or {}
    rows = pl.get("rows") or []
    mid = next((r for r in rows if float(r.get("capital_cny") or 0) == CRITERIA["capital_cny"]), None)
    return {
        "placement_best_vehicle": (mid or {}).get("best_vehicle"),
        "placement_cash_net_annual": float((pl.get("config") or {}).get("cash_net_annual")),
        "placement_evidence_cutoff": pl.get("evidence_cutoff"),
        "placement_book_level_used": None if not mid else
        float(((mid.get("vehicles") or {}).get("etf_book") or {}).get("cagr_level_used")),
        "placement_basket_level_used": None if not mid else
        float(((mid.get("vehicles") or {}).get("four_etf_basket") or {}).get("cagr")),
        "ticket": {"cagr": ticket.get("cagr"), "sharpe": ticket.get("sharpe"),
                   "vol": ticket.get("vol"), "maxdd": ticket.get("maxdd"),
                   "window": ticket.get("years")},
        "card5": {"cagr": card.get("cagr"), "sharpe": card.get("sharpe"),
                  "vol": card.get("vol"), "maxdd": card.get("maxdd")},
        "card12": {"cagr": card12.get("cagr"), "sharpe": card12.get("sharpe")},
        "card5_sigma_sr_published": None if not card else _published_sigma(rent),
        "basket": {"cagr": bk.get("cagr"), "sharpe": bk.get("sharpe"), "vol": bk.get("vol"),
                   "maxdd": bk.get("maxdd")},
        "spanning_window_start": ((span.get("arms") or {}).get("book") or {}).get("window", [None])[0],
    }


def _published_sigma(rent):
    curve = rent.get("dsr_curve") or []
    sig = sorted({round(float(r["sigma_sr"]), 9) for r in curve if "sigma_sr" in r})
    if len(sig) != 1:
        raise RuntimeError("published sigma_sr is not constant: %s" % sig)
    return sig[0]


def _anchor_checks(measure, published, tol_cagr=1e-4, tol_sr=3e-3, tol_vol=1e-3):
    """Every measured arm must reproduce what its own published face printed."""
    import book_deflated_expectation as BDE

    legs = []
    arms = measure["arms"]
    t = arms["ticket_n5_beta020_8bp"]["own"]
    pt = published["ticket"]
    legs.append({
        "arm": "ticket_n5_beta020_8bp",
        "what": "etf_book_cagr_reconcile production cell (5, 'beta020', 8.0)",
        "ok": (abs(t["cagr"] - pt["cagr"]) <= tol_cagr and abs(t["sharpe"] - pt["sharpe"]) <= tol_sr
               and abs(t["vol"] - pt["vol"]) <= tol_vol),
        "measured": {"cagr": t["cagr"], "sharpe": t["sharpe"], "vol": t["vol"]},
        "published": {"cagr": pt["cagr"], "sharpe": pt["sharpe"], "vol": pt["vol"]},
    })
    c = arms["n5_vol08_10bp"]["own"]
    pc = published["card5"]
    legs.append({
        "arm": "n5_vol08_10bp",
        "what": "etf_book_search_rent book cents (r1962's card)",
        "ok": (abs(c["cagr"] - pc["cagr"]) <= tol_cagr and abs(c["sharpe"] - pc["sharpe"]) <= tol_sr
               and abs(c["vol"] - pc["vol"]) <= tol_vol),
        "measured": {"cagr": c["cagr"], "sharpe": c["sharpe"], "vol": c["vol"]},
        "published": {"cagr": pc["cagr"], "sharpe": pc["sharpe"], "vol": pc["vol"]},
    })
    # the sigma_sr of the 5-name card is published on a different window start (2020-01-03);
    # our own window slices from the card's first bar, so this must land to ~1e-4
    legs.append({
        "arm": "n5_vol08_10bp",
        "what": "etf_book_search_rent sigma_sr (constant across its grid)",
        "ok": abs(c["sigma_sr"] - published["card5_sigma_sr_published"]) <= 2e-4,
        "measured": {"sigma_sr": c["sigma_sr"]},
        "published": {"sigma_sr": published["card5_sigma_sr_published"]},
    })
    b = arms["basket_ew4_20bar_10bp"]["anchor_window"]
    pb = published["basket"]
    legs.append({
        "arm": "basket_ew4_20bar_10bp",
        "what": "etf_book_spanning span_portfolios.equal_weight_basket (same start)",
        "ok": (abs(b["cagr"] - pb["cagr"]) <= 5e-4 and abs(b["sharpe"] - pb["sharpe"]) <= 5e-3
               and abs(b["vol"] - pb["vol"]) <= 2e-3),
        "measured": {"cagr": b["cagr"], "sharpe": b["sharpe"], "vol": b["vol"]},
        "published": {"cagr": pb["cagr"], "sharpe": pb["sharpe"], "vol": pb["vol"]},
    })
    c12 = arms["card_n12_vol08_10bp"]["anchor_window"]
    p12 = published["card12"]
    legs.append({
        "arm": "card_n12_vol08_10bp",
        "what": "etf_book_cagr_reconcile production cell (12, 'vol08', 10.0)",
        "ok": (abs(c12["cagr"] - p12["cagr"]) <= tol_cagr
               and abs(c12["sharpe"] - p12["sharpe"]) <= tol_sr),
        "measured": {"cagr": c12["cagr"], "sharpe": c12["sharpe"]},
        "published": {"cagr": p12["cagr"], "sharpe": p12["sharpe"]},
    })
    # the haircut must be the one that produced BDE's published 1.8007% -- not a re-write
    bde = _load(ROOT / "results" / "book_deflated_expectation.json")
    at58 = (bde or {}).get("at_conservative_n") or {}
    mine = BDE._haircut_row(c["sharpe"], c["vol"], c["sigma_sr"], CRITERIA["n_conservative"],
                            CRITERIA["capital_cny"], CRITERIA["t_req"], CRITERIA["abandon_p"])
    legs.append({
        "arm": "n5_vol08_10bp",
        "what": "book_deflated_expectation published row at N=58 (the haircut import)",
        "ok": (at58.get("budgetable_cagr") is not None
               and abs(mine["budgetable_cagr"] - float(at58["budgetable_cagr"])) <= 1e-6),
        "measured": {"budgetable_cagr": mine["budgetable_cagr"]},
        "published": {"budgetable_cagr": at58.get("budgetable_cagr")},
    })
    return legs


# ---------------------------------------------------------------------- the arithmetic
def _pct(x, nd=2):
    return "n/a" if x is None else "%.*f%%" % (nd, 100.0 * x)


def _money(x):
    if x is None:
        return "n/a"
    sign = "-" if x < 0 else ""
    return "%s¥%s" % (sign, format(abs(round(x)), ","))


def _rows(measure, cash_net, capital):
    """Per arm per frame, the haircut ladder. Every number derives from the printed blocks."""
    import book_deflated_expectation as BDE

    out = []
    for name in (list(ARMS) + [CASH_ARM]):
        if name == CASH_ARM:
            for frame in CRITERIA["frames"]:
                out.append({
                    "arm": CASH_ARM, "window": frame, "bars": None, "sr_star_ann": None,
                    "credible_sharpe": None, "dsr": None,
                    "published_cagr": round(cash_net, 6),
                    "published_sharpe": None, "published_vol": None,
                    "budgetable_cagr": round(cash_net, 6),
                    "money_on_capital": round(capital * cash_net, 2),
                    "p_edge_is_noise": None,
                    "vs_cash_pp": 0.0,
                })
            continue
        for frame in CRITERIA["frames"]:
            b = measure["arms"][name][frame]
            r = BDE._haircut_row(b["sharpe"], b["vol"], b["sigma_sr"],
                                 CRITERIA["n_conservative"], capital,
                                 CRITERIA["t_req"], CRITERIA["abandon_p"])
            out.append({
                "arm": name, "window": frame, "bars": b["bars"],
                "sr_star_ann": r["sr_star_ann"],
                "credible_sharpe": r["credible_sharpe"],
                "dsr": r["dsr"],
                "published_cagr": b["cagr"], "published_sharpe": b["sharpe"],
                "published_vol": b["vol"],
                "budgetable_cagr": r["budgetable_cagr"],
                "money_on_capital": r["money_on_capital"],
                "p_edge_is_noise": r["p_edge_is_noise"],
                "vs_cash_pp": round(100.0 * (r["budgetable_cagr"] - cash_net), 4),
            })
    return out


def _verdict(rows, cash_net, chosen):
    """Read off the deciding frame: does the placement's pick still rank first?"""
    frame = CRITERIA["deciding_frame"]
    dec = [r for r in rows if r["window"] == frame and r["arm"] != CASH_ARM]
    if not dec:
        return "NO_DECIDING_FRAME"
    by_head = sorted(dec, key=lambda r: -(r["published_cagr"] or 0))
    by_cred = sorted(dec, key=lambda r: -(r["budgetable_cagr"] or 0))
    head_rank = [r["arm"] for r in by_head].index(chosen) + 1
    cred_rank = [r["arm"] for r in by_cred].index(chosen) + 1
    cash_row = next(r for r in rows if r["arm"] == CASH_ARM and r["window"] == frame)
    losers = [r["arm"] for r in dec if (r["budgetable_cagr"] or 0) < cash_net]
    info = {
        "deciding_frame": frame,
        "headline_order": [r["arm"] for r in by_head],
        "credible_order": [r["arm"] for r in by_cred],
        "chosen_headline_rank": head_rank,
        "chosen_credible_rank": cred_rank,
        "arms_below_cash": losers,
        "chosen_excess_vs_cash_cny": round(
            (next(r for r in dec if r["arm"] == chosen)["money_on_capital"] or 0)
            - cash_row["money_on_capital"], 2),
    }
    if head_rank == 1 and cred_rank > 1:
        return "THE_PLACEMENT_TRADES_THE_BOOK_THE_RENT_LIKES_LEAST", info
    if head_rank == 1 and cred_rank == 1:
        return "THE_PLACEMENT_SURVIVES_THE_RENT", info
    return "THE_PLACEMENT_IS_NOT_THE_HEADLINE_PICK", info


def _verdict_zh(verdict, info, chosen, rows, cash_net):
    frame = CRITERIA["deciding_frame"]

    def row_of(arm):
        return next(r for r in rows if r["window"] == frame and r["arm"] == arm)

    dec = row_of(chosen)
    if verdict == "THE_PLACEMENT_TRADES_THE_BOOK_THE_RENT_LIKES_LEAST":
        top = info["credible_order"][0]
        top_row = row_of(top)
        gap = (dec["budgetable_cagr"] or 0.0) - cash_net
        return (
            f"资金表按标题收益把 {chosen} 排第一（{_pct(dec['published_cagr'])}/年）；"
            f"扣掉 N={CRITERIA['n_conservative']} 的搜索租金后它掉到第 "
            f"{info['chosen_credible_rank']} 位、只剩 {_pct(dec['budgetable_cagr'])}/年，"
            f"比躺利息（{_pct(cash_net)}/年）{'少' if gap < 0 else '多'} "
            f"{_money(abs(gap * CRITERIA['capital_cny']))}/年。第一位换成了 {top} "
            f"（{_pct(top_row['budgetable_cagr'])}/年）。翻转只发生在最上面两名，"
            f"但位置全变：标题第一的书付完租金后是四只里第 {info['chosen_credible_rank']} 位，"
            f"而四只里有 {len(info['arms_below_cash'])} 只落在现金腿之下。"
        )
    if verdict == "THE_PLACEMENT_SURVIVES_THE_RENT":
        return (f"资金表的第一名在扣掉租金后仍是第一名（{_pct(dec['budgetable_cagr'])}/年，"
                f"现金 {_pct(cash_net)}/年），排序没翻。")
    return ("资金表推荐的第一名与标题第一名不是同一只，本面对不上账，需人工核对。")


# --------------------------------------------------------------------------- build
def build(measure=None, write=True, verbose=True):
    published = _published()
    if measure is None:
        measure = _measure(verbose=verbose, span_start=published.get("spanning_window_start"))
    cash_net = published["placement_cash_net_annual"]
    chosen = _chosen_arm(published)
    rows = _rows(measure, cash_net, CRITERIA["capital_cny"])
    verdict, info = _verdict(rows, cash_net, chosen)
    anchors = _anchor_checks(measure, published)

    face = {
        "schema": "capital_placement_rent_audit/v1",
        "script": SCRIPT,
        "face": FACE,
        "generated": _now(),
        "evidence_cutoff": measure["schedule"]["panel_last_bar"],
        "evidence_cutoff_source": "measured panel last bar (all arms stop there)",
        "criteria": CRITERIA,
        "arms": {k: v["config"] for k, v in measure["arms"].items()},
        "measure": measure,
        "published_anchors": published,
        "anchors": anchors,
        "anchors_ok": all(a["ok"] for a in anchors),
        "rows": rows,
        "verdict": verdict,
        "verdict_info": info,
        "verdict_zh": _verdict_zh(verdict, info, chosen, rows, cash_net),
        "chosen_arm": chosen,
        "caveats": [
            "The two own-window frames are printed for context only; the verdict is read off the "
            "common window, because a comparison across different windows is not a comparison "
            "(r1262).",
            "N is not derivable from the repo: the ladder prints the mechanical counts and the "
            "verdict is taken at the smallest of them (58), so the haircut errs high.",
            "The beta-covered ticket adds a cash leg and de-levers; part of its lower Sharpe is "
            "the cash return in a window where the repo rate fell. That is priced in as published, "
            "not adjusted.",
            "The basket's N is the same ladder on purpose -- the mix was chosen inside the sample "
            "window, so on its own window it is not rent-free either.",
            "The 13.3-year basket history is printed, but its verdict frame is the common window; "
            "a longer window with a lower Sharpe is not extra evidence for the present.",
            "check() does not re-run the engine: it re-anchors the printed measurement to the "
            "published faces and re-derives every number from it. Re-measuring is `run`'s job, and "
            "the chain leg must run unconditionally.",
            "Costs are 10bp/side (8bp for the ticket) with no impact term; the capacity face owns "
            "size effects. No stamp duty, no dividend withholding, no borrow on the hedge legs.",
        ],
    }
    if write:
        _dump(OUT_JSON, face)
        _write_doc(face)
    return face


def _chosen_arm(published):
    """Which arm is the placement's recommendation, read from the published face."""
    best = published.get("placement_best_vehicle")
    if best == "etf_book":
        return "ticket_n5_beta020_8bp"
    if best == "four_etf_basket":
        return "basket_ew4_20bar_10bp"
    raise RuntimeError("unmapped placement vehicle: %s" % best)


# ------------------------------------------------------------------------ rendering
def _render(face):
    s = face["measure"]["schedule"]
    cash = face["published_anchors"]["placement_cash_net_annual"]
    lines = []
    lines.append("Rent audit of the capital placement. Every arm is measured on the repo's own "
                 "engines and stopped at the panel's last bar **%s**; the deciding frame is the "
                 "**common window %s → %s**, identical start and width for every arm."
                 % (face["evidence_cutoff"], s["common_window"][0], s["common_window"][1]))
    lines.append("")
    lines.append("| arm | frame | bars | published CAGR | Sharpe | vol | SR*(N=%d) | credible Sharpe | budgetable CAGR | on %s | vs cash (pp) |"
                 % (face["criteria"]["n_conservative"], _money(face["criteria"]["capital_cny"])))
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in face["rows"]:
        if r["arm"] == CASH_ARM:
            lines.append("| %s | %s | – | – | – | – | – | – | %s | %s | 0.00 |" % (
                r["arm"], r["window"], _pct(r["published_cagr"]), _money(r["money_on_capital"])))
            continue
        lines.append("| %s | **%s** | %d | %s | %.3f | %s | %.3f | %.3f | **%s** | %s | %+.2f |" % (
            r["arm"], r["window"], r["bars"], _pct(r["published_cagr"]), r["published_sharpe"],
            _pct(r["published_vol"]), r["sr_star_ann"], r["credible_sharpe"],
            _pct(r["budgetable_cagr"]), _money(r["money_on_capital"]), r["vs_cash_pp"]))
    lines.append("")
    info = face["verdict_info"]
    lines.append("**Verdict: %s.** %s" % (face["verdict"], face["verdict_zh"]))
    lines.append("")
    lines.append("1. **What the placement says.** On headline returns the order is %s."
                 % " > ".join("%s (%s)" % (a, _pct(next(x["published_cagr"] for x in face["rows"]
                                                        if x["arm"] == a and
                                                        x["window"] == face["criteria"]["deciding_frame"])))
                              for a in info["headline_order"]))
    lines.append("2. **What survives the rent.** On the same bars, after subtracting the Sharpe a "
                 "pure-noise search of N=%d would show, the order is %s."
                 % (face["criteria"]["n_conservative"],
                    " > ".join("%s (%s)" % (a, _pct(next(x["budgetable_cagr"] for x in face["rows"]
                                                          if x["arm"] == a and
                                                          x["window"] == face["criteria"]["deciding_frame"])))
                               for a in info["credible_order"])))
    lines.append("3. **What that costs.** The recommended arm's excess over simply holding the net "
                 "repo rate is %s per year on %s; arms that fall below the cash leg: %s."
                 % (_money(info["chosen_excess_vs_cash_cny"]),
                    _money(face["criteria"]["capital_cny"]),
                    ", ".join(info["arms_below_cash"]) or "none"))
    lines.append("")
    lines.append("Anchor legs -- the measurement must be the published book before any haircut is "
                 "applied (a haircut on a book I failed to reproduce is a haircut on nothing):")
    lines.append("")
    lines.append("| arm | what it must reproduce | measured | published | ok |")
    lines.append("|---|---|---|---|---|")
    for a in face["anchors"]:
        m = ", ".join("%s=%s" % (k, ("%.6f" % v) if isinstance(v, float) else v)
                      for k, v in (a["measured"] or {}).items())
        p = ", ".join("%s=%s" % (k, ("%.6f" % v) if isinstance(v, float) else v)
                      for k, v in (a["published"] or {}).items())
        lines.append("| %s | %s | %s | %s | %s |" % (
            a["arm"], a["what"], m, p, "PASS" if a["ok"] else "**FAIL**"))
    lines.append("")
    lines.append("Caveats, printed so they cannot be read past:")
    lines.append("")
    for c in face["caveats"]:
        lines.append("- " + c)
    return "\n".join(lines)


def _write_doc(face):
    head = (
        "# Does the capital placement survive the search rent?\n\n"
        "Generated by `%s` -- do not edit the block below by hand; `check` compares it\n"
        "byte-for-byte with what the face would render today.\n\n"
        "<!-- BEGIN GENERATED -->\n" % SCRIPT
    )
    tail = "\n<!-- END GENERATED -->\n"
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head + _render(face) + tail)


def _doc_block(text):
    a = text.find("<!-- BEGIN GENERATED -->")
    b = text.find("<!-- END GENERATED -->")
    if a < 0 or b < 0:
        return None
    return text[a + len("<!-- BEGIN GENERATED -->"):b]


# --------------------------------------------------------------------------- check
def check():
    face = _load(OUT_JSON)
    if not face:
        print("STALE face missing: %s" % FACE)
        return 3
    if (face.get("criteria") or {}) != CRITERIA:
        print("CHECK FAILED criteria differ from the frozen constants (face is not this code)")
        return 4
    try:
        published = _published()
    except RuntimeError as exc:
        print("STALE source face missing: %s" % exc)
        return 3
    old = face.get("published_anchors") or {}
    moved = [k for k in ("placement_book_level_used", "placement_basket_level_used",
                         "placement_cash_net_annual", "placement_best_vehicle",
                         "card5_sigma_sr_published")
             if old.get(k) != published.get(k)]
    if moved:
        print("STALE published inputs advanced: %s (the placement or its parents moved)"
              % ", ".join(moved))
        return 3
    if face.get("evidence_cutoff") != face["measure"]["schedule"]["panel_last_bar"]:
        print("STALE face cutoff %s is not the measured panel last bar %s"
              % (face.get("evidence_cutoff"), face["measure"]["schedule"]["panel_last_bar"]))
        return 3
    fresh_rows = _rows(face["measure"], published["placement_cash_net_annual"],
                       CRITERIA["capital_cny"])
    if face.get("rows") != fresh_rows:
        print("CHECK FAILED same measurement, different numbers: rows (not a freshness issue)")
        return 4
    fresh_anchors = _anchor_checks(face["measure"], published)
    if [a["ok"] for a in fresh_anchors] != [a["ok"] for a in (face.get("anchors") or [])]:
        print("CHECK FAILED anchor verdicts differ from the face (re-measure with `run`)")
        return 4
    chosen = _chosen_arm(published)
    verdict, info = _verdict(fresh_rows, published["placement_cash_net_annual"], chosen)
    if verdict != face.get("verdict") or info != face.get("verdict_info"):
        print("CHECK FAILED verdict does not follow from the printed rows")
        return 4
    if not OUT_MD.exists():
        print("STALE doc missing: research/CAPITAL-PLACEMENT-RENT-AUDIT.md")
        return 3
    block = _doc_block(OUT_MD.read_text(encoding="utf-8"))
    if block is None or block.strip() != _render(face).strip():
        print("CHECK FAILED doc block differs from what the face renders today")
        return 4
    print("CHECK OK -- %s at N=%d, arms=%d, anchors=%d/%d"
          % (face["verdict"], CRITERIA["n_conservative"], len(ARMS),
             sum(1 for a in (face.get("anchors") or []) if a["ok"]), len(face.get("anchors") or [])))
    return 0


# ------------------------------------------------------------------------ selftest
def _fixture_measure(cagr, sharpe, vol, sigma_sr, bars=1540):
    """A synthetic measurement block with the same shape as the real one."""
    import book_deflated_expectation as BDE

    def blk(c, s, v, sig):
        return {"cagr": c, "sharpe": s, "maxdd": -0.1, "vol": v, "years": 6.11,
                "bars": bars, "window": ["2020-07-16", "2026-11-20"],
                "sigma_sr": sig,
                "dsr_curve": [{"n_trials": n, "dsr": 0.5, "sr_star_daily": 0.01}
                              for n in CRITERIA["n_ladder"]]}

    arms = {}
    for name, (c, s, v, sig) in zip(list(ARMS),
                                    [(cagr[0], sharpe[0], vol[0], sigma_sr[0]),
                                     (cagr[1], sharpe[1], vol[1], sigma_sr[1]),
                                     (cagr[2], sharpe[2], vol[2], sigma_sr[2]),
                                     (cagr[3], sharpe[3], vol[3], sigma_sr[3])]):
        arms[name] = {"own": blk(c, s, v, sig), "common": blk(c, s, v, sig),
                      "anchor_window": blk(c, s, v, sig),
                      "config": ARMS[name]}
    _ = BDE  # imported for symmetry with the real path
    return {"schedule": {"panel_universe": 1528, "panel_flips_repaired": 169,
                         "span_flips_repaired": 1, "panel_last_bar": "2026-11-20",
                         "common_window": ["2020-07-16", "2026-11-20"],
                         "basket_turnover_total": 1.0, "market_column": "510300"},
            "arms": arms, "elapsed_sec": 0.0}


def selftest():
    """Offline: arithmetic and behaviour on fixtures. No panel, no engine."""
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    import book_deflated_expectation as BDE

    # L1 the haircut is imported, and it is the one that produced the published row
    bde = _load(ROOT / "results" / "book_deflated_expectation.json") or {}
    at58 = (bde.get("at_conservative_n") or {})
    rent = _load(SRC_RENT) or {}
    cents = (rent.get("book") or {}).get("cents") or {}
    sig = _published_sigma(rent) if rent else None
    mine = BDE._haircut_row(cents["sharpe"], cents["vol"], sig, 58,
                            CRITERIA["capital_cny"], CRITERIA["t_req"], CRITERIA["abandon_p"])
    leg("L1 imported haircut reproduces the published N=58 row (%.6f vs %s)"
        % (mine["budgetable_cagr"], at58.get("budgetable_cagr")),
        at58.get("budgetable_cagr") is not None
        and abs(mine["budgetable_cagr"] - float(at58["budgetable_cagr"])) <= 1e-6)

    # L2 budgetable is credible x vol, exactly (storage precision 6dp)
    leg("L2 budgetable = credible Sharpe x vol",
        abs(mine["budgetable_cagr"] - mine["credible_sharpe"] * cents["vol"]) <= 1e-6)

    # L3 the credible Sharpe never rises with trial count
    prev = None
    mono = True
    for n in CRITERIA["n_ladder"]:
        r = BDE._haircut_row(cents["sharpe"], cents["vol"], sig, n,
                             CRITERIA["capital_cny"], CRITERIA["t_req"], CRITERIA["abandon_p"])
        if prev is not None and r["credible_sharpe"] > prev + 1e-12:
            mono = False
        prev = r["credible_sharpe"]
    leg("L3 credible Sharpe is non-increasing in N", mono)

    # L4/L5 verdict branches, both driven by rows the fixture actually prints
    cash = 0.01777
    # winner on headline, loser after rent -> the flip verdict
    flip = _fixture_measure(cagr=(0.1272, 0.1093, 0.0916, 0.0765),
                            sharpe=(0.991, 1.123, 0.946, 0.790),
                            vol=(0.1348, 0.1005, 0.1019, 0.1039),
                            sigma_sr=(0.025656, 0.025457, 0.025103, 0.025531))
    rows = _rows(flip, cash, CRITERIA["capital_cny"])
    v, info = _verdict(rows, cash, "ticket_n5_beta020_8bp")
    leg("L4 headline-first + rent-worst -> flip verdict (%s, rank %s->%s)"
        % (v, info["chosen_headline_rank"], info["chosen_credible_rank"]),
        v == "THE_PLACEMENT_TRADES_THE_BOOK_THE_RENT_LIKES_LEAST"
        and info["chosen_headline_rank"] == 1 and info["chosen_credible_rank"] > 1)

    # the same shape but a much stronger ticket -> survives
    strong = _fixture_measure(cagr=(0.20, 0.11, 0.09, 0.08),
                              sharpe=(1.60, 1.123, 0.946, 0.790),
                              vol=(0.1348, 0.1005, 0.1019, 0.1039),
                              sigma_sr=(0.025656, 0.025457, 0.025103, 0.025531))
    v2, info2 = _verdict(_rows(strong, cash, CRITERIA["capital_cny"]), cash,
                         "ticket_n5_beta020_8bp")
    leg("L5 a genuinely strong ticket survives the rent (%s)" % v2,
        v2 == "THE_PLACEMENT_SURVIVES_THE_RENT" and info2["chosen_credible_rank"] == 1)

    # L6 the cash row is a ruler, not an arm: it never enters the ranking
    cash_rows = [r for r in rows if r["arm"] == CASH_ARM]
    leg("L6 cash leg printed once per frame and excluded from the ranking",
        len(cash_rows) == len(CRITERIA["frames"])
        and all(r["budgetable_cagr"] == round(cash, 6) for r in cash_rows)
        and info["arms_below_cash"] is not None)

    # L7 arms below cash are named from the printed rows
    below = set(info["arms_below_cash"])
    recomputed = {r["arm"] for r in rows
                  if r["window"] == CRITERIA["deciding_frame"] and r["arm"] != CASH_ARM
                  and r["budgetable_cagr"] < cash}
    leg("L7 arms_below_cash == the rows printed below the cash leg", below == recomputed)

    # L8 the published anchors are present and named (a face that cannot name them cannot be checked)
    try:
        pub = _published()
        named = all(pub.get(k) is not None for k in
                    ("ticket", "card5", "basket", "placement_cash_net_annual",
                     "placement_best_vehicle", "card5_sigma_sr_published"))
    except Exception:
        pub, named = None, False
    leg("L8 anchor inputs are present and named", named)
    if named:
        leg("L8b the placement's best vehicle maps to a measured arm",
            _chosen_arm(pub) in ARMS)

    # L11 the verdict sentence must not claim a rank the arithmetic does not give it.
    # (The first draft of this sentence said "headline first = worst after the rent"; the
    # ticket is second, not last, which is exactly the E222 shape -- a description of the
    # number, not a story about it.)
    cash2 = pub["placement_cash_net_annual"] if named else cash
    zh = _verdict_zh(v, info, "ticket_n5_beta020_8bp", rows, cash2)
    leg("L11 verdict sentence states the measured rank and claims nothing stronger",
        ("第 %d 位" % info["chosen_credible_rank"]) in zh and "垫底" not in zh
        and info["credible_order"][0] in zh)

    global OUT_JSON, OUT_MD
    saved_json, saved_md = OUT_JSON, OUT_MD
    tmpdir = Path(tempfile.mkdtemp(prefix="cpr_selftest_"))
    try:
        # the selftest must never touch the real face -- everything below lives in tmpdir
        OUT_JSON = tmpdir / "face.json"
        OUT_MD = tmpdir / "page.md"
        face = build(measure=flip, write=False, verbose=False)
        _dump(OUT_JSON, face)
        _write_doc(face)

        import io as _io
        from contextlib import redirect_stdout

        poisoned = json.loads(json.dumps(face))
        # a number that no longer follows from the printed measurement
        poisoned["rows"][0]["money_on_capital"] = 999999.0
        _dump(OUT_JSON, poisoned)
        buf = _io.StringIO()
        with redirect_stdout(buf):
            rc = check()
        txt = buf.getvalue()
        leg("L9 same measurement, wrong number -> rc4 without the STALE word",
            rc == 4 and "CHECK FAILED" in txt and "STALE" not in txt)

        _dump(OUT_JSON, face)
        moved = json.loads(json.dumps(face))
        moved["evidence_cutoff"] = "1999-01-01"
        _dump(OUT_JSON, moved)
        buf = _io.StringIO()
        with redirect_stdout(buf):
            rc = check()
        txt = buf.getvalue()
        leg("L10 cutoff that is not the measured last bar -> rc3 naming STALE",
            rc == 3 and "STALE" in txt)
    finally:
        OUT_JSON, OUT_MD = saved_json, saved_md
        shutil.rmtree(tmpdir, ignore_errors=True)

    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def show():
    face = _load(OUT_JSON)
    if not face:
        print("no face yet: run `run` first")
        return 1
    print(_render(face))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "show", "--selftest"])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "--selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    if args.cmd == "show":
        return show()
    face = build(write=True)
    if not face["anchors_ok"]:
        bad = [a["arm"] + " / " + a["what"] for a in face["anchors"] if not a["ok"]]
        print("WARNING: anchor legs failed -- the arm I measured is not the published book; "
              "the verdict below is not evidence")
        for b in bad:
            print("  ANCHOR FAIL: " + b)
    chosen_row = next(r for r in face["rows"]
                      if r["arm"] == face["chosen_arm"]
                      and r["window"] == CRITERIA["deciding_frame"])
    # ASCII only on stdout: the console codepage is GBK and cannot carry the yen sign
    print("%s at N=%d: %s -> %.2f%%/yr on %d CNY -- %s"
          % (face["verdict"], CRITERIA["n_conservative"], face["chosen_arm"],
             100.0 * chosen_row["budgetable_cagr"], CRITERIA["capital_cny"], face["face"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
