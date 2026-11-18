"""One order, five names, three bars -- and three different capacity numbers.

The capacity veto is a *reading on a bar*: "one day's order <= 1% of that name's ADV". Two
faces already print it and they print it on different days. The fit face (`etf_book_width_fit`)
reads the panel's last bar (2026-11-17 -> the live five names at 1.0087% ADV, capacity
991,421 CNY). The ticket's own capacity block prices the ticket's ranking on its decision bar
(2026-11-11 -> 0.7932%, capacity 1,260,724 CNY). Both are the same rule, applied correctly to
two different days, and a reader with the two numbers in front of them has no way to tell which
one governs -- so a 269,303 CNY difference silently becomes a matter of taste.

This face puts the ladder in one place: the same five names, the same 20-bar median ADV, the
same 1% line, priced bar by bar. It then says the only thing that can be said about the
difference -- which bar governs is decided by when the order is executed, not by which reading
is friendlier.

What it does NOT do: it does not re-rank per bar. The names are held constant (today's picks),
so earlier rows answer "what would these five names have cost on that day", never "what the
book actually held then". That distinction is printed, not implied.
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

OUT = os.path.join(ROOT, "results", "etf_book_width_bar_ladder.json")
GATE_FACE = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")
FIT_FACE = os.path.join(ROOT, "results", "etf_book_width_fit.json")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")

IMPACT_MAX = 0.01
ADV_BARS = 20
DEFAULT_BARS = 3        # how many recent bars the ladder walks back


def load_json(path):
    if not os.path.exists(path):
        return None
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def gate_reads(doc):
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
        "live_picks_asof": ((doc or {}).get("data") or {}).get("live_picks_asof"),
        "evidence_cutoff": (doc or {}).get("evidence_cutoff"),
    }


def latest_ticket():
    """The most recent ticket payload (its own capacity block is the second name set)."""
    if not os.path.isdir(TICKET_DIR):
        return None, None
    names = sorted(n for n in os.listdir(TICKET_DIR)
                   if n.startswith("TICKET-") and n.endswith(".json") and "-card" not in n)
    if not names:
        return None, None
    path = os.path.join(TICKET_DIR, names[-1])
    return path, load_json(path)


def decision_bar_set(ticket_doc):
    """The five names the ticket priced on ITS decision bar -- a different five from today's."""
    wc = (ticket_doc or {}).get("width_capacity") or {}
    rows = wc.get("widths") or []
    if not rows:
        return None, None
    live = wc.get("ticket_n_hold") or rows[0].get("n")
    row = next((r for r in rows if r.get("n") == live), rows[0])
    return list(row.get("picks") or []), wc.get("decision_bar")


def _published_impact(ticket_doc, picks):
    """What the ticket itself published for exactly this name set (None if it is not there)."""
    wc = (ticket_doc or {}).get("width_capacity") or {}
    for r in (wc.get("widths") or []):
        if list(r.get("picks") or []) == list(picks):
            return r.get("impact_pct_of_adv")
    return None


def decompose(gap, names_effect, bar_effect):
    """Names vs day: the two levers, priced separately, plus what neither explains."""
    return {"impact_gap_pp": round(gap, 4),
            "names_effect_pp": round(names_effect, 4),
            "bar_effect_pp": round(bar_effect, 4),
            "unexplained_pp": round(gap - names_effect - bar_effect, 6)}



def panel_and_score():
    """The gate's own panel, repair, class map and score -- its code path, not a copy."""
    import etf_composite_pf as E
    import etf_equity_alpha as A

    close, openp, amt, feats = E.build_panel()
    close, openp, _n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns
            if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    return sc, amt[cols]


def adv_at(amt, sym, bar, bars=ADV_BARS):
    """Median of the slot's last `bars` values AT `bar` -- the panel is sliced, never read
    from the end, so asking about an old bar cannot borrow a later day's turnover."""
    if sym not in amt.columns or bar not in amt.index:
        return None
    s = amt.loc[:bar, sym].tail(bars).dropna()
    if len(s) < bars:
        return None
    med = float(s.median())
    if not (med == med) or med <= 0:
        return None
    return med


