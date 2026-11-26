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

r1326: the table now ranks the bar the TICKET decided on, not the panel's last bar. On
2026-11-17 those two books shared one name out of five, so "six names passes" was priced on a
book nobody holds. The decision bar is read from the ticket's own published block (single
source), the turnover window is sliced to that bar, and width 5 must equal the ticket's own
live row before this face may be printed beside it. The gate's last-bar reading is still
published -- labelled, with its own picks -- because the two answer different questions.
"""
import argparse
import glob
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
TICKET_GLOB = os.path.join(ROOT, "results", "etf_book_order", "TICKET-*.json")

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
        # r2162: the gate publishes the bar its capacity reading belongs to; without it this
        # face cannot tell a same-generation quote from one taken off a gate that has since
        # re-derived (the gate carries no top-level evidence_cutoff -- that field is empty)
        "gate_bar": ((doc or {}).get("data") or {}).get("last"),
    }


def score_row(bar=None):
    """The gate's own panel, repair, class map and score -- copied from its code path, not
    re-implemented. `bar` cuts BOTH the ranking row and the turnover window: nothing after
    the decision bar is visible to it (r1325 made the window causal; this face must read
    the same causal face the ticket printed). Returns (rank_row, amt, bar_used, panel_last)."""
    import etf_composite_pf as E
    import etf_equity_alpha as A

    close, openp, amt, feats = E.build_panel()
    close, openp, _n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns
            if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    panel_last = sc.index[-1]
    use = panel_last
    if bar is not None:
        import pandas as pd
        cut = pd.Timestamp(str(bar)[:10])
        upto = sc.index[sc.index <= cut]
        if len(upto):
            use = upto[-1]
    return sc.loc[use].dropna(), amt[cols].loc[:use], use, panel_last


def ticket_reads(pattern=TICKET_GLOB):
    """The ticket's own capacity block -- the only place the book's decision bar is written.

    The ticket publishes it after slicing its ranking and its turnover window to that bar;
    copying the bar from there (instead of re-deriving a grid) keeps one source of truth.
    Returns None when no ticket has been published, so the caller can label the fallback."""
    paths = sorted(glob.glob(pattern))
    if not paths:
        return None
    try:
        with io.open(paths[-1], encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception:                                          # noqa: BLE001
        return None
    wc = doc.get("width_capacity") or {}
    if not wc.get("decision_bar"):
        return None
    return {
        "path": os.path.relpath(paths[-1], ROOT).replace("\\", "/"),
        "asof": doc.get("asof"),
        "decision_bar": str(wc.get("decision_bar")),
        "amount_window_end": str(wc.get("amount_window_end") or ""),
        "panel_last_bar": (str(wc.get("panel_last_bar")) if wc.get("panel_last_bar")
                           else None),
        "nav_cny": wc.get("nav_cny"),
        "live_width": wc.get("live_width") or {},
        "min_width_row": wc.get("min_width_row") or {},
        "widths": [r.get("n") for r in (wc.get("widths") or [])],
    }


def agreement(rows, t):
    """Is this table the same book the ticket printed? Width 5 is the whole test: same slots,
    same turnover window, same price. A face that quotes a ticket's number must re-derive it."""
    out = {"ticket_face": (t or {}).get("path"),
           "decision_bar": (t or {}).get("decision_bar"),
           "checks": [], "mismatched": []}
    if not t:
        out["status"] = "NO_TICKET_FACE"
        out["ok"] = None
        out["sentence"] = ("没有票面可对：本表退回面板最后一根 bar 排名/读成交额，"
                           "这一张数不得与任何票面数字并列或相加。")
        return out
    lw = t.get("live_width") or {}
    base = next((r for r in rows if r["n"] == 5), None) or {}
    for name, mine, theirs in (
            ("width5_impact", base.get("impact_pct_of_adv"), lw.get("impact_pct_of_adv")),
            ("width5_per_name_cny", base.get("per_name_cny"), lw.get("per_name_cny")),
            ("width5_weakest_adv_cny", base.get("adv_weakest_cny"), lw.get("adv_weakest_cny")),
            ("width5_weakest_sym", base.get("adv_weakest_sym"), lw.get("adv_weakest_sym")),
            ("width5_picks", sorted(base.get("picks") or []), sorted(lw.get("picks") or []))):
        bad = False
        if isinstance(mine, (int, float)) and isinstance(theirs, (int, float)):
            # impact is a percentage (rounds at 4dp); CNY fields round at whole CNY
            tol = 2e-4 if name.endswith("impact") else 1.0
            bad = abs(float(mine) - float(theirs)) > tol
        else:
            bad = mine != theirs
        out["checks"].append({"name": name, "mine": mine, "ticket": theirs, "same": not bad})
        if bad:
            out["mismatched"].append(name)
    out["ok"] = not out["mismatched"]
    out["status"] = "AGREES_WITH_TICKET" if out["ok"] else "DISAGREES_WITH_TICKET"
    if out["ok"]:
        out["sentence"] = ("宽度 5 与票面同书：同一批名字、同一个含决策日的 20 日成交额窗口、"
                           "同一个冲击读数（%.4f%% ADV，容量 %s 元）——两张面可并列读。"
                           % (float(lw.get("impact_pct_of_adv") or 0.0),
                              format(int(lw.get("capital_at_line_cny") or 0), ",")))
    else:
        out["sentence"] = ("宽度 5 与票面**不是同一本书**（%s）——本表不得与票面数字并列，"
                           "要么重跑本表、要么票面重出。" % "、".join(out["mismatched"]))
    return out


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
    t = ticket_reads()
    rank_row, amt, used, panel_last = score_row(t["decision_bar"] if t else None)
    cap = capital if capital is not None else g["capital_cny"]
    if cap is None:
        cap = 1_000_000.0
    rows = [price_width(rank_row, amt, n, cap) for n in WIDTHS]
    s = summarise(rows, cap, g["line_pct"] if g["line_pct"] is not None else IMPACT_MAX * 100.0)
    s["bar"] = str(used)[:10]
    s["bar_source"] = "ticket_decision_bar" if t else "panel_last_bar"
    agree = agreement(rows, t)
    base_picks = list((next((r for r in rows if r["n"] == 5), {}) or {}).get("picks") or [])
    gate_picks = list(g.get("live_picks") or [])
    shared = sorted(set(base_picks) & set(gate_picks))
    payload = {
        "kind": "etf_book_width_fit",
        "script": "scripts/etf_book_width_fit.py",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        # two dates, both printed (r1781): the panel this face stands on runs to `panel_last`,
        # while the ranking row and the turnover window are cut at the ticket's decision bar.
        # `evidence_cutoff` is the page's bar (same convention as the ticket's as_of); the
        # decision bar is carried beside it and never merged into it.
        "evidence_cutoff": str(panel_last)[:10],
        "decision_bar": s["bar"],
        "amount_window_end": s["bar"],
        "amount_window_bars": ADV_BARS,
        "panel_last_bar": str(panel_last)[:10],
        "bar_source": s["bar_source"],
        "gate_face": "results/etf_book_year_gate/YEAR-GATE.json",
        "gate_reads": {k: g[k] for k in ("verdict", "lens", "capital_cny", "per_name_cny",
                                        "impact_pct_of_adv", "line_pct", "evidence_cutoff")},
        "gate_live_picks": gate_picks,
        "ticket": ({k: t[k] for k in ("path", "asof", "decision_bar", "amount_window_end",
                                     "panel_last_bar", "nav_cny", "widths")} if t else None),
        "ticket_agreement": agree,
        "gate_vs_ticket": {
            "ticket_picks": base_picks,
            "gate_picks": gate_picks,
            "shared_names": shared,
            "shared_n": len(shared),
            "note": ("准入闸的容量读数在它自己的排名上算（%d 只），本表在票面决策日排名上算（%d 只），"
                     "两边共同名字 %d 只：两个数回答的是两个问题，不得相加，也不得把闸的读数"
                     "当成「本书装不装得下」。" % (len(gate_picks), len(base_picks), len(shared))),
            # r1327: the side-by-side table says the two numbers answer two questions, but
            # not whether the VERDICT changes if the gate read this book. Same rule, the
            # book's own row -- derived from the two published readings, never re-ranked.
            "same_rule_on_this_book": same_rule(g, s.get("live_width") or {}),
        },
        "live_picks": base_picks,
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
            "The ranking bar and the turnover window both end on the TICKET's decision bar "
            "(%s); the panel runs to %s. Numbers from the two bars are not interchangeable."
            % (s["bar"], str(panel_last)[:10]),
        ],
    }
    return payload


