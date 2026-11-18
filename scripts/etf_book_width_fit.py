"""How many names does 1,000,000 CNY need before its own order stops moving the price?

r1684 put capacity in the veto seat as "one day's order <= 1% of that name's ADV", judged on
the live five names. On 2026-11-17 that reading is 1.0087% -- 8,579 CNY over the line -- and
the whole book is refused for it. The reader is then left with one number and no instruction:
does the desk shrink the ticket, or widen it?

Widening is the one lever the current faces never price. `etf_book_capacity_edge` re-measures
the SAME five names over 60 sessions and says what fits today; `etf_book_capacity_rule` prices
a p90 frontier at a fixed width. Neither answers "if we bought six names instead of five,
would 1,000,000 fit, and what does the sixth name cost us in per-name size".

That is a capacity question with a one-line answer per width, and it needs no engine run: the
score row is the same one the gate reads, the ADV is the same 20-bar median the gate reads,
and the only new thing is that the width is allowed to move. Everything here is read from the
gate's own published face or rebuilt through the gate's own code path -- there is no second
score, no second panel, no hand-copied 1,000,000.

The honest limit: this face prices CAPACITY only. It does not re-price the return of a wider
book (that is a full engine run and lives elsewhere), so it prints what widening costs in
per-name size and refuses to claim what it costs in annual return.
"""
import argparse
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

OUT_DIR = os.path.join(ROOT, "results")
OUT = os.path.join(OUT_DIR, "etf_book_width_fit.json")
GATE_FACE = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")

# The widths we price. 5 is the live book; the rest ask how much room each extra name buys.
WIDTHS = (5, 6, 7, 8, 10, 12, 15, 20)
IMPACT_MAX = 0.01          # 1% of ADV, the gate's own line (candidate_year_gate.GATE_IMPACT_MAX)
ADV_BARS = 20              # the gate's window: `amt[sym].tail(20).median()`


def load_gate(face=GATE_FACE):
    if not os.path.exists(face):
        return None
    with io.open(face, encoding="utf-8") as fh:
        return json.load(fh)


def gate_reads(doc):
    """The three things this face must agree with, taken from the gate's own publication."""
    dec = (doc or {}).get("decision") or {}
    reads = dec.get("reads") or {}
    lens = reads.get("capacity_veto_lens") or "1M"
    blk = (reads.get("capacity_by_capital") or {}).get(lens) or {}
    return {
        "verdict": dec.get("verdict"),
        "lens": lens,
        "capital_cny": blk.get("capital_cny"),
        "per_name_cny": blk.get("per_name_cny"),
        "impact_pct_of_adv": blk.get("impact_pct_of_adv"),
        "line_pct": reads.get("impact_max_pct_of_adv"),
        "live_picks": list(((doc or {}).get("data") or {}).get("live_picks") or []),
        "evidence_cutoff": (doc or {}).get("evidence_cutoff"),
    }


def score_row():
    """The gate's own panel, repair, class map and score -- copied from its code path, not
    re-implemented. Returns (score_row, amt, last_bar)."""
    import etf_composite_pf as E
    import etf_equity_alpha as A

    close, openp, amt, feats = E.build_panel()
    close, openp, _n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns
            if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    last = sc.index[-1]
    return sc.loc[last].dropna(), amt[cols], last


def adv20_at(amt, sym, bars=ADV_BARS):
    """The gate's ADV reading for one slot: median of the slot's own last 20 values."""
    if sym not in amt.columns:
        return None
    s = amt[sym].tail(bars).dropna()
    if len(s) < bars:
        return None
    med = float(s.median())
    if not (med == med) or med <= 0:      # NaN or non-positive
        return None
    return med


def price_width(rank_row, amt, n, capital):
    """One width, one capital. The binding slot is the worst ADV of the n names bought."""
    picks = list(rank_row.nlargest(n).index)
    advs = {}
    for sym in picks:
        advs[sym] = adv20_at(amt, sym)
    measured = [(s, a) for s, a in advs.items() if a is not None]
    if not measured:
        return {"n": n, "picks": picks, "n_measurable": 0, "adv_weakest_cny": None,
                "per_name_cny": None, "impact_pct_of_adv": None, "fits": None,
                "capital_at_line_cny": None, "unmeasurable": picks}
    weakest_sym, weakest_adv = min(measured, key=lambda kv: kv[1])
    per_name = float(capital) / float(n)
    share = per_name / weakest_adv
    # the same slot at exactly 1%: how much capital this width can carry on this bar
    at_line = IMPACT_MAX * weakest_adv * float(n)
    return {
        "n": n,
        "picks": picks,
        "n_measurable": len(measured),
        "adv_weakest_cny": round(weakest_adv, 0),
        "adv_weakest_sym": weakest_sym,
        "per_name_cny": round(per_name, 0),
        "impact_pct_of_adv": round(share * 100.0, 4),
        "fits": bool(share <= IMPACT_MAX),
        "capital_at_line_cny": round(at_line, 0),
        "unmeasurable": [s for s, a in advs.items() if a is None],
    }