def price_bar(sc, amt, bar, picks, capital, line=IMPACT_MAX):
    advs = {sym: adv_at(amt, sym, bar) for sym in picks}
    measured = [(s, a) for s, a in advs.items() if a is not None]
    row = {"bar": str(bar)[:10], "n": len(picks), "picks": list(picks),
           "n_measurable": len(measured), "unmeasurable": [s for s, a in advs.items() if a is None]}
    if not measured or capital is None:
        row.update({"adv_weakest_cny": None, "adv_weakest_sym": None, "per_name_cny": None,
                    "impact_pct_of_adv": None, "fits": None, "capital_at_line_cny": None})
        return row
    weakest_sym, weakest_adv = min(measured, key=lambda kv: kv[1])
    per_name = float(capital) / float(len(picks))
    share = per_name / weakest_adv
    row.update({
        "adv_weakest_cny": round(weakest_adv, 0),
        "adv_weakest_sym": weakest_sym,
        "per_name_cny": round(per_name, 0),
        "impact_pct_of_adv": round(share * 100.0, 4),
        "fits": bool(share <= line),
        "capital_at_line_cny": round(line * weakest_adv * float(len(picks)), 0),
    })
    return row


def verdict_name(rows):
    """Whether the bar moves the answer, and never an average of the rows."""
    seen = [r for r in rows if r.get("fits") is not None]
    if not seen:
        return "UNMEASURABLE", None
    if len({r["fits"] for r in seen}) == 1:
        return ("EVERY_BAR_AGREES" if seen[0]["fits"] else "EVERY_BAR_REFUSES"), seen[-1]["bar"]
    return "BAR_MOVES_THE_VERDICT", seen[-1]["bar"]


def sentence(s, rows, picks, capital):
    if s["verdict"] == "UNMEASURABLE":
        return "这根梯子读不到：评分行或成交额面缺读数，本面不给任何「装得下」的结论。"
    cells = "；".join("%s：%.4f%%（容量 %s 元）" % (
        r["bar"], r["impact_pct_of_adv"],
        format(int(r["capital_at_line_cny"]), ",") if r["capital_at_line_cny"] is not None else "-")
        for r in rows if r.get("impact_pct_of_adv") is not None)
    head = ("同一批 %d 只（%s）、同一笔 %s 元、同一条 %.2f%% ADV 线，按每个 bar 各自的 20 日"
            "成交额分开算：%s。"
            % (len(picks), "/".join(picks), format(int(capital), ",") if capital else "-",
               (s.get("line_pct") or IMPACT_MAX * 100.0), cells))
    if s["verdict"] == "BAR_MOVES_THE_VERDICT":
        tail = ("同一笔单子在窗口里过线和不过线各出现过——**哪一根 bar 说了算，取决于单子在"
                "哪一天成交，不取决于哪个读数好看**。将要成交的那一根才是判据，其余几根是记录。")
    elif s["verdict"] == "EVERY_BAR_AGREES":
        tail = "窗口里每一根 bar 都说得下——判词不依赖选哪一天。"
    else:
        tail = "窗口里每一根 bar 都说不下——这笔单子不是某一天运气不好。"
    return head + tail