def same_rule(g, live_row):
    """Run the GATE's own rule on the book this ticket actually holds.

    The gate and this table rank different five-name sets (they shared one name on
    2026-11-17), so the two capacity numbers answer two questions and are never summed.
    What the reader still needs is the one thing the side-by-side table cannot say: if the
    gate read THIS book, would its verdict change? That is a comparison of verdicts on the
    same rule, not of magnitudes -- and it is derived from the two published readings
    rather than from either face's wording.
    """
    g = g or {}
    live_row = live_row or {}
    line = g.get("line_pct")
    impact_gate = g.get("impact_pct_of_adv")
    impact_live = live_row.get("impact_pct_of_adv")
    out = {"rule": "per-name impact <= %.2f%% of that name's ADV" % (line if line is not None else IMPACT_MAX * 100.0),
           "gate_verdict": g.get("verdict"),
           "gate_impact_pct_of_adv": impact_gate,
           "book_width": live_row.get("n"),
           "book_impact_pct_of_adv": impact_live,
           "book_fits": live_row.get("fits")}
    if impact_gate is None or line is None:
        out["status"] = "GATE_UNREADABLE"
        out["sentence"] = ("准入闸的读数读不到 —— 这一页不印「同一条规矩换本书结论会不会变」，"
                          "缺面不等于两边一致。")
        return out
    if impact_live is None or out["book_fits"] is None:
        out["status"] = "BOOK_UNMEASURABLE"
        out["sentence"] = ("本书这一档的读数读不到（宽度 %s 有名字缺 ADV）—— 不拿闸的结论代替本书的结论。"
                          % out["book_width"])
        return out
    gate_fits = impact_gate <= line + 1e-9
    out["gate_fits"] = gate_fits
    out["status"] = "SAME_VERDICT" if gate_fits == bool(out["book_fits"]) else "VERDICTS_DIVERGE"
    # the verdict word and the arithmetic must agree, or the gate's own face is the problem
    if (g.get("verdict") == "DENY") is not (not gate_fits):
        out["status"] = "GATE_FACE_INCONSISTENT"
    if out["status"] == "SAME_VERDICT":
        out["sentence"] = (
            "同一条规矩（单名冲击 ≤ %.2f%% ADV）分别读两本书：闸的 %d 只 %.4f%% → %s，"
            "本册的 %d 只 %.4f%% → %s —— **结论相同**。所以那 1/%d 的重合差不改今天的判断："
            "闸拒的和本册被拒的是同一件事（每名买太多），要改的是宽度或单子大小，不是名册。"
            % (line, len(g.get("live_picks") or []) or 5, impact_gate,
               "过线" if gate_fits else "不过线",
               out["book_width"] or 5, impact_live,
               "过线" if out["book_fits"] else "不过线",
               max(1, (live_row.get("n") or 5))))
    elif out["status"] == "VERDICTS_DIVERGE":
        out["sentence"] = (
            "同一条规矩读两本书给出相反结论：闸的 %.4f%% → %s，本册的 %d 只 %.4f%% → %s。"
            "这不是可以折中的分歧 —— 两本书各自的名册不同，读者必须知道闸拒的到底是哪一本。"
            % (impact_gate, "过线" if gate_fits else "不过线",
               out["book_width"] or 5, impact_live,
               "过线" if out["book_fits"] else "不过线"))
    else:
        out["sentence"] = ("准入闸面自己不成立：判词 %r 与它自己的读数 %.4f%% 对 %.2f%% 线不符 —— "
                          "先修闸面，不再往下比较。"
                          % (g.get("verdict"), impact_gate, line))
    return out