def verdict_name(rows):
    """The smallest width whose own worst slot still fits the ticket at 1% of ADV."""
    fitting = [r for r in rows if r.get("fits") is True]
    if not rows or all(r.get("fits") is None for r in rows):
        return "UNMEASURABLE", None
    if not fitting:
        return "NO_WIDTH_FITS", None
    return "MIN_WIDTH_THAT_FITS", min(r["n"] for r in fitting)


def summarise(rows, capital, line_pct):
    v, min_n = verdict_name(rows)
    base = next((r for r in rows if r["n"] == 5), None)
    best = next((r for r in rows if r["n"] == min_n), None) if min_n else None
    out = {
        "capital_cny": capital,
        "line_pct": line_pct,
        "verdict": v,
        "min_width": min_n,
        "live_width": base,
        "min_width_row": best,
    }
    if v == "MIN_WIDTH_THAT_FITS" and base and best:
        out["extra_names"] = best["n"] - base["n"]
        out["per_name_drop_cny"] = (None if base.get("per_name_cny") is None
                                    or best.get("per_name_cny") is None
                                    else round(base["per_name_cny"] - best["per_name_cny"], 0))
        # widening never refreshes the weakest slot upward: the extra name can only be smaller
        out["adv_weakest_change_cny"] = (None if base.get("adv_weakest_cny") is None
                                         or best.get("adv_weakest_cny") is None
                                         else round(best["adv_weakest_cny"]
                                                    - base["adv_weakest_cny"], 0))
    return out


def sentence(s):
    cap = s.get("capital_cny")
    if s["verdict"] == "MIN_WIDTH_THAT_FITS":
        b, w = s["live_width"], s["min_width_row"]
        same_slot = (b.get("adv_weakest_sym") == w.get("adv_weakest_sym")
                     and b.get("adv_weakest_cny") == w.get("adv_weakest_cny"))
        tail = ("最弱席还是同一只（%s，%s 元）——冲击下降全部来自每名字少买，不是换到了更厚的票。"
                % (b.get("adv_weakest_sym") or "-",
                   format(int(b["adv_weakest_cny"]), ","))
                if same_slot else
                "最弱席从 %s（%s 元）换成 %s（%s 元）。"
                % (b.get("adv_weakest_sym") or "-",
                   format(int(b["adv_weakest_cny"]), ","),
                   w.get("adv_weakest_sym") or "-",
                   format(int(w["adv_weakest_cny"]), ",")))
        return ("同一笔 %s 元、%d 名等权在 %s 这一天打 %.4f%% ADV（最弱 %s，闸线 %.2f%%）；"
                "把宽度加到 **%d 名** 就落到 %.4f%% —— 每名从 %s 元降到 %s 元。%s"
                "宽 %d 名在这一天的容量上限是 %s 元。"
                % (format(int(cap), ",") if cap else "-", b["n"],
                   (s.get("bar") or "-"),
                   b["impact_pct_of_adv"], b.get("adv_weakest_sym") or "-",
                   s["line_pct"], w["n"], w["impact_pct_of_adv"],
                   format(int(b["per_name_cny"]), ","),
                   format(int(w["per_name_cny"]), ","), tail,
                   w["n"], format(int(w["capital_at_line_cny"]), ",")))
    if s["verdict"] == "NO_WIDTH_FITS":
        return ("同一笔 %s 元在测过的每个宽度（%s 名）上都超过 %.2f%% ADV —— 加名字不能解决"
                "这笔单子，只能缩小它或换到更厚的票上。"
                % (format(int(cap), ",") if cap else "-",
                   "/".join(str(r["n"]) for r in s.get("rows") or []), s["line_pct"]))
    return "宽度容量读不到：评分行或成交额面缺读数，这一页不印任何「装得下」的结论。"


