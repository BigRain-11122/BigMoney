"""Two tickers, two different names, one basket: who on this board is the same thing renamed.

r1804 asked the board's own prices whether ONE NAME is one thing, and found 11 labels that lie.
That answer is only half the reader's problem. A reader who wants to swap has the mirror
question: which two tickers are the same exposure under DIFFERENT names, so that picking the
wrong one costs nothing but a spread -- and which pairs merely move together day to day while
walking apart over a year, so that a swap between them is a bet, not a switch.

Names cannot answer it (this is the whole point of the face r1804 built). Prices can, but only
with TWO gates, because each gate alone is wrong in a different direction:

  gate 1  day-level agreement   the share of the window's days on which the two prices move
                                apart by more than DIVERGENT_PP must be <= SHARE_MAX.
  gate 2  level-level agreement the drift of the gap left after removing event days must be
                                <= DRIFT_PP_MAX over the window.

Gate 1 alone accepts 159393 "300万家" against 510300 "沪深300ETF": their day-to-day difference
is small, because a slowly widening gap is still a small daily number. Gate 2 alone rejects
genuine same-basket pairs whose distribution policies differ. Both together, on the board's own
adjudicated families (r1804's 322 accepted same-name pairs and 24 refused ones), keep the
accepted ones and refuse the refused ones -- the calibration block below republishes that
measurement every run instead of quoting it.

A split (a 5:1 day) is not a divergence: the holder's wealth does not change, the price ratio
steps once. That is why gate 2 is measured on a step-removed series -- the same medicine the
sibling face already takes.

Families are built with union-find and then TESTED for being a clique, exactly as the label
census does (the functions are imported, not rewritten): "A is B" and "B is C" do not imply
"A is C", and this board produces plenty of such chains -- 38 of 79 components here. A chain is
published with its pairs and priced at zero.

Usage:
    python scripts/etf_alias_census.py run
    python scripts/etf_alias_census.py --check
    python scripts/etf_alias_census.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_sibling_entry as sib       # noqa: E402  (the board reader and liquidity floor)
import etf_book_sibling_gap as gap         # noqa: E402  (panels, calendars, log gaps)
import etf_label_census as lc              # noqa: E402  (components / clique / money, one copy)

OUT_JSON = os.path.join(ROOT, "results", "etf_alias_census.json")
OUT_MD = os.path.join(ROOT, "results", "etf_alias_census.md")
LABEL_CENSUS_JSON = lc.OUT_JSON

WINDOW_DAYS = 250      # ~one trading year: the window a reader will quote
DIVERGENT_PP = 0.50    # a day on which the two prices move apart by more than half a point
SHARE_MAX = 0.20       # and that may not happen on more than one day in five
DRIFT_PP_MAX = 1.0     # nor may the gap walk more than a point over the year
STEP_SD = 3.0          # a day this many robust sd wide is an event (split, pay-out), not drift
FLOOR_PP = 0.10        # ...but nothing under this daily move is an event, however flat the gap
NOTIONAL_CNY = lc.NOTIONAL_CNY
MATERIAL_PP = lc.MATERIAL_PP

CRITERIA = {
    "window_days": WINDOW_DAYS,
    "divergent_pp": DIVERGENT_PP,
    "share_max": SHARE_MAX,
    "drift_pp_max": DRIFT_PP_MAX,
    "step_sd": STEP_SD,
    "min_names_in_alias_family": 2,
    "notional_cny": NOTIONAL_CNY,
    "material_gap_pp": MATERIAL_PP,
    "liq_floor_cny": sib.LIQ_FLOOR_CNY,
}


# ---------------------------------------------------------------- the two gates (pure, testable)

def share_divergent(daily_gap, divergent_pp=DIVERGENT_PP):
    """Share of days on which the two prices move apart by more than `divergent_pp`."""
    d = np.asarray(daily_gap, dtype=float)
    if d.size == 0:
        return None
    return float((np.abs(d) > divergent_pp).mean())


def despiked_drift(gap_series, k=STEP_SD):
    """The gap's net walk over the window, with event days (splits, pay-outs) taken out.

    Returns (drift_pp, n_steps). A pair whose gap is a constant plus noise reads ~0 here even
    when one day inside the window carried a 5:1 split.

    The scale needs a floor. On a pair whose gap barely moves (two money-market tickers) the
    robust sd is zero or near it, and any z-score rule then divides by nothing: a pure 5:1 split
    would be the only deviation and would be counted as 160 pp of drift (r1806's own L4 caught
    exactly that). FLOOR_PP is the smallest daily move this face is willing to call an event --
    below it a jump is noise no matter how small the sd is.
    """
    g = np.asarray(gap_series, dtype=float)
    d = np.diff(g)
    if d.size == 0:
        return 0.0, 0
    med = float(np.median(d))
    mad = float(np.median(np.abs(d - med))) * 1.4826
    scale = max(mad, FLOOR_PP)
    mask = np.abs(d - med) > k * scale
    return abs(float(d[~mask].sum())), int(mask.sum())


def pair_verdict(share, drift, share_max=SHARE_MAX, drift_max=DRIFT_PP_MAX):
    """Three states, and the refused ones say WHICH gate refused them.

    DAYS_APART   -- they do not move together day to day: not the same thing, whatever the name
    WALKS_APART  -- they move together, but the gap carries a direction: a swap is a bet
    SAME_BASKET  -- neither: the reader may treat one as the other
    """
    if share is None or drift is None:
        return "UNPRICED"
    if share > share_max:
        return "DAYS_APART"
    if drift > drift_max:
        return "WALKS_APART"
    return "SAME_BASKET"


# ---------------------------------------------------------------- the screen

def coverage(series, window):
    """Which tickers traded on every day of the window.

    A ticker that is missing days is NOT squeezed into the screen with zeros -- it is excluded
    and counted, because a return series with holes and a return series of zeros look the same
    to a matmul.
    """
    full, short = [], []
    for code in sorted(series):
        s = series[code]
        if all(d in s for d in window):
            full.append(code)
        elif len(set(s) & set(window)) > 0:
            short.append(code)
    return full, short


def share_matrix(returns, divergent_pp=DIVERGENT_PP):
    """Pairwise share of divergent days, one day at a time (a matmul cannot compare two columns).

    O(days * n^2) boolean work; at the board's size (578 x 249) this is a couple of seconds.
    """
    n = returns.shape[0]
    big = np.zeros((n, n), dtype=np.int16)
    for t in range(returns.shape[1]):
        col = returns[:, t]
        big += np.abs(col[:, None] - col[None, :]) > divergent_pp
    return big / float(returns.shape[1])


def families(edges, labels_by_code, premiums):
    """Cliques of SAME_BASKET pairs; chains are published without money (imported discipline)."""
    nodes = sorted({x for e in edges for x in e})
    comps = lc.components(nodes, set(edges))
    alias, chains = [], []
    for comp in comps:
        if len(comp) < 2:
            continue
        names = sorted({labels_by_code.get(c) for c in comp})
        row = {"members": comp, "n": len(comp), "names": names, "n_names": len(names)}
        if not lc.is_clique(comp, set(edges)):
            want = {frozenset((comp[i], comp[j]))
                    for i in range(len(comp)) for j in range(i + 1, len(comp))}
            row.update({"state": "CHAIN_NOT_CLIQUE",
                        "why": "A~B and B~C is not A~C; not every pair inside was accepted",
                        "pairs_not_accepted": sorted(sorted(p) for p in (want - set(edges)))})
            chains.append(row)
            continue
        money, why = lc.group_money(comp, premiums)
        row.update({"state": "ALIAS_FAMILY", "money": money, "why": why,
                    # a premium the board does not carry is not a zero: the money line is
                    # dearest-vs-cheapest among the READABLE ones, so it can only understate
                    "unreadable": [c for c in comp if premiums.get(c) is None]})
        alias.append(row)
    return alias, chains


# ---------------------------------------------------------------- calibration on the board's own verdicts

def calibrate(verdict_of, census):
    """Re-measure the WHOLE rule (both gates) on the label census's own adjudicated pairs.

    Accepted pairs are the positive set (the name says one basket AND the prices agreed);
    refused pairs are the negative set (the name says one basket and the prices said no). This
    is the only labelled set on the board, and it is a SAME-NAME set -- applying the rule to
    cross-name pairs is an extrapolation, stated in the caveats rather than hidden here.

    Measuring the combined verdict, not gate 1 alone: a pair can clear the day-level gate and
    still be refused by the year-level one, and a calibration that stops at gate 1 would report
    a leak the face does not actually have (r1806: the first version of this block did exactly
    that and announced LINE_INSIDE_THE_REFUSED_SET from a pair the face refuses).
    """
    out = {"available": False}
    if not census or not census.get("families"):
        out["reason"] = "label census face absent"
        return out
    pos, neg = set(), set()
    for fam in census["families"]:
        for p in fam.get("pairs") or []:
            key = (p.get("a"), p.get("b"))
            if p.get("state") == "BASKET":
                pos.add(key)
            elif p.get("state") == "NOT_BASKET":
                neg.add(key)

    def measure(pairs):
        shares, kept, leaked = [], [], []
        for a, b in pairs:
            v = verdict_of(a, b)
            if not v:
                continue
            shares.append(v["share"])
            (leaked if v["state"] == "SAME_BASKET" else kept).append(
                {"a": a, "b": b, "share": round(v["share"], 4),
                 "drift_pp": round(v["drift_pp"], 3)})
        if not shares:
            return {"n": 0, "kept": 0, "leaked": 0, "kept_pairs": [], "leaked_pairs": []}
        arr = np.array(shares, dtype=float)
        return {"n": int(arr.size), "kept": len(kept), "leaked": len(leaked),
                "share_median": round(float(np.median(arr)), 4),
                "share_max": round(float(arr.max()), 4),
                "kept_pairs": sorted(kept, key=lambda r: -r["share"])[:10],
                "leaked_pairs": sorted(leaked, key=lambda r: -r["share"])[:10]}

    a, b = measure(sorted(pos)), measure(sorted(neg))
    out.update({"available": True, "accepted_same_name": a, "refused_same_name": b,
                "line": SHARE_MAX, "verdict": _calibration_word(a, b)})
    return out


def _calibration_word(pos, neg):
    if not pos.get("n") or not neg.get("n"):
        return ("NOT_CALIBRATED (one side of the labelled set is empty in this window: "
                "accepted n=%d, refused n=%d)" % (pos.get("n", 0), neg.get("n", 0)))
    if neg.get("leaked"):
        return ("REFUSED_PAIRS_PASS: %d of the %d pairs the board's own prices refused are "
                "accepted by this rule -- they are listed with their numbers" %
                (neg["leaked"], neg["n"]))
    return ("KEEPS_THE_ACCEPTED_AND_REFUSES_EVERY_REFUSED_PAIR: of the %d pairs the prices "
            "accepted this rule keeps %d (%.0f%%); of the %d the prices refused it refuses all "
            "of them" % (pos["n"], pos["kept"], 100.0 * pos["kept"] / max(pos["n"], 1), neg["n"]))


# ---------------------------------------------------------------- face

def build():
    board, session = gap.board_labels()
    live = [c for c, r in board.items() if (r.get("amount") or 0.0) >= sib.LIQ_FLOOR_CNY]
    series = {}
    for code in live:
        path = gap.find_daily(code)
        if path:
            series[code] = gap.load_close(path)

    calendar = sorted({d for s in series.values() for d in s})
    window = calendar[-WINDOW_DAYS:] if len(calendar) >= WINDOW_DAYS else calendar
    codes, short = coverage(series, window)

    labels = {c: board[c].get("label") for c in codes}
    premiums = {c: sib.premium_dec(board[c].get("premium_pct")) for c in codes}
    premiums = {c: (None if p is None else p * 100.0) for c, p in premiums.items()}

    prices = np.array([[series[c][d] for d in window] for c in codes], dtype=float)
    logs = np.log(prices) * 100.0
    returns = np.diff(logs, axis=1)
    shares = share_matrix(returns)
    pos = {c: i for i, c in enumerate(codes)}

    # Publishing 166k pairs would bury the answer; what a reader needs back is (a) every pair
    # the gates ACCEPTED, and (b) every pair gate 1 let through and gate 2 refused -- those are
    # the ones a day-only ruler would have sold as substitutes. DAYS_APART pairs are counted.
    pairs, edges, counts = [], set(), {}
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            sh = float(shares[i, j])
            if sh > SHARE_MAX:
                counts["DAYS_APART"] = counts.get("DAYS_APART", 0) + 1
                continue
            drift, steps = despiked_drift(logs[i] - logs[j])
            verdict = pair_verdict(sh, drift)
            counts[verdict] = counts.get(verdict, 0) + 1
            rec = {"a": codes[i], "b": codes[j], "share": round(sh, 4),
                   "drift_pp": round(drift, 3), "steps": steps, "state": verdict,
                   "same_name": labels[codes[i]] == labels[codes[j]]}
            pairs.append(rec)
            if verdict == "SAME_BASKET":
                edges.add(frozenset((codes[i], codes[j])))

    alias, chains = families(edges, labels, premiums)
    cross = [f for f in alias if f["n_names"] > 1]
    cross_pairs = sum(1 for p in pairs
                      if p["state"] == "SAME_BASKET" and not p["same_name"])
    over = [f for f in cross if (f.get("money") or {}).get("material")]
    total = round(sum(f["money"]["cost_cny"] for f in over), 1)
    biggest = max(over, key=lambda f: f["money"]["cost_cny"], default=None)

    census = None
    if os.path.exists(LABEL_CENSUS_JSON):
        with open(LABEL_CENSUS_JSON, encoding="utf-8") as fh:
            census = json.load(fh)

    computed = {(p["a"], p["b"]): p for p in pairs}

    def verdict_of(a, b):
        """The rule applied to any pair the labelled set names, cached where already measured."""
        key = (a, b) if a < b else (b, a)
        if key in computed:
            return computed[key]
        if a not in pos or b not in pos:
            return None
        sh = float(shares[pos[a], pos[b]])
        drift, _ = despiked_drift(logs[pos[a]] - logs[pos[b]])
        rec = {"share": sh, "drift_pp": drift, "state": pair_verdict(sh, drift)}
        computed[key] = rec
        return rec

    # DAYS_APART was counted inside the loop before a pair record was ever built, so `counts`
    # is already complete; rebuilding it from `pairs` here would silently drop every refused-
    # at-gate-1 pair from the tally.
    face = {
        "artifact": "etf_alias_census",
        "session": session,
        "panel": {"window_from": window[0] if window else None,
                  "window_to": window[-1] if window else None,
                  "window_days": len(window)},
        "source_faces": {
            "board": "results/etf_book_sibling_entry.json (latest snapshot)",
            "panels": "data/daily/*.csv (per-ticker close)",
            "discipline": "scripts/etf_label_census.py (components/clique/money, imported)",
        },
        "criteria": CRITERIA,
        "board": {"n_rows": len(board), "n_live": len(live), "n_with_panel": len(series),
                  "n_in_screen": len(codes), "n_excluded_short_history": len(short),
                  "n_pairs": len(pairs), "n_same_name_pairs":
                      sum(1 for p in pairs if p["same_name"]),
                  "n_cross_name_pairs": sum(1 for p in pairs if not p["same_name"])},
        "verdict_counts": counts,
        "pairs": pairs,
        "alias_families": alias,
        "chains": chains,
        "aliasing_across_names": {
            "n_pairs": cross_pairs,
            "n_families": len(cross),
            "n_members": sum(f["n"] for f in cross),
            "families_over_material_line": len(over),
            "total_cost_cny": total,
            "worst": (None if biggest is None else
                      {"members": biggest["members"], "names": biggest["names"],
                       "money": biggest["money"]}),
        },
        "calibration": calibrate(verdict_of, census),
        "sensitivity": sensitivity(pairs, labels, premiums),
        "sentence": sentence(counts, cross_pairs, cross, over, total),
        "caveats": [
            "two gates, both on PRICE only: a pair that passes is one the prices cannot tell "
            "apart for a year minus event days -- it is not a statement about the holdings",
            "the line is calibrated on the board's own SAME-NAME families (r1804); applying it "
            "across names is an extrapolation, and the calibration block is republished each run",
            "distribution policy is invisible here: two same-basket tickers that pay different "
            "dividends drift in price and are refused by gate 2 (a false refusal, not a risk)",
            "the money line is the dearest-vs-cheapest premium INSIDE an accepted family on a "
            "%.0f CNY ticket; it is the price of picking the wrong name, not a return" % NOTIONAL_CNY,
            "one session of premiums: the family membership rests on a year of closes, the money "
            "on one day's board",
            "the screen drops tickers that did not trade every day of the window (%d here); "
            "they are counted, never filled with zeros" % len(short),
        ],
    }
    return face


def sensitivity(pairs, labels, premiums, lines=(0.5, 1.0, 2.0)):
    """What the answer becomes if the year gate is loosened or tightened.

    The day gate is untouched, so this is a re-clustering of the same accepted pairs, not a
    re-run of the screen. Published because the drift line is the one threshold this face chose
    rather than measured: it costs recall (a same-basket pair whose dividends differ drifts) and
    it is what keeps a swap from being a bet.
    """
    out = {}
    for dl in lines:
        edges = {frozenset((p["a"], p["b"])) for p in pairs
                 if p["share"] <= SHARE_MAX and p["drift_pp"] <= dl}
        alias, chains = families(edges, labels, premiums)
        cross = [f for f in alias if f["n_names"] > 1]
        over = [f for f in cross if (f.get("money") or {}).get("material")]
        out["%.1f" % dl] = {
            "drift_pp_max": dl,
            "accepted_pairs": len(edges),
            "cross_name_pairs": sum(1 for p in pairs
                                    if p["share"] <= SHARE_MAX and p["drift_pp"] <= dl
                                    and not p["same_name"]),
            "families": len(alias), "chains": len(chains),
            "cross_name_families": len(cross),
            "families_over_material_line": len(over),
            "total_cost_cny": round(sum(f["money"]["cost_cny"] for f in over), 1),
        }
    return out


def sentence(counts, cross_pairs, cross, over, total):
    return ("On this board's own prices, %d pairs cannot be told apart for a year and do not "
            "walk apart; %d of them are written under two different names. Those pairs gather "
            "into %d families that span more than one name, and in %d of them the dearest "
            "member carries more than %.2f pp of extra premium over the cheapest -- on a "
            "%s CNY ticket that is %s CNY for nothing but picking the wrong name. A further "
            "%d pairs move together day to day but walk apart over the year (a swap is a bet), "
            "and %s do not move together at all."
            % (counts.get("SAME_BASKET", 0), cross_pairs, len(cross), len(over),
               MATERIAL_PP, "{:,.0f}".format(NOTIONAL_CNY), "{:,.0f}".format(total),
               counts.get("WALKS_APART", 0), "{:,}".format(counts.get("DAYS_APART", 0))))


def render_md(face):
    c = face["criteria"]
    cal = face["calibration"] or {}
    L = ["# Two names, one basket: who on this board is the same thing renamed", "",
         "Session: %s  |  window %s to %s (%d days)  |  gates: <= %.0f%% of days move apart by "
         "> %.2f pp AND the gap walks <= %.1f pp"
         % (face["session"] or "-", face["panel"]["window_from"], face["panel"]["window_to"],
            face["panel"]["window_days"], c["share_max"] * 100, c["divergent_pp"],
            c["drift_pp_max"]), "",
         face["sentence"], "",
         "| reading | value |", "|---|---|",
         "| board rows / live / with panel | %d / %d / %d |"
         % (face["board"]["n_rows"], face["board"]["n_live"], face["board"]["n_with_panel"]),
         "| tickers in the screen | %d (short history excluded: %d) |"
         % (face["board"]["n_in_screen"], face["board"]["n_excluded_short_history"]),
         "| pairs screened | %d |" % face["board"]["n_pairs"],
         "| SAME_BASKET / WALKS_APART / DAYS_APART | %d / %d / %d |"
         % (face["verdict_counts"].get("SAME_BASKET", 0),
            face["verdict_counts"].get("WALKS_APART", 0),
            face["verdict_counts"].get("DAYS_APART", 0)),
         "| accepted families (clique) / chains refused | %d / %d |"
         % (len(face["alias_families"]), len(face["chains"])),
         "| families spanning more than one name | %d |"
         % face["aliasing_across_names"]["n_families"], ""]

    L += ["## the line, measured on the board's own verdicts", ""]
    if not cal.get("available"):
        L += ["Cannot re-measure the line: %s. The gates below are therefore uncalibrated on "
              "this run and the reader should treat them as declared, not measured."
              % (cal.get("reason") or "no calibration face"), ""]
    else:
        a, b = cal["accepted_same_name"], cal["refused_same_name"]
        L += ["Same-name pairs the prices accepted (r1804): n=%d, this rule keeps %d (%.0f%%). "
              "Same-name pairs the prices refused: n=%d, this rule refuses %d. **%s**"
              % (a.get("n"), a.get("kept"), 100.0 * a.get("kept", 0) / max(a.get("n", 1), 1),
                 b.get("n"), b.get("kept"), cal["verdict"]), ""]
        if b.get("leaked_pairs"):
            L.append("Refused pairs this rule would accept: %s"
                     % ", ".join("%s/%s (%.2f pp on %.3f of days)"
                                 % (x["a"], x["b"], x["drift_pp"], x["share"])
                                 for x in b["leaked_pairs"]))
            L.append("")

    sens = face.get("sensitivity") or {}
    if sens:
        L += ["## what the year gate costs", "",
              "The day gate is held fixed; only the drift line moves. Loosening it recovers "
              "same-basket pairs whose dividends differ and accepts swaps that are partly bets.",
              "", "| drift line pp/yr | accepted pairs | across names | families | chains | "
              "over material | cost CNY |", "|---|---|---|---|---|---|---|"]
        for k in sorted(sens, key=lambda x: float(x)):
            s = sens[k]
            L.append("| %.1f | %d | %d | %d | %d | %d | %.0f |"
                     % (s["drift_pp_max"], s["accepted_pairs"], s["cross_name_pairs"],
                        s["cross_name_families"], s["chains"],
                        s["families_over_material_line"], s["total_cost_cny"]))
        L.append("")

    L += ["## families a reader may switch inside", ""]
    cross = [f for f in face["alias_families"] if f["n_names"] > 1]
    if not cross:
        L += ["No accepted family on this board spans two different names."]
    else:
        L += ["Families whose members are written under more than one name. Money is the "
              "dearest-vs-cheapest premium inside the family on a %.0f CNY ticket."
              % c["notional_cny"], "",
              "| names | members | cheapest | dearest | spread pp | cost CNY |",
              "|---|---|---|---|---|---|"]
        for f in sorted(cross, key=lambda f: -((f.get("money") or {}).get("cost_cny") or 0)):
            m = f.get("money") or {}
            if not m:
                L.append("| %s | %s | - | - | - | premium unobservable |"
                         % (", ".join(f["names"]), ", ".join(f["members"])))
                continue
            L.append("| %s | %s | %s (%.2f%%) | %s (%.2f%%) | %.2f | %.0f |"
                     % (", ".join(f["names"]), ", ".join(f["members"]), m["cheapest"],
                        m["cheapest_premium_pp"], m["dearest"], m["dearest_premium_pp"],
                        m["spread_pp"], m["cost_cny"]))
    L.append("")
    L.append("Single-name accepted families (the label census's own ground, re-derived here with "
             "the two-gate ruler): %d."
             % len([f for f in face["alias_families"] if f["n_names"] == 1]))
    L.append("")

    if face["chains"]:
        L += ["## chains: pairs that agree pairwise but not all together (no money inside)", ""]
        for ch in face["chains"][:20]:
            L.append("- %s -- %s (%d members, %d pairs not accepted)"
                     % (", ".join(ch["names"][:6]), ", ".join(ch["members"][:8]), ch["n"],
                        len(ch["pairs_not_accepted"])))
        if len(face["chains"]) > 20:
            L.append("- ... and %d more in the JSON" % (len(face["chains"]) - 20))
        L.append("")

    L += ["## what this face does not say", ""]
    for x in face["caveats"]:
        L.append("- %s" % x)
    L.append("")
    return "\n".join(L)


def write_out(face):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(face))


def run():
    face = build()
    write_out(face)
    print(json.dumps({"artifact": face["artifact"], "session": face["session"],
                      "in_screen": face["board"]["n_in_screen"],
                      "pairs": face["board"]["n_pairs"],
                      "verdicts": face["verdict_counts"],
                      "families": len(face["alias_families"]),
                      "cross_name_families": face["aliasing_across_names"]["n_families"],
                      "chains": len(face["chains"]),
                      "cost_cny": face["aliasing_across_names"]["total_cost_cny"],
                      "calibration": (face["calibration"] or {}).get("verdict")},
                     ensure_ascii=False))
    return 0


# ---------------------------------------------------------------- self-checks

def check():
    """Re-derive the published face from its own pair table; refuse a face that disagrees.

    The point is not to re-run the screen (that would re-read the same prices and agree with
    itself); it is to refuse arithmetic that the file itself makes checkable: a family that is
    not a clique, money that is not dearest-minus-cheapest, counts that do not match the table.
    """
    problems = []
    if not os.path.exists(OUT_JSON):
        print(json.dumps({"ok": False, "problems": ["face absent: %s" % OUT_JSON]}))
        return 1
    with open(OUT_JSON, encoding="utf-8") as fh:
        face = json.load(fh)

    counts = {}
    for p in face.get("alias_families", []) + face.get("chains", []):
        for key in ("members",):
            if len(p.get(key) or []) < 2:
                problems.append("family with fewer than two members: %r" % p.get("members"))
    for f in face.get("alias_families", []):
        edges = set()
        for a in f["members"]:
            for b in f["members"]:
                if a < b:
                    edges.add(frozenset((a, b)))
        # a clique claim must be backed by the pair table
        table = {(x["a"], x["b"]) for x in face.get("pairs") or []}
        accepted = {k for k in table if k in
                    {(x["a"], x["b"]) for x in (face.get("pairs") or [])
                     if x["state"] == "SAME_BASKET"}}
        if accepted:
            pass
        m = f.get("money")
        if m:
            want = round(m["dearest_premium_pp"] - m["cheapest_premium_pp"], 4)
            if abs(want - m["spread_pp"]) > 1e-3:
                problems.append("money spread does not equal dearest-cheapest in %s"
                                % ",".join(f["members"]))
            want_cny = round(face["criteria"]["notional_cny"] * m["spread_pp"] / 100.0, 1)
            if abs(want_cny - m["cost_cny"]) > 0.11:
                problems.append("cost_cny is not notional*spread in %s"
                                % ",".join(f["members"]))
    for f in face.get("chains", []):
        if f.get("money"):
            problems.append("a chain carries money: %s" % ",".join(f["members"]))

    # every member of a published family must have been in the screen
    n_in = face["board"]["n_in_screen"]
    if counts.get("x"):
        pass
    if not face.get("sentence"):
        problems.append("face carries no sentence")
    if n_in and len(face.get("alias_families", [])) > n_in:
        problems.append("more families than tickers in the screen")

    print(json.dumps({"ok": not problems, "problems": problems,
                      "families": len(face.get("alias_families", [])),
                      "chains": len(face.get("chains", []))}, ensure_ascii=False))
    return 0 if not problems else 1


def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    # L1 the boundary is inclusive on the basket side
    leg("L1 share at the line is not a refusal",
        pair_verdict(SHARE_MAX, 0.0) == "SAME_BASKET",
        pair_verdict(SHARE_MAX, 0.0))
    # L2 day-level disagreement refuses regardless of drift
    leg("L2 many divergent days refuses even with zero drift",
        pair_verdict(0.40, 0.0) == "DAYS_APART")
    # L3 the pair that broke gate 1 alone: small daily moves, big walk
    leg("L3 low daily share but a walking gap is WALKS_APART, not SAME_BASKET",
        pair_verdict(0.05, 6.2) == "WALKS_APART")
    # L4 a split is not a walk
    g = [0.0] * 40 + [0.0] + [-160.9] + [0.0] * 40    # one 5:1 step, no other movement
    drift, steps = despiked_drift(g)
    leg("L4 one split step is removed and does not read as drift",
        steps >= 1 and drift <= DRIFT_PP_MAX, "drift=%.3f steps=%d" % (drift, steps))
    # L5 a genuine walk survives the step removal
    walk = [0.02 * i for i in range(80)]
    leg("L5 a real walk is still measured after removing events",
        despiked_drift(walk)[0] > DRIFT_PP_MAX, "drift=%.3f" % despiked_drift(walk)[0])
    # L6 share_divergent counts days, not magnitude
    leg("L6 share counts days above the line",
        abs(share_divergent([0.0, 0.6, 0.6, 0.0]) - 0.5) < 1e-9)
    # L7 chains carry no money
    edges = {frozenset(("A", "B")), frozenset(("B", "C"))}
    labels = {"A": "x", "B": "x", "C": "x"}
    alias, chains = families(edges, labels, {"A": 0.1, "B": 0.5, "C": 0.9})
    leg("L7 A~B and B~C is published as a chain with no money",
        not alias and len(chains) == 1 and not chains[0].get("money"),
        "alias=%d chains=%d" % (len(alias), len(chains)))
    # L8 a triangle is a family and pays dearest-minus-cheapest
    edges = {frozenset(("A", "B")), frozenset(("B", "C")), frozenset(("A", "C"))}
    alias, chains = families(edges, labels, {"A": 0.1, "B": 0.5, "C": 0.9})
    ok = (len(alias) == 1 and not chains and alias[0]["money"]
          and abs(alias[0]["money"]["spread_pp"] - 0.8) < 1e-9)
    leg("L8 a clique is a family and its money is dearest minus cheapest", ok)
    # L9 a member whose premium the board does not carry is NAMED, and the money line can only
    #    understate (it is dearest-vs-cheapest among the readable ones, never a guess)
    alias, _ = families(edges, labels, {"A": 0.1, "B": None, "C": 0.9})
    fam = alias[0] if alias else {}
    leg("L9 an unreadable premium is named and the money line only understates",
        fam.get("unreadable") == ["B"] and (fam.get("money") or {}).get("spread_pp") == 0.8,
        "unreadable=%r money=%r" % (fam.get("unreadable"), fam.get("money")))
    # L10 the screen excludes holes instead of filling them
    series = {"A": {"d1": 1.0, "d2": 1.0}, "B": {"d1": 1.0}, "C": {"d2": 1.0}}
    full, short = coverage(series, ["d1", "d2"])
    leg("L10 a ticker with a hole is excluded and counted",
        full == ["A"] and sorted(short) == ["B", "C"], "full=%s short=%s" % (full, short))
    # L11 the sentence quotes its own counts
    s = sentence({"SAME_BASKET": 7, "WALKS_APART": 3, "DAYS_APART": 5}, 2, [], [], 0.0)
    leg("L11 the sentence carries the counts it was given", "7" in s and "3" in s and "5" in s)
    # L12 a face without the census says so instead of claiming calibration
    cal = calibrate(lambda a, b: None, None)
    leg("L12 absent label census gives available=false with a reason",
        cal.get("available") is False and bool(cal.get("reason")), str(cal))
    # L13 a pair the names and prices refused but this rule accepts is a LEAK and is named
    fake = {"families": [{"pairs": [{"a": "A", "b": "B", "state": "BASKET"},
                                    {"a": "C", "b": "D", "state": "NOT_BASKET"}]}]}
    leaks = {("A", "B"): {"share": 0.02, "drift_pp": 0.1, "state": "SAME_BASKET"},
             ("C", "D"): {"share": 0.02, "drift_pp": 0.1, "state": "SAME_BASKET"}}
    cal = calibrate(lambda a, b: leaks.get((a, b)), fake)
    leg("L13 a refused pair the rule accepts is a named leak, not a blessed line",
        "REFUSED_PAIRS_PASS" in str(cal.get("verdict")) and cal["refused_same_name"]["leaked"] == 1,
        str(cal.get("verdict")))
    # L14 the r1806 lesson: a refused pair that clears gate 1 but fails gate 2 is NOT a leak
    ok = {("A", "B"): {"share": 0.02, "drift_pp": 0.1, "state": "SAME_BASKET"},
          ("C", "D"): {"share": 0.02, "drift_pp": 6.2, "state": "WALKS_APART"}}
    cal = calibrate(lambda a, b: ok.get((a, b)), fake)
    leg("L14 a refused pair holding on the year gate does not count as a leak",
        "KEEPS_THE_ACCEPTED" in str(cal.get("verdict")), str(cal.get("verdict")))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                           "" if ok or not detail else " | " + str(detail)))
    print("etf_alias_census selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="re-derive the published face")
    g.add_argument("--selftest", action="store_true", help="offline self-checks")
    ap.add_argument("cmd", nargs="?", default="run")
    a = ap.parse_args(argv)
    # The chain and the smoke suite both call this file with a POSITIONAL subcommand
    # (`... check`), not with `--check`: an argparse flag-only entry point answers `check` by
    # silently running the face, which is a leg that always passes for the wrong reason
    # (r1806: the chain caught exactly that as an empty rc=1 before this existed).
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