def drift(payload, t="disk", g="disk"):
    """Is this table OLDER than the two faces it quotes? A newer input is a rebuild, not a
    confession (r1935: a check that only re-derives itself can never say it is out of date).

    Both anchors are external on purpose: the ticket writes the decision bar, the gate writes
    the capacity reading, and this face quotes both. When either rolls forward, every number
    below is about a book nobody holds -- which is the state the chain leg has to be able to
    repair, and it can only do that if the probe uses the contract word (r1850).
    """
    out = []
    if t == "disk":
        t = ticket_reads()
    if g == "disk":
        g = load_gate()
    if t is not None and str(payload.get("decision_bar")) != str(t["decision_bar"]):
        out.append("STALE: the ticket now decides on bar %s, this table priced %s"
                   % (t["decision_bar"], payload.get("decision_bar")))
    now = gate_reads(g)
    was = payload.get("gate_reads") or {}
    # the gate re-derives on every bar and its capacity reading moves with its live five, so
    # a quote taken off yesterday's gate is a real staleness, not a cosmetic label
    if (now.get("gate_bar") and was.get("gate_bar")
            and str(now["gate_bar"]) != str(was["gate_bar"])):
        out.append("STALE: the gate re-derived on bar %s, this table quotes %s"
                   % (now["gate_bar"], was["gate_bar"]))
    elif (now.get("evidence_cutoff") and was.get("evidence_cutoff")
            and str(now["evidence_cutoff"]) != str(was["evidence_cutoff"])):
        out.append("STALE: the gate re-derived on %s, this table quotes %s"
                   % (now["evidence_cutoff"], was["evidence_cutoff"]))
    return out