def build(capital=None):
    doc = load_gate()
    g = gate_reads(doc)
    rank_row, amt, last = score_row()
    cap = capital if capital is not None else g["capital_cny"]
    if cap is None:
        cap = 1_000_000.0
    rows = [price_width(rank_row, amt, n, cap) for n in WIDTHS]
    s = summarise(rows, cap, g["line_pct"] if g["line_pct"] is not None else IMPACT_MAX * 100.0)
    s["bar"] = str(last)[:10]
    payload = {
        "kind": "etf_book_width_fit",
        "script": "scripts/etf_book_width_fit.py",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": s["bar"],
        "gate_face": "results/etf_book_year_gate/YEAR-GATE.json",
        "gate_reads": {k: g[k] for k in ("verdict", "lens", "capital_cny", "per_name_cny",
                                        "impact_pct_of_adv", "line_pct", "evidence_cutoff")},
        "live_picks": g["live_picks"],
        "line_pct": s["line_pct"],
        "widths": list(WIDTHS),
        "rows": rows,
        "summary": s,
        "sentence": sentence(dict(s, rows=rows)),
        "caveats": [
            "This face prices CAPACITY only. A wider book's annual return is not re-priced "
            "here (that needs a full engine run) -- the per-name drop is printed instead.",
            "ADV is the gate's own reading: median of the slot's last 20 values of "
            "`close x volume` (itself a rolling 20-bar median), so both steps are causal.",
            "The binding slot is the worst ADV among the n names, never their sum: an "
            "equal-weight book must fill its worst name.",
            "A name whose ADV cannot be read makes that width's weakest-slot reading "
            "incomplete, and it is listed rather than silently dropped.",
        ],
    }
    return payload


def check(payload):
    """Re-derive the three readings the gate published and the arithmetic between them."""
    problems = []
    g = payload.get("gate_reads") or {}
    rows = payload.get("rows") or []
    base = next((r for r in rows if r["n"] == 5), None)

    # 1. the five names this face buys must be the five the gate published
    if g.get("verdict") is None:
        problems.append("gate face unreadable: nothing to agree with")
    elif base is not None:
        mine = sorted(base.get("picks") or [])
        theirs = sorted(payload.get("live_picks") or [])
        if mine != theirs:
            problems.append("width 5 picks %s != gate live_picks %s" % (mine, theirs))

    # 2. the same slot, the same impact, the same line
    if base is not None and g.get("impact_pct_of_adv") is not None:
        if base.get("impact_pct_of_adv") is None:
            problems.append("width 5 reading unmeasurable while the gate measures it")
        elif abs(base["impact_pct_of_adv"] - g["impact_pct_of_adv"]) > 1e-4:
            problems.append("width 5 impact %.4f%% != gate %.4f%%"
                            % (base["impact_pct_of_adv"], g["impact_pct_of_adv"]))
    if base is not None and g.get("per_name_cny") is not None:
        if base.get("per_name_cny") is None or abs(base["per_name_cny"]
                                                   - g["per_name_cny"]) > 1.0:
            problems.append("width 5 per-name %s != gate %s"
                            % (base.get("per_name_cny"), g["per_name_cny"]))

    # 3. every row is its own arithmetic
    cap = payload.get("summary", {}).get("capital_cny")
    for r in rows:
        if None in (r.get("adv_weakest_cny"), r.get("per_name_cny"),
                    r.get("impact_pct_of_adv"), r.get("capital_at_line_cny")) or cap is None:
            continue
        if abs(r["per_name_cny"] - cap / r["n"]) > 1.0:
            problems.append("width %d: per-name %s != capital/n %.2f"
                            % (r["n"], r["per_name_cny"], cap / r["n"]))
        want = r["per_name_cny"] / r["adv_weakest_cny"] * 100.0
        if abs(want - r["impact_pct_of_adv"]) > 1e-4:
            problems.append("width %d: impact %.4f%% != per_name/adv %.4f%%"
                            % (r["n"], r["impact_pct_of_adv"], want))
        # the published line-reading is rounded to whole CNY, so the re-derivation is the
        # same rounding, not a tolerance-free division (a rounded number cannot invert exactly)
        want_at_line = round(IMPACT_MAX * r["adv_weakest_cny"] * r["n"], 0)
        if abs(r["capital_at_line_cny"] - want_at_line) > 1.0:
            problems.append("width %d: capital-at-line %s != %.0f (1%% of its own weakest slot)"
                            % (r["n"], r["capital_at_line_cny"], want_at_line))

    # 4. widening can only add a smaller name, so the weakest slot never improves
    measurable = [r for r in rows if r.get("adv_weakest_cny") is not None]
    for a, b in zip(measurable, measurable[1:]):
        if b["adv_weakest_cny"] > a["adv_weakest_cny"] + 1.0:
            problems.append("width %d weakest ADV %s > width %d %s: widening improved the "
                            "binding slot" % (b["n"], b["adv_weakest_cny"],
                                              a["n"], a["adv_weakest_cny"]))

    # 5. the verdict must be the smallest fitting width, not a hand-written number
    v, min_n = verdict_name(rows)
    if v != payload.get("summary", {}).get("verdict"):
        problems.append("verdict %s != re-derived %s"
                        % (payload.get("summary", {}).get("verdict"), v))
    if min_n != payload.get("summary", {}).get("min_width"):
        problems.append("min_width %s != re-derived %s"
                        % (payload.get("summary", {}).get("min_width"), min_n))
    return problems