def build(bars=None, capital=None):
    g = gate_reads(load_json(GATE_FACE))
    picks = g["live_picks"]
    cap = capital if capital is not None else (g["capital_cny"] or 1_000_000.0)
    sc, amt = panel_and_score()
    last = sc.index[-1]
    if not bars:
        idx = list(sc.index)
        bars = idx[-DEFAULT_BARS:] if len(idx) >= DEFAULT_BARS else idx
    rows = [price_bar(sc, amt, b, picks, cap) for b in bars]
    # second name set: the five the ticket priced on its own decision bar. The two published
    # readings differ by 269,303 CNY today and nobody said whether that is names or days.
    tpath, tdoc = latest_ticket()
    dec_picks, dec_bar = decision_bar_set(tdoc)
    recon = None
    if dec_picks:
        dec_rows = [price_bar(sc, amt, b, dec_picks, cap) for b in bars]
        dec_last = price_bar(sc, amt, last, dec_picks, cap)
        last_bar = str(last)[:10]
        by_bar_today = {r["bar"]: r for r in rows}
        by_bar_dec = {r["bar"]: r for r in dec_rows}
        a = by_bar_today.get(last_bar) or {}
        bbar = dec_bar if dec_bar in by_bar_dec else (sorted(by_bar_dec)[0] if by_bar_dec else None)
        b = by_bar_dec.get(bbar) or {}
        mid_today = by_bar_today.get(bbar) or {}
        if a.get("impact_pct_of_adv") is not None and b.get("impact_pct_of_adv") is not None \
                and mid_today.get("impact_pct_of_adv") is not None:
            recon = {
                "kind": "two_published_readings_decomposed",
                "ticket": os.path.relpath(tpath, ROOT).replace("\\", "/") if tpath else None,
                "today_set": {"picks": picks, "bar": last_bar,
                              "impact_pct_of_adv": a["impact_pct_of_adv"],
                              "capital_at_line_cny": a["capital_at_line_cny"]},
                "decision_bar_set": {"picks": dec_picks, "bar": bbar,
                                     "impact_pct_of_adv": b["impact_pct_of_adv"],
                                     "capital_at_line_cny": b["capital_at_line_cny"]},
                "today_set_on_the_decision_bar": {
                    "bar": bbar, "impact_pct_of_adv": mid_today["impact_pct_of_adv"],
                    "capital_at_line_cny": mid_today["capital_at_line_cny"]},
                "matrix": {
                    "cols": [last_bar, bbar],
                    "today_five": {last_bar: {"impact_pct_of_adv": a["impact_pct_of_adv"],
                                              "capital_at_line_cny": a["capital_at_line_cny"]},
                                   bbar: {"impact_pct_of_adv": mid_today["impact_pct_of_adv"],
                                          "capital_at_line_cny": mid_today["capital_at_line_cny"]}},
                    "ticket_five": {last_bar: {"impact_pct_of_adv": dec_last["impact_pct_of_adv"],
                                               "capital_at_line_cny": dec_last["capital_at_line_cny"]},
                                    bbar: {"impact_pct_of_adv": b["impact_pct_of_adv"],
                                           "capital_at_line_cny": b["capital_at_line_cny"]}},
                },
                # the gap the reader actually sees: today's five on the panel bar vs the
                # ticket's five as published. Both of those read the SAME turnover window.
                "published_gap": {
                    "today_cny": a["capital_at_line_cny"],
                    "ticket_cny": dec_last["capital_at_line_cny"],
                    "diff_cny": round(float(dec_last["capital_at_line_cny"])
                                      - float(a["capital_at_line_cny"]), 0),
                    "names_effect_pp": round(a["impact_pct_of_adv"]
                                             - dec_last["impact_pct_of_adv"], 4),
                    "bar_effect_pp": 0.0,
                    "both_reads": last_bar,
                },
                "decomposition": decompose(
                    a["impact_pct_of_adv"] - b["impact_pct_of_adv"],
                    mid_today["impact_pct_of_adv"] - b["impact_pct_of_adv"],
                    a["impact_pct_of_adv"] - mid_today["impact_pct_of_adv"]),
            }
            pub = _published_impact(tdoc, dec_picks)
            if pub is not None:
                matched = None
                if abs(float(dec_last["impact_pct_of_adv"]) - float(pub)) <= 1e-3:
                    matched = "panel_last_bar"
                if abs(float(b["impact_pct_of_adv"]) - float(pub)) <= 1e-3:
                    matched = "named_bar"
                recon["decision_bar_set_on_panel_last_bar"] = {
                    "bar": str(last)[:10],
                    "impact_pct_of_adv": dec_last["impact_pct_of_adv"],
                    "capital_at_line_cny": dec_last["capital_at_line_cny"]}
                recon["label_check"] = {
                    "published_impact_pct_of_adv": pub,
                    "published_label_bar": bbar,
                    "reproduced_on_panel_last_bar": dec_last["impact_pct_of_adv"],
                    "reproduced_on_named_bar": b["impact_pct_of_adv"],
                    "matched": matched,
                    "cells_differ_by_pp": round(
                        abs(float(b["impact_pct_of_adv"]) - float(dec_last["impact_pct_of_adv"])), 4),
                    "where": "scripts/etf_book_order.py:4050 width_capacity(score.loc[dec_bar], "
                             "amt[cols], _n, nav) -- the ranking row is sliced at the decision bar, "
                             "the turnover panel is not",
                }
    s = {"capital_cny": cap,
         "line_pct": g["line_pct"] if g["line_pct"] is not None else IMPACT_MAX * 100.0}
    name, governing = verdict_name(rows)
    s.update({"verdict": name, "governing_bar": governing,
              "panel_last_bar": str(last)[:10],
              "rows": rows})
    payload = {
        "kind": "etf_book_width_bar_ladder",
        "script": "scripts/etf_book_width_bar_ladder.py",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": str(last)[:10],
        "gate_face": "results/etf_book_year_gate/YEAR-GATE.json",
        "gate_reads": {k: g[k] for k in ("verdict", "lens", "capital_cny", "per_name_cny",
                                        "impact_pct_of_adv", "line_pct", "live_picks_asof")},
        "picks": picks,
        "picks_basis": "today's live picks, held constant on every bar",
        "bars": [str(b)[:10] for b in bars],
        "summary": s,
        "sentence": sentence(s, rows, picks, cap),
        "caveats": [
            "The names are held constant across bars: an earlier row answers "
            "\"what would these five cost that day\", not \"what the book held then\".",
            "The rows are never averaged. A verdict is read off one bar; which bar governs is "
            "decided by the execution day, not by which reading fits.",
            "ADV is the gate's own rule (median of the slot's last 20 close x volume values), "
            "with the panel sliced at the bar being asked about.",
            "Capacity at the line is per-name capital x width: it is a capacity number, never "
            "a return number.",
        ],
    }
    if recon:
        d = recon["decomposition"]
        pg = recon["published_gap"]
        payload["reconcile"] = recon
        payload["sentence"] += (
            " 两块已发布的面其实读的是同一根成交额窗（%s）——%s 元的差**全部来自换了名字**"
            "（%.4fpp），没有一分来自换了日子。"
            % (pg["both_reads"], format(int(pg["diff_cny"]), ","), pg["names_effect_pp"]))
        lc = recon.get("label_check")
        if lc and lc.get("matched") == "panel_last_bar":
            payload["sentence"] += (
                " 牌子才是错的：票面把那块标成 %s，可它的成交额读到的是 %s。若真按牌子那天算，"
                "同一批名字只有 %s 元——**牌子把容量说高 %s 元（%.4fpp）**。"
                "（排名日 %s 与成交额日 %s 是两个日子，容量读数跟着后者走。）"
                % (lc["published_label_bar"], recon["decision_bar_set_on_panel_last_bar"]["bar"],
                   format(int(recon["decision_bar_set"]["capital_at_line_cny"]), ","),
                   format(int(round(float(recon["decision_bar_set_on_panel_last_bar"]["capital_at_line_cny"])
                                    - float(recon["decision_bar_set"]["capital_at_line_cny"]))), ","),
                   lc["cells_differ_by_pp"], lc["published_label_bar"],
                   recon["decision_bar_set_on_panel_last_bar"]["bar"]))
        elif lc:
            payload["sentence"] += (" 票面那块在它自称的 %s 上复现得到（%.4f%%）——牌子与窗口一致。"
                                    % (lc["published_label_bar"], lc["published_impact_pct_of_adv"]))
    return payload, sc, amt