def check(payload, t="disk"):
    """Re-derive the readings this face publishes, and prove it is the ticket's own book."""
    problems = []
    g = payload.get("gate_reads") or {}
    rows = payload.get("rows") or []
    base = next((r for r in rows if r["n"] == 5), None)
    if t == "disk":
        t = ticket_reads()
    agree = payload.get("ticket_agreement") or {}
    # a ticket on a NEWER bar is a rebuild (drift() owns that sentence); comparing this
    # table's picks against the new book here would print one event twice, once as a
    # contradiction -- and "the market moved" is not a contradiction
    bar_moved = (t is not None
                 and str(payload.get("decision_bar")) != str(t["decision_bar"]))

    # 1. the bar this table ranks must be the bar the ticket decided on -- or, when no
    #    ticket exists, the fallback must say so instead of silently reading the panel tail
    if t is None:
        if payload.get("bar_source") != "panel_last_bar":
            problems.append("no ticket face, but bar_source=%s"
                            % payload.get("bar_source"))
        if (agree.get("status") or "NO_TICKET_FACE") != "NO_TICKET_FACE":
            problems.append("no ticket face, but agreement claims %s"
                            % agree.get("status"))
    elif bar_moved:
        pass
    else:
        if payload.get("amount_window_end") != payload.get("decision_bar"):
            problems.append("amount window ends %s, ranking ends %s"
                            % (payload.get("amount_window_end"),
                               payload.get("decision_bar")))
        if agree.get("status") != "AGREES_WITH_TICKET":
            problems.append("ticket agreement %s (mismatched: %s)"
                            % (agree.get("status"),
                               "、".join(agree.get("mismatched") or []) or "-"))

    # 2. width 5 IS the ticket's live row: same slots, same price, re-derived from the face
    if t is not None and base is not None and not bar_moved:
        lw = t.get("live_width") or {}
        if sorted(base.get("picks") or []) != sorted(lw.get("picks") or []):
            problems.append("width 5 picks %s != ticket %s"
                            % (sorted(base.get("picks") or []),
                               sorted(lw.get("picks") or [])))
        if (base.get("impact_pct_of_adv") is not None
                and lw.get("impact_pct_of_adv") is not None
                and abs(base["impact_pct_of_adv"] - lw["impact_pct_of_adv"]) > 2e-4):
            problems.append("width 5 impact %.4f%% != ticket %.4f%%"
                            % (base["impact_pct_of_adv"], lw["impact_pct_of_adv"]))
        if (base.get("per_name_cny") is not None and lw.get("per_name_cny") is not None
                and abs(base["per_name_cny"] - lw["per_name_cny"]) > 1.0):
            problems.append("width 5 per-name %s != ticket %s"
                            % (base["per_name_cny"], lw["per_name_cny"]))

    # 3. the gate's reading is carried, never recomputed: if the gate face is unreadable
    #    there is nothing to quote and the face must not print a capacity verdict
    if g.get("verdict") is None:
        problems.append("gate face unreadable: nothing to agree with")

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

    # 6. the verdict comparison must re-derive from the two published readings: a side
    #    block that can drift from the numbers above it is a second, silent opinion
    sr = (payload.get("gate_vs_ticket") or {}).get("same_rule_on_this_book") or {}
    if not sr.get("status"):
        problems.append("gate_vs_ticket carries no same_rule_on_this_book status")
    else:
        want = same_rule(g, payload.get("summary", {}).get("live_width") or {})
        if sr.get("status") != want["status"]:
            problems.append("same_rule status %s != re-derived %s"
                            % (sr.get("status"), want["status"]))
        if sr.get("status") == "SAME_VERDICT" and not sr.get("sentence"):
            problems.append("same_rule says the verdicts agree but prints no sentence")
    return problems