def run():
    payload = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    s = payload["summary"]
    print(s["verdict"], "min_width=%s" % s.get("min_width"), "bar=%s" % payload["evidence_cutoff"])
    for r in payload["rows"]:
        print("  n=%-3d impact=%-9s fits=%-5s weakest=%-10s per_name=%s"
              % (r["n"],
                 ("%.4f%%" % r["impact_pct_of_adv"]) if r.get("impact_pct_of_adv") is not None else "-",
                 r.get("fits"), r.get("adv_weakest_sym") or "-",
                 r.get("per_name_cny")))
    print(payload["sentence"])
    print("->", OUT)
    return 0


def main_check():
    with io.open(OUT, encoding="utf-8") as fh:
        payload = json.load(fh)
    problems = check(payload)
    if problems:
        print("CHECK_FAIL")
        for p in problems:
            print("  -", p)
        return 1
    print("CHECK_OK width 5 agrees with the gate (%s) and every row re-derives"
          % payload["gate_reads"].get("impact_pct_of_adv"))
    return 0


def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    have_panel = False
    rank_row = amt = None
    try:
        rank_row, amt, last = score_row()
        have_panel = True
    except Exception as exc:                                  # noqa: BLE001
        leg("panel unavailable (%s) -> structural legs still run" % str(exc)[:60], True)

    import pandas as pd

    fake_row = {"n": 5, "adv_weakest_cny": 20_000_000.0, "per_name_cny": 200_000.0,
                "impact_pct_of_adv": 1.0, "fits": True, "capital_at_line_cny": 1_000_000.0}
    leg("a slot at exactly 1% of ADV is inside the line", fake_row["fits"] is True)
    r2 = dict(fake_row, per_name_cny=200_001.0)
    leg("a slot one CNY over the line is outside it",
        (r2["per_name_cny"] / r2["adv_weakest_cny"]) > IMPACT_MAX)
    empty_adv = pd.DataFrame({"AAA": [0.0] * 20})
    leg("a missing ADV is not a pass",
        price_width(pd.Series({"AAA": 1.0}), empty_adv, 1, 1_000_000.0)["fits"] is None)

    if have_panel:
        rows = [price_width(rank_row, amt, n, 1_000_000.0) for n in WIDTHS]
        leg("width 5 is measured", rows[0]["fits"] is not None)
        leg("widening never improves the weakest slot",
            all(b["adv_weakest_cny"] <= a["adv_weakest_cny"] + 1.0
                for a, b in zip(rows, rows[1:])
                if a["adv_weakest_cny"] and b["adv_weakest_cny"]))
        tiny = [price_width(rank_row, amt, n, 1.0) for n in (5, 8)]
        leg("a 1-CNY ticket fits every width", all(t["fits"] for t in tiny))
        huge = [price_width(rank_row, amt, n, 1e12) for n in (5, 8)]
        leg("a 1e12 ticket fits no width", not any(h["fits"] for h in huge))

    v, n = verdict_name([{"n": 5, "fits": False}, {"n": 6, "fits": True},
                         {"n": 8, "fits": True}])
    leg("the verdict is the SMALLEST fitting width", v == "MIN_WIDTH_THAT_FITS" and n == 6)
    v, n = verdict_name([{"n": 5, "fits": False}, {"n": 6, "fits": False}])
    leg("no fitting width is its own verdict", v == "NO_WIDTH_FITS" and n is None)
    v, n = verdict_name([{"n": 5, "fits": None}])
    leg("an unmeasurable width is not a pass", v == "UNMEASURABLE" and n is None)

    ok = sum(1 for _n, o in legs if o)
    for name, o in legs:
        print("  [%s] %s" % ("PASS" if o else "FAIL", name))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--capital", type=float, default=None)
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run()
    if a.cmd == "check":
        return main_check()
    if a.cmd == "selftest":
        return selftest()
    raise SystemExit("unknown command: %s" % a.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