def check(payload):
    problems = []
    rows = payload.get("summary", {}).get("rows") or []
    g = payload.get("gate_reads") or {}
    line = (payload.get("summary", {}).get("line_pct") or 1.0) / 100.0
    for r in rows:
        if r.get("impact_pct_of_adv") is None:
            continue
        if r.get("adv_weakest_cny") is None or r.get("capital_at_line_cny") is None:
            problems.append("%s: incomplete row with a printed impact" % r.get("bar"))
            continue
        adv = float(r["adv_weakest_cny"])
        n = int(r["n"])
        want_share = (float(payload["summary"]["capital_cny"]) / n) / adv * 100.0
        if abs(want_share - r["impact_pct_of_adv"]) > 1e-3:
            problems.append("%s: impact %.4f != share %.4f" %
                            (r["bar"], r["impact_pct_of_adv"], want_share))
        want_cap = line * adv * n
        if abs(want_cap - float(r["capital_at_line_cny"])) > 1.0:
            problems.append("%s: capacity %.0f != %.0f" % (r["bar"], r["capital_at_line_cny"], want_cap))
        if (r["impact_pct_of_adv"] / 100.0 <= line) != bool(r["fits"]):
            problems.append("%s: fits flag disagrees with its own impact" % r["bar"])
    # the panel bar must reproduce the gate's own published reading on the same picks
    last_bar = payload.get("summary", {}).get("panel_last_bar")
    gate_row = [r for r in rows if r["bar"] == last_bar]
    if gate_row and g.get("impact_pct_of_adv") is not None:
        if abs(float(gate_row[0]["impact_pct_of_adv"]) - float(g["impact_pct_of_adv"])) > 1e-3:
            problems.append("panel bar %s reads %.4f but the gate published %.4f" %
                            (last_bar, gate_row[0]["impact_pct_of_adv"], g["impact_pct_of_adv"]))
    if len({r["bar"] for r in rows}) != len(rows):
        problems.append("a bar appears twice in the ladder")
    rec = payload.get("reconcile") or {}
    if rec:
        d = rec.get("decomposition") or {}
        gap = (rec["today_set"]["impact_pct_of_adv"]
               - rec["decision_bar_set"]["impact_pct_of_adv"])
        if abs((d.get("names_effect_pp") or 0) + (d.get("bar_effect_pp") or 0)
               + (d.get("unexplained_pp") or 0) - gap) > 1e-3:
            problems.append("decomposition does not add up to the gap")
        lc = rec.get("label_check") or {}
        if lc:
            # the published number must land on ONE of the two bars -- on neither means this
            # face and the ticket disagree about the model, not about a label.
            if lc.get("matched") is None:
                problems.append("ticket's published %.4f reproduces on neither bar" %
                                float(lc.get("published_impact_pct_of_adv") or 0))
            if (lc.get("matched") == "panel_last_bar"
                    and lc.get("published_label_bar") == lc.get("matched")):
                problems.append("label_check says panel_last_bar but the label claims that bar")
    return problems