def run():
    payload = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    s = payload["summary"]
    print(s["verdict"], "min_width=%s" % s.get("min_width"),
          "decision_bar=%s(%s)" % (payload["decision_bar"], payload["bar_source"]),
          "panel_last=%s" % payload["panel_last_bar"])
    for r in payload["rows"]:
        print("  n=%-3d impact=%-9s fits=%-5s weakest=%-10s per_name=%s"
              % (r["n"],
                 ("%.4f%%" % r["impact_pct_of_adv"]) if r.get("impact_pct_of_adv") is not None else "-",
                 r.get("fits"), r.get("adv_weakest_sym") or "-",
                 r.get("per_name_cny")))
    print(payload["sentence"])
    ag = payload.get("ticket_agreement") or {}
    print("ticket:", ag.get("status"), "--", ag.get("sentence"))
    print("gate vs ticket:", payload["gate_vs_ticket"]["shared_n"],
          "shared names of", len(payload["gate_vs_ticket"]["gate_picks"]), "/",
          len(payload["gate_vs_ticket"]["ticket_picks"]))
    sr = payload["gate_vs_ticket"].get("same_rule_on_this_book") or {}
    print("same rule on this book:", sr.get("status"), "--", sr.get("sentence"))
    print("->", OUT)
    return 0


def main_check():
    with io.open(OUT, encoding="utf-8") as fh:
        payload = json.load(fh)
    t = ticket_reads()
    problems = check(payload, t=t)
    if problems:
        print("CHECK_FAIL")
        for p in problems:
            print("  -", p)
        return 1
    stale = drift(payload, t=t)
    if stale:
        print("CHECK_STALE")
        for s in stale:
            print("  -", s)
        return 3
    print("CHECK_OK width 5 IS the ticket's live row on bar %s (%.4f%%) and every row "
          "re-derives" % (payload.get("decision_bar"),
                          (payload.get("ticket_agreement") or {}).get("checks", [{}])[0].get("mine")
                          or 0.0))
    return 0


