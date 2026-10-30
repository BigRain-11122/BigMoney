"""Does the production book's width sign survive a signal-free book on its OWN panel?

Why this exists (one sentence): bm-c r1362's card E276 measured the width sign on the
E198 18-name cross and found it flips against the family's published "+wider earns more",
then showed a seeded random score reproduces the published direction -- and closed with the
demand that the family's width sign needs its own null *on its own panel*. This face is that
null: the SAME panel the production card is priced on (prep_panel() of
etf_book_production, equity/commodity/convertible only, repaired flips), the SAME engine
(backtest), the SAME cadence and toll, widths 3/5/8/12, real score vs N seeded random
scores masked to the real eligibility.

It does not change the book. It does not claim an optimum: it answers one question -- is the
width direction on THIS panel a property of the score, or the direction a signal-free book
has on a rising panel?

  python scripts/etf_book_width_null_production.py run [--seeds=6]
  python scripts/etf_book_width_null_production.py --selftest
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np

import etf_book_production as P

WIDTHS = (3, 5, 8, 12)
N_SELF = 5          # the width the card is currently in force at; published for the reader
OUT = os.path.join(ROOT, "results", "etf_book_width_null_production.json")
MD = os.path.join(ROOT, "results", "etf_book_width_null_production.md")


def spearman(xs, ys):
    """Rank correlation with average ranks for ties; None when a series is constant."""
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    if len(xs) < 2 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    a, b = rank(xs), rank(ys)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    da = sum((p - ma) ** 2 for p in a) ** 0.5
    db = sum((q - mb) ** 2 for q in b) ** 0.5
    if da == 0 or db == 0:
        return None
    return num / (da * db)


def sign(v):
    if v is None:
        return None
    return 1 if v > 0 else (-1 if v < 0 else 0)


def null_score(score, seed):
    """Seeded random scores on the real eligibility mask (NaN stays NaN)."""
    rng = np.random.default_rng(seed)
    out = score.copy()
    vals = rng.standard_normal(score.shape)
    out.loc[:, :] = np.where(score.notna().values, vals, np.nan)
    return out


def measure(widths, reals, nulls, cost_bp):
    """Frozen verdict rule -- recomputed from the published columns, never hand-written."""
    real_cagr = [reals[str(w)]["cagr"] for w in widths]
    null_cagr = [nulls[str(w)] for w in widths]
    if any(v is None for v in real_cagr) or any(v is None for v in null_cagr):
        return {"verdict": "NOT-ASSESSED", "why": "a rung never priced (None)"}
    if any(not np.isfinite(v) for v in real_cagr + null_cagr):
        return {"verdict": "NOT-ASSESSED", "why": "a rung priced a non-finite number"}
    real_rho = spearman(list(widths), real_cagr)
    null_rho = spearman(list(widths), null_cagr)
    gaps = [round((r - n) * 100.0, 2) for r, n in zip(real_cagr, null_cagr)]
    same = sign(real_rho) is not None and sign(real_rho) == sign(null_rho)
    return {
        "verdict": ("WIDTH_SIGN_IS_THE_NOISE_SIGN" if same
                    else "WIDTH_SIGN_DIFFERS_FROM_NOISE"),
        "real_rank_corr_width_cagr": None if real_rho is None else round(real_rho, 3),
        "null_rank_corr_width_cagr": None if null_rho is None else round(null_rho, 3),
        "real_minus_null_pp_per_rung": gaps,
        "widths": list(widths),
        "cost_bp": cost_bp,
    }



def cross_face_rules(ticket_path, my_sign):
    """The ticket already publishes width under TWO leverage rules. Read it, do not retype it.

    r1291's law is that a width difference means nothing until the leverage rule is fixed; this
    face prices a THIRD rule (no vol target, no beta scaling), so the reader has to be told
    whether the other two rules agree with the sign measured here.
    """
    if not os.path.exists(ticket_path):
        return {"ticket": ticket_path, "state": "omitted", "why": "ticket absent"}
    try:
        with open(ticket_path, encoding="utf-8") as f:
            tk = json.load(f)
        cells = ((tk.get("width_disclosure") or {}).get("square") or {}).get("cells") or {}
        out = {"ticket": ticket_path, "rules": {}}
        for rule in ("beta", "vol"):
            a = (cells.get("%s@5" % rule) or {}).get("cagr")
            b = (cells.get("%s@12" % rule) or {}).get("cagr")
            if a is None or b is None:
                out["rules"][rule] = {"state": "cell_absent"}
                continue
            gap = (b - a) * 100.0
            out["rules"][rule] = {"cagr@5": round(a, 4), "cagr@12": round(b, 4),
                                  "gap_12_minus_5_pp": round(gap, 2),
                                  "agrees_with_this_face": (sign(gap) == my_sign)}
        signs = [v.get("gap_12_minus_5_pp") for v in out["rules"].values()
                 if "gap_12_minus_5_pp" in v]
        agree = [v.get("agrees_with_this_face") for v in out["rules"].values()
                 if "agrees_with_this_face" in v]
        out["state"] = ("rules_agree" if agree and all(agree) else
                        "RULES_DISAGREE_ON_THE_WIDTH_SIGN" if agree else "unreadable")
        out["this_face_rule"] = ("no vol target, no beta scaling, 10bp, cadence 20 -- a third "
                                 "rule, so only the SIGN is comparable")
        return out
    except Exception as e:  # never let a reader-face break the measurement
        return {"ticket": ticket_path, "state": "unreadable", "why": repr(e)[:120]}

def run(n_seeds=6):
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    reals, nulls_by_seed = {}, {}
    nulls = {}
    for w in WIDTHS:
        out, _ = P.backtest(close, openp, amt, score, w, 20)
        reals[str(w)] = {k: out["full"][k] for k in ("cagr", "vol", "sharpe", "maxdd")}
        reals[str(w)]["turnover_per_decision"] = out["turnover_per_decision"]
        reals[str(w)]["is_cagr"] = out["is"]["cagr"]
        reals[str(w)]["oos_cagr"] = out["oos"]["cagr"]
        print("real n=%d cagr=%.4f" % (w, out["full"]["cagr"]), flush=True)
    for seed in range(1, n_seeds + 1):
        sc = null_score(score, seed)
        row = {}
        for w in WIDTHS:
            out, _ = P.backtest(close, openp, amt, sc, w, 20)
            row[str(w)] = out["full"]["cagr"]
            print("null seed=%d n=%d cagr=%.4f" % (seed, w, out["full"]["cagr"]), flush=True)
        nulls_by_seed[str(seed)] = row
    spread = {}
    for w in WIDTHS:
        vals = [nulls_by_seed[str(s)][str(w)] for s in range(1, n_seeds + 1)]
        nulls[str(w)] = float(np.median(vals))
        # the null is an estimate too: publish its per-seed range and the gap to its BEST draw,
        # otherwise a 15pp headline looks like it was measured against a point, not a spread.
        spread[str(w)] = {"min": float(min(vals)), "max": float(max(vals)),
                          "real_minus_best_null_pp": round((reals[str(w)]["cagr"] - max(vals)) * 100.0, 2)}
    verdict = measure(WIDTHS, reals, nulls, P.COST * 1e4)
    my_sign = sign(verdict.get("real_rank_corr_width_cagr"))
    cutoff = str(close.index[-1].date())
    cross = cross_face_rules(os.path.join(
        ROOT, "results", "etf_book_order", "TICKET-%s.json" % cutoff), my_sign)
    doc = {
        "face": "etf_book_width_null_production",
        "question": "is the width direction on the production panel a property of the score "
                    "or the direction a signal-free book has?",
        "panel": {"bars": int(len(close)), "names": int(len(close.columns)),
                  "first": str(close.index[0].date()), "last": str(close.index[-1].date()),
                  "n_flip_repairs": int(n_flip),
                  "universe_note": "equity+commodity+convertible only, repaired prints, "
                                   "same builder as the production card"},
        "config": {"rebal": 20, "cost_bp": P.COST * 1e4, "vol_target": None,
                   "widths": list(WIDTHS), "seeds": n_seeds},
        "real": reals,
        "null_median_cagr": nulls,
        "null_by_seed": nulls_by_seed,
        "null_spread": spread,
        "verdict": verdict,
        "cross_face_rules": cross,
        "honest_caveats": [
            "null shares the real eligibility mask and cadence, so it isolates the SCORE, "
            "not the universe or the toll",
            "the panel is the live ETF universe (survivorship), which is why a signal-free "
            "book still earns -- that is the point of the control",
            "one cadence (20) and one toll (10bp): a sign that moves with either is not "
            "answered here",
        ],
        "evidence_cutoff": str(close.index[-1].date()),
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
    lines = [
        "# ETF book: does the width sign survive a signal-free book on the same panel?",
        "",
        "Panel %d bars x %d names, %s..%s, cadence 20, toll %.0fbp. Real score vs %d seeded"
        % (doc["panel"]["bars"], doc["panel"]["names"], doc["panel"]["first"],
           doc["panel"]["last"], doc["config"]["cost_bp"], n_seeds),
        "random scores on the same eligibility mask.",
        "",
        "| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |",
        "|---|---|---|---|---|---|",
    ]
    for i, w in enumerate(WIDTHS):
        r = reals[str(w)]
        lines.append("| %d | %.2f%% | %.2f%% (%.2f..%.2f) | %+.2fpp | %+.2fpp | %.2f | %.1f%% |"
                     % (w, r["cagr"] * 100, nulls[str(w)] * 100,
                        verdict.get("real_minus_null_pp_per_rung", [None] * 4)[i] or 0.0,
                        spread[str(w)]["min"] * 100, spread[str(w)]["max"] * 100,
                        spread[str(w)]["real_minus_best_null_pp"],
                        r["sharpe"] or 0.0, (r["vol"] or 0.0) * 100))
    lines += ["", "Verdict: **%s**" % verdict["verdict"],
              "rank corr(width, CAGR): real %s / null %s"
              % (verdict.get("real_rank_corr_width_cagr"), verdict.get("null_rank_corr_width_cagr")),
              "", "Reading: " + (
                  "the width direction here is the direction a signal-free book has, so this "
                  "panel cannot credit it to the score; the honest output is 'needs its own "
                  "null', never 'confirmed' (E276 rule 3)."
                  if verdict["verdict"] == "WIDTH_SIGN_IS_THE_NOISE_SIGN" else
                  "the real score's width direction differs from the signal-free book's, so "
                  "the direction is not purely diversification arithmetic on this panel."),
              "", "The null is an estimate: its per-seed range is published, and the last "
              "money column is the gap to its BEST draw (not its median).",
              "", "Cross-rule check (r1291: a width difference means nothing until the "
              "leverage rule is fixed): %s" % cross.get("state"),
              "", "The book in force is width %d; this face does not change it." % N_SELF]
    with open(MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(json.dumps(verdict, ensure_ascii=False))
    print("wrote", OUT)
    return 0


def selftest():
    ok = True

    def chk(name, cond, note=""):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name + (" [" + str(note) + "]" if note else ""))
        ok = ok and bool(cond)

    chk("spearman is +1 on a monotone series",
        abs(spearman([1, 2, 3, 4], [10, 20, 30, 40]) - 1.0) < 1e-12)
    chk("spearman is -1 when the order reverses",
        abs(spearman([1, 2, 3, 4], [40, 30, 20, 10]) + 1.0) < 1e-12)
    chk("spearman refuses a constant series", spearman([1, 1, 1, 1], [1, 2, 3, 4]) is None)
    chk("average ranks break ties symmetrically",
        abs(spearman([1, 2, 2, 3], [1, 2, 2, 3]) - 1.0) < 1e-12)
    chk("sign is three-valued", [sign(1.0), sign(-0.5), sign(0.0), sign(None)] == [1, -1, 0, None])
    widths = (3, 5, 8, 12)
    rising = {str(w): {"cagr": c} for w, c in zip(widths, [0.05, 0.07, 0.09, 0.11])}
    fall = {str(w): c for w, c in zip(widths, [0.02, 0.03, 0.04, 0.05])}
    inv = {str(w): c for w, c in zip(widths, [0.05, 0.04, 0.03, 0.02])}
    v = measure(widths, rising, fall, 10)
    chk("same-sign real and noise reads WIDTH_SIGN_IS_THE_NOISE_SIGN",
        v["verdict"] == "WIDTH_SIGN_IS_THE_NOISE_SIGN", v["verdict"])
    v2 = measure(widths, rising, inv, 10)
    chk("opposite signs read WIDTH_SIGN_DIFFERS_FROM_NOISE",
        v2["verdict"] == "WIDTH_SIGN_DIFFERS_FROM_NOISE", v2["verdict"])
    chk("a rung that never priced is NOT-ASSESSED, never a pass",
        measure(widths, dict(rising, **{"5": {"cagr": None}}), fall, 10)["verdict"] == "NOT-ASSESSED")
    chk("a non-finite rung is NOT-ASSESSED, never a pass",
        measure(widths, dict(rising, **{"8": {"cagr": float("nan")}}), fall, 10)["verdict"]
        == "NOT-ASSESSED")
    chk("the gap column is real minus null per rung",
        measure(widths, rising, fall, 10)["real_minus_null_pp_per_rung"]
        == [3.0, 4.0, 5.0, 6.0])
    class FakeScore:
        pass
    import pandas as pd
    sc = pd.DataFrame([[1.0, np.nan], [2.0, 3.0]], columns=["a", "b"])
    n1 = null_score(sc, 7)
    n2 = null_score(sc, 7)
    chk("the null keeps the eligibility mask and is reproducible by seed",
        bool(n1["b"].isna().iloc[0]) and not bool(n1["b"].isna().iloc[1])
        and n1.equals(n2))
    chk("different seeds draw differently", not null_score(sc, 8).equals(n1))
    import json as _json
    import tempfile
    tdir = tempfile.mkdtemp()
    tp = os.path.join(tdir, "TICKET-x.json")
    with open(tp, "w", encoding="utf-8") as f:
        _json.dump({"width_disclosure": {"square": {"cells": {
            "beta@5": {"cagr": 0.10}, "beta@12": {"cagr": 0.09},
            "vol@5": {"cagr": 0.10}, "vol@12": {"cagr": 0.11}}}}}, f)
    c1 = cross_face_rules(tp, -1)
    chk("a ticket whose two rules disagree is named as such, not averaged",
        c1["state"] == "RULES_DISAGREE_ON_THE_WIDTH_SIGN"
        and c1["rules"]["beta"]["agrees_with_this_face"] is True
        and c1["rules"]["vol"]["agrees_with_this_face"] is False, c1["state"])
    chk("an absent ticket is omitted honestly, never fabricated",
        cross_face_rules(os.path.join(tdir, "nope.json"), -1)["state"] == "omitted")
    print("SELFTEST " + ("OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    seeds = 6
    for a in sys.argv[1:]:
        if a.startswith("--seeds="):
            seeds = int(a.split("=", 1)[1])
    sys.exit(run(seeds))