def run(bars=None, capital=None):
    payload, _sc, _amt = build(bars=bars, capital=capital)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    print(payload["summary"]["verdict"], "governing=%s" % payload["summary"]["governing_bar"])
    print(payload["sentence"])
    return 0


def main_check():
    doc = load_json(OUT)
    if not doc:
        print("no face at %s -- run it first" % OUT)
        return 2
    problems = check(doc)
    if problems:
        print("CHECK_FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print("CHECK_OK verdict=%s governing=%s bars=%d" % (
        doc["summary"]["verdict"], doc["summary"]["governing_bar"],
        len(doc.get("bars") or [])))
    return 0


def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    # L1 causal slicing: asking an old bar must not read a later day's turnover
    try:
        import pandas as pd
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 100.0]},
                          index=pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-05",
                                                "2026-01-06", "2026-01-07"]))
        old = adv_at(df, "a", pd.Timestamp("2026-01-06"), bars=3)
        new = adv_at(df, "a", pd.Timestamp("2026-01-07"), bars=3)
        leg("L1 old bar median 3.0 vs last-bar 4.0 (later day not borrowed)",
            old == 3.0 and new == 4.0)
        leg("L2 bar absent from the panel -> None, not zero",
            adv_at(df, "a", pd.Timestamp("2026-01-09"), bars=3) is None)
        leg("L3 fewer than 20 bars at that bar -> None (no short window silently used)",
            adv_at(df, "a", pd.Timestamp("2026-01-06"), bars=20) is None)
    except Exception as exc:                      # noqa: BLE001
        leg("panel arithmetic unavailable (%s)" % str(exc)[:60], False)

    # L4/L5 verdict functions: a bar that flips the answer is named, and never averaged
    flip = [{"bar": "2026-11-11", "fits": True}, {"bar": "2026-11-17", "fits": False}]
    same = [{"bar": "2026-11-16", "fits": True}, {"bar": "2026-11-17", "fits": True}]
    leg("L4 one refusal among passes -> BAR_MOVES_THE_VERDICT",
        verdict_name(flip)[0] == "BAR_MOVES_THE_VERDICT")
    leg("L5 every bar agreeing keeps its own name",
        verdict_name(same)[0] == "EVERY_BAR_AGREES" and verdict_name([])[0] == "UNMEASURABLE")

    d = decompose(0.2155, 0.2792, -0.0637)
    leg("L5b names + day + unexplained add back to the gap",
        abs(d["names_effect_pp"] + d["bar_effect_pp"] + d["unexplained_pp"] - d["impact_gap_pp"]) < 1e-6)
    leg("L5c the two levers are reported separately, never folded into one number",
        d["names_effect_pp"] != d["impact_gap_pp"] and d["bar_effect_pp"] != 0.0)

    # L6 the face on disk reproduces the gate's own published reading
    doc = load_json(OUT)
    if doc:
        leg("L6 published face reproduces the gate reading on the panel bar",
            not [p for p in check(doc) if "gate published" in p])
        leg("L7 face states the names are held constant",
            any("held constant" in c for c in (doc.get("caveats") or [])))
        leg("L8 no row is an average (each row carries its own bar)",
            len({r["bar"] for r in doc["summary"]["rows"]}) == len(doc["summary"]["rows"]))
    else:
        leg("L6-L8 no face on disk yet -> structural legs only", True)

    passed = sum(1 for _n, ok in legs if ok)
    for name, ok in legs:
        if not ok:
            print("FAIL", name)
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="same order, five names, bar-by-bar capacity")
    ap.add_argument("--bars", help="comma-separated YYYY-MM-DD (default: the last 3 bars)")
    ap.add_argument("--capital", type=float, default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check:
        return main_check()
    bars = [b.strip() for b in a.bars.split(",") if b.strip()] if a.bars else None
    if bars:
        import pandas as pd
        bars = [pd.Timestamp(b) for b in bars]
    return run(bars=bars, capital=a.capital)


if __name__ == "__main__":
    sys.exit(main())