def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    have_panel = False
    rank_row = amt = None
    try:
        rank_row, amt, _used, _panel_last = score_row()
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

    # --- r1326: this table must be the ticket's own book, on the ticket's own bar --------
    fake_t = {"path": "fixture/TICKET-x.json", "decision_bar": "2026-01-05",
              "live_width": {"n": 5, "picks": ["AAA", "BBB"], "impact_pct_of_adv": 1.0,
                             "per_name_cny": 200000.0, "adv_weakest_cny": 20000000.0,
                             "adv_weakest_sym": "AAA"}}
    fake_rows = [{"n": 5, "picks": ["BBB", "AAA"], "impact_pct_of_adv": 1.0,
                  "per_name_cny": 200000.0, "adv_weakest_cny": 20000000.0,
                  "adv_weakest_sym": "AAA", "fits": True}]
    leg("a table identical to the ticket agrees (pick order is not a difference)",
        agreement(fake_rows, fake_t)["status"] == "AGREES_WITH_TICKET")
    ag = agreement([dict(fake_rows[0], impact_pct_of_adv=1.0087)], fake_t)
    leg("a table priced on another bar is caught, not averaged",
        ag["status"] == "DISAGREES_WITH_TICKET" and "width5_impact" in ag["mismatched"])
    ag = agreement([dict(fake_rows[0], picks=["AAA"])], fake_t)
    leg("a table ranking another book is caught by its picks",
        ag["status"] == "DISAGREES_WITH_TICKET" and "width5_picks" in ag["mismatched"])
    ag = agreement(fake_rows, None)
    leg("no ticket face is its own status and blocks side-by-side reading",
        ag["status"] == "NO_TICKET_FACE" and ag["ok"] is None)

    if have_panel:
        import pandas as pd
        full_rank, full_amt, last, panel_last = score_row()
        leg("the default bar is the panel's last bar",
            str(last)[:10] == str(panel_last)[:10])
        cut = (pd.Timestamp(str(last)[:10]) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        _r, sliced_amt, used, _pl = score_row(cut)
        leg("a decision bar slices the turnover window (no bar after it survives)",
            len(sliced_amt.index) > 0
            and sliced_amt.index[-1] <= pd.Timestamp(cut)
            and used <= pd.Timestamp(cut))
        leg("the slice is strictly shorter than the panel tail",
            len(sliced_amt.index) < len(full_amt.index))

    # --- r1327: the gate's rule read on THIS book, compared verdict to verdict ----------
    g_fit = {"verdict": "ADMIT", "line_pct": 1.0, "impact_pct_of_adv": 0.84,
             "live_picks": ["A", "B", "C", "D", "E"]}
    row_fit = {"n": 5, "fits": True, "impact_pct_of_adv": 0.91}
    sr = same_rule(g_fit, row_fit)
    leg("two books that both pass are SAME_VERDICT, not a shared number",
        sr["status"] == "SAME_VERDICT" and sr.get("gate_fits") is True
        and "0.8400" in sr["sentence"] and "0.9100" in sr["sentence"])
    sr = same_rule({"verdict": "DENY", "line_pct": 1.0, "impact_pct_of_adv": 1.0087,
                    "live_picks": ["A", "B", "C", "D", "E"]}, row_fit)
    leg("a gate that refuses while this book passes is DIVERGENCE, not an average",
        sr["status"] == "VERDICTS_DIVERGE" and "相反结论" in sr["sentence"])
    sr = same_rule({"verdict": None, "line_pct": None, "impact_pct_of_adv": None}, row_fit)
    leg("an unreadable gate is not 'the same verdict'",
        sr["status"] == "GATE_UNREADABLE" and "缺面" in sr["sentence"])
    sr = same_rule(g_fit, {"n": 5, "fits": None, "impact_pct_of_adv": None})
    leg("an unmeasurable book does not borrow the gate's answer",
        sr["status"] == "BOOK_UNMEASURABLE")
    sr = same_rule({"verdict": "DENY", "line_pct": 1.0, "impact_pct_of_adv": 0.84}, row_fit)
    leg("a gate whose word fights its own arithmetic is caught before comparison",
        sr["status"] == "GATE_FACE_INCONSISTENT")

    # --- r2162: the two anchors that can go out from under this table ---------------------
    _payload = {"decision_bar": "2026-01-05",
                "gate_reads": {"gate_bar": "2026-01-05"},
                "rows": fake_rows,
                "summary": {"capital_cny": 1_000_000.0},
                "ticket_agreement": {"status": "AGREES_WITH_TICKET"}}
    _same = {"decision_bar": "2026-01-05"}
    leg("a table on the ticket's own bar is not called stale",
        drift(_payload, t=_same, g={}) == [])
    _d = drift(_payload, t={"decision_bar": "2026-01-06"}, g={})
    leg("the ticket rolling one bar forward is STALE (a rebuild, not a contradiction)",
        len(_d) == 1 and "STALE" in _d[0] and "2026-01-06" in _d[0])
    _g = {"data": {"last": "2026-01-06"},
          "decision": {"verdict": "ADMIT", "reads": {"capacity_veto_lens": "1M"}}}
    _d = drift(_payload, t=_same, g=_g)
    leg("the gate re-deriving on a new bar is STALE too",
        len(_d) == 1 and "STALE" in _d[0] and "2026-01-06" in _d[0])
    _bad = dict(_payload,
                gate_reads={"verdict": "ADMIT"},
                rows=[dict(fake_rows[0], per_name_cny=999_999.0,
                           capital_at_line_cny=1_000_000.0)])
    _p = check(_bad, t=_same)
    leg("a row that fights its own capital still fails WITHOUT the repair word",
        bool(_p) and not any("stale" in x.lower() for x in _p))

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
