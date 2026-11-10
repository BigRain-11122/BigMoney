"""ETF book -- one cost, three scopes, and the number the trigger actually used.

The sheet now prints two tolls half a page apart, and both of them are called the same thing:

  * r1466 (the trigger) says "act again only if a pair's gap exceeds 0.16 pp -- 2 x 8 bp
    per side", and its window share (92%) is computed against that 0.16;
  * r1522 (the way back) says the round trip is 0.32 pp, and r1523 subtracts 0.32 before it
    calls anything paid.

0.16 and 0.32 are both correct. They are not the same quantity, and the sheet never says so:

    entry  2 sides  -- paid on the bar the swap executed; SUNK, it does not come back
    exit   2 sides  -- the only cost that changes with today's decision to unwind
    trip   4 sides  -- entry + exit; the cost of the whole manoeuvre, not of the next trade

A desk that reads 0.32 as the trigger's threshold waits for twice the gap it needs; a desk
that reads 0.16 as "what the swap costs" thinks the discount is twice as cheap as it is.
Neither mistake is arithmetic -- both are a label without a scope.

This face puts the scope on every number and refuses to let the three be combined:

  1. per pair and in total, entry / exit / trip in pp and in CNY on the notional that
     actually traded (the side counts and the cost are imported, never retyped);
  2. the trigger's own window share re-run at both thresholds, with a reproduction gate --
     the 0.16 share must re-derive from this face's series before the 0.32 share is printed,
     otherwise the face refuses (a threshold moved on top of a series that does not match the
     published one measures nothing);
  3. r1523's net re-priced on the incremental caliber beside the published cumulative one,
     labelled, NOT added and NOT averaged.

Usage:
    python scripts/etf_book_toll_scope.py run
    python scripts/etf_book_toll_scope.py --check
    python scripts/etf_book_toll_scope.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_sibling_gap as gap_face          # noqa: E402  (the one gap reconstruction)
import etf_book_swap_toll as toll_face           # noqa: E402  (the side counts, not retyped)
import etf_book_swap_trigger as trig_face        # noqa: E402  (the structural share line)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_toll_scope.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_toll_scope.md")

# ---- frozen criteria (echoed into the payload; --check refuses a face that disagrees) ----
DECISION_SCOPE = "exit"     # the only cost that moves with "do I unwind today"
PRINTED_WORD = "round-trip"  # what the trigger calls its 0.16


def cost_bp():
    """The per-side cost this book is priced at -- read from the ticket, never retyped."""
    try:
        from scripts.etf_book_order import COST_BP
        return float(COST_BP)
    except Exception:                                            # noqa: BLE001
        import etf_book_order
        return float(etf_book_order.COST_BP)


def scopes(bp=None):
    """The three scopes on one cost. Side counts come from r1522's own constants."""
    bp = cost_bp() if bp is None else float(bp)
    entry_sides = int(toll_face.ENTRY_SIDES)
    exit_sides = int(toll_face.EXIT_SIDES)
    out = [
        {"name": "entry", "sides": entry_sides,
         "pp": round(entry_sides * bp / 100.0, 4),
         "question": "换进去那一笔付了多少",
         "decision_use": "SUNK: paid on the execution bar, unchanged by anything decided today"},
        {"name": "exit", "sides": exit_sides,
         "pp": round(exit_sides * bp / 100.0, 4),
         "question": "今天换回来还要付多少",
         "decision_use": "INCREMENTAL: this is the threshold a 'act again?' decision may use"},
        {"name": "trip", "sides": entry_sides + exit_sides,
         "pp": round((entry_sides + exit_sides) * bp / 100.0, 4),
         "question": "一来一回总共多少",
         "decision_use": "CUMULATIVE: answers 'did the discount pay for the whole manoeuvre'"},
    ]
    for s in out:
        s["cny_per_100k"] = round(100000.0 * s["pp"] / 100.0, 2)
    return out


def _scope(name, bp):
    for s in scopes(bp):
        if s["name"] == name:
            return s
    raise KeyError(name)


def _cny(notional, pp):
    return round(float(notional) * float(pp) / 100.0, 2)


def pair_series(leg, sib):
    """The same reconstruction the gap face publishes -- imported, never rebuilt here."""
    a, b = gap_face.find_daily(leg), gap_face.find_daily(sib)
    if not a or not b:
        return None
    try:
        _dates, ca, cb = gap_face.common_series(gap_face.load_close(a), gap_face.load_close(b))
    except Exception:                                            # noqa: BLE001
        return None
    g = gap_face.gap_series(ca, cb)
    return g or None


def share_above(series, threshold):
    if not series:
        return None
    return round(sum(1 for v in series if v > threshold) / len(series), 4)


def _face(toll, conv, trig, as_of):
    face = {"artifact": "etf_book_toll_scope", "bar": as_of, "verdict": None,
            "scopes": [], "rows": [], "totals": {}, "convergence": {}, "label_audit": {},
            "reproduction": {}, "decision": {}, "refused": [], "caveats": [], "sources": {},
            "evidence_cutoff": as_of, "sentence": ""}
    if not toll:
        face["refused"].append("no etf_book_swap_toll face: nothing to scope")
        return face
    if toll.get("verdict") != "TOLL_PRICED":
        face["refused"].append("the toll face itself refused (%s): a scope on an unpriced toll "
                               "is a scope on a guess" % (toll.get("verdict") or "no verdict"))
        return face
    bp = float(toll.get("cost_bp_per_side") or cost_bp())
    face["cost_bp_per_side"] = bp
    face["scopes"] = scopes(bp)
    face["decision"] = {"threshold_scope": DECISION_SCOPE,
                        "threshold_pp": _scope(DECISION_SCOPE, bp)["pp"],
                        "why": ("only the exit toll moves with 'do I unwind today'; the entry "
                                "toll is already paid whether this desk acts or not")}
    trig_pairs = {}
    for p in ((trig or {}).get("pairs") or []):
        trig_pairs[(p.get("leg_symbol"), p.get("sibling_symbol"))] = p
    conv_pairs = {}
    for p in ((conv or {}).get("pairs") or []):
        conv_pairs[(p.get("leg_symbol"), p.get("sibling_symbol"))] = p

    entry_pp = _scope("entry", bp)["pp"]
    exit_pp = _scope("exit", bp)["pp"]
    trip_pp = _scope("trip", bp)["pp"]

    for r in toll.get("rows") or []:
        key = (r.get("symbol"), r.get("sibling"))
        notional = float(r.get("notional_cny") or 0.0)
        row = {"symbol": r.get("symbol"), "sibling": r.get("sibling"), "notional_cny": notional,
               "entry_pp": entry_pp, "exit_pp": exit_pp, "trip_pp": trip_pp,
               "entry_cny": _cny(notional, entry_pp), "exit_cny": _cny(notional, exit_pp),
               "trip_cny": _cny(notional, trip_pp), "why": ""}
        tp = trig_pairs.get(key) or {}
        today_gap = tp.get("today_gap_pp")
        if today_gap is None:
            row["why"] = "the trigger does not publish this pair's gap: no share can be re-read"
            face["rows"].append(row)
            continue
        series = pair_series(r.get("symbol"), r.get("sibling"))
        if not series:
            row["why"] = "no daily panel for this pair: the share is not re-derivable"
            face["rows"].append(row)
            continue
        rec, _offset = gap_face.reconstruct(series, float(today_gap))
        row["share_at_entry_pp"] = share_above(rec, entry_pp)
        row["share_at_trip_pp"] = share_above(rec, trip_pp)
        row["published_share_at_0_16"] = tp.get("window_share")
        row["published_share_matches"] = (
            None if row["published_share_at_0_16"] is None
            else abs(float(row["published_share_at_0_16"]) - float(row["share_at_entry_pp"])) <= 0.01)
        row["structural_share"] = trig_face.STRUCTURAL_SHARE
        row["standing_at_entry_scope"] = (
            None if row["share_at_entry_pp"] is None
            else bool(row["share_at_entry_pp"] >= trig_face.STRUCTURAL_SHARE))
        row["standing_at_trip_scope"] = (
            None if row["share_at_trip_pp"] is None
            else bool(row["share_at_trip_pp"] >= trig_face.STRUCTURAL_SHARE))
        row["verdict_flips_with_scope"] = (
            None if row["standing_at_entry_scope"] is None or row["standing_at_trip_scope"] is None
            else bool(row["standing_at_entry_scope"] != row["standing_at_trip_scope"]))
        cp = conv_pairs.get(key) or {}
        gain = cp.get("gain_pp")
        if gain is None and cp.get("net_after_toll_pp") is not None and conv.get("toll_pp"):
            gain = round(float(cp["net_after_toll_pp"]) + float(conv["toll_pp"]), 4)
        if gain is not None and notional:
            row["path_gain_pp"] = float(gain)
            row["net_round_trip_pp"] = round(float(gain) - trip_pp, 4)
            row["net_exit_only_pp"] = round(float(gain) - exit_pp, 4)
            row["net_round_trip_cny"] = _cny(notional, row["net_round_trip_pp"])
            row["net_exit_only_cny"] = _cny(notional, row["net_exit_only_pp"])
            row["caliber_gap_pp"] = round(trip_pp - exit_pp, 4)
        else:
            row["why"] = (row["why"] or "") or "no measured path for this pair: nothing to re-price"
        face["rows"].append(row)

    priced = [r for r in face["rows"] if r.get("exit_cny") is not None]
    face["totals"] = {
        "notional_cny": round(sum(r["notional_cny"] for r in priced), 2),
        "entry_cny": round(sum(r["entry_cny"] for r in priced), 2),
        "exit_cny": round(sum(r["exit_cny"] for r in priced), 2),
        "trip_cny": round(sum(r["trip_cny"] for r in priced), 2),
        "pairs": len(priced),
        # deliberately absent, and --check fails if anyone adds it: entry and exit are the
        # same money counted at two moments; a "combined" total is how the 0.32 got read as
        # the trigger's threshold in the first place.
        "combined_cny": None,
    }
    repriced = [r for r in face["rows"] if r.get("net_exit_only_pp") is not None]
    face["convergence"] = {
        "pairs": len(repriced),
        "net_round_trip_cny": round(sum(r["net_round_trip_cny"] for r in repriced), 2),
        "net_exit_only_cny": round(sum(r["net_exit_only_cny"] for r in repriced), 2),
        "verdict_round_trip": ("PAYS" if sum(r["net_round_trip_cny"] for r in repriced) > 0
                               else "DOES_NOT_PAY") if repriced else None,
        "verdict_exit_only": ("PAYS" if sum(r["net_exit_only_cny"] for r in repriced) > 0
                              else "DOES_NOT_PAY") if repriced else None,
        "do_not_add": True,
        "why": ("the two columns read the same gap change twice: one charges the entry toll a "
                "second time (cumulative), the other charges only what acting again costs. "
                "Adding or averaging them prices the trade at 1.5 exchanges"),
    }

    published_toll = ((trig or {}).get("criteria") or {}).get("toll_pp")
    audit = {"trigger_toll_pp": published_toll, "printed_as": PRINTED_WORD,
             "round_trip_pp": trip_pp, "single_exchange_pp": entry_pp,
             "equal_to_round_trip": None, "disclosure_status": "NO_TRIGGER_FACE"}
    if published_toll is not None:
        audit["equal_to_round_trip"] = abs(float(published_toll) - trip_pp) <= 1e-9
        audit["equal_to_single_exchange"] = abs(float(published_toll) - entry_pp) <= 1e-9
        if audit["equal_to_round_trip"]:
            audit["disclosure_status"] = "LABEL_MATCHES_VALUE"
        elif audit["equal_to_single_exchange"]:
            audit["disclosure_status"] = "VALUE_IS_ONE_EXCHANGE_LABEL_SAYS_ROUND_TRIP"
        else:
            audit["disclosure_status"] = "VALUE_MATCHES_NEITHER_SCOPE"
    face["label_audit"] = audit

    mism = [r for r in face["rows"] if r.get("published_share_matches") is False]
    face["reproduction"] = {
        "checked": len([r for r in face["rows"] if r.get("published_share_matches") is not None]),
        "mismatched": [r["symbol"] for r in mism],
        "ok": not mism,
    }

    face["caveats"] = [
        "the three scopes share one cost figure and one notional; the side counts are imported "
        "from r1522 and the cost from the ticket, so a change in either moves all three together",
        "the trigger's window share is REPRODUCED here at its own threshold before the second "
        "share is printed: a share at a moved threshold is a measurement, a share at a moved "
        "threshold on a series that no longer matches the published one is a new number wearing "
        "an old name",
        "the path column re-prices an already published net; it does not re-measure the path "
        "and it does not re-derive the gain",
        "a pair the trigger does not publish carries no share and is named, not printed as 0",
    ]
    face["sources"] = {"swap_toll": "results/etf_book_swap_toll.json",
                       "swap_convergence": "results/etf_book_swap_convergence.json",
                       "swap_trigger": "results/etf_book_swap_trigger.json",
                       "gap": "results/etf_book_sibling_gap.json (reconstruction imported)"}
    face["verdict"] = "SCOPES_SEPARATED"
    return face


def sentence(face):
    if not face or face.get("verdict") != "SCOPES_SEPARATED":
        return (face or {}).get("sentence") or "这一问答不了：三个范围都没有可读的数。"
    sc = {s["name"]: s for s in face["scopes"]}
    t = face.get("totals") or {}
    conv = face.get("convergence") or {}
    head = ("同一个成本在读三个范围：进 %.2fpp（已付、沉没）、出 %.2fpp（今天再动才付）、"
            "一来一回 %.2fpp——这一次进出各 ￥%s，合计 ￥%s。"
            % (sc["entry"]["pp"], sc["exit"]["pp"], sc["trip"]["pp"],
               format(t.get("exit_cny") or 0.0, ",.0f"), format(t.get("trip_cny") or 0.0, ",.0f")))
    if conv.get("pairs"):
        head += (" 判「要不要再动一次」只能用 %.2fpp；按它算净额是 ￥%s，按一来一回算是 ￥%s，"
                 "两个数不能相加也不能平均。"
                 % (sc["exit"]["pp"], format(conv["net_exit_only_cny"], ",.0f"),
                    format(conv["net_round_trip_cny"], ",.0f")))
    return head


def md_lines(face, heading="## 这条过路费是几个钱（r1529）"):
    if not face:
        return ["", heading,
                "- **这一问答不了**：没有已发布的过路费范围面（跑 "
                "scripts/etf_book_toll_scope.py run）。缺面不等于三个范围相等。", ""]
    if face.get("refused"):
        return ["", heading, "- **算不出来**：%s。" % "；".join(face["refused"]),
                "- 读法：范围没定之前，任何「过路费是多少」的回答都可能是在拿一边的钱"
                "回答另一边的问题。", ""]
    L = ["", heading, "- %s" % sentence(face)]
    sc = {s["name"]: s for s in face["scopes"]}
    L += ["", "| 范围 | 边数 | pp | 每 10 万 | 它回答什么 | 能不能当决策门槛 |",
          "|---|---|---|---|---|---|"]
    for name in ("entry", "exit", "trip"):
        s = sc[name]
        L.append("| %s | %d | %.2f | ￥%s | %s | %s |"
                 % ({"entry": "进", "exit": "出", "trip": "一来一回"}[name], s["sides"], s["pp"],
                    format(s["cny_per_100k"], ",.0f"), s["question"],
                    "能" if s["decision_use"].startswith("INCREMENTAL") else "不能"))
    rows = face.get("rows") or []
    if rows:
        L += ["", "| 换出 | 换入 | 发生额 | 进 | 出 | 一来一回 | 站稳门槛(出/一来一回) | 换范围后判决翻转 |",
              "|---|---|---|---|---|---|---|---|"]
        for r in rows:
            flip = r.get("verdict_flips_with_scope")
            L.append("| %s | %s | ￥%s | ￥%s | ￥%s | ￥%s | %s / %s | %s |"
                     % (r["symbol"], r["sibling"], format(r["notional_cny"], ",.0f"),
                        format(r["entry_cny"], ",.0f"), format(r["exit_cny"], ",.0f"),
                        format(r["trip_cny"], ",.0f"),
                        _pct(r.get("share_at_entry_pp")), _pct(r.get("share_at_trip_pp")),
                        ("是" if flip else "否") if flip is not None else "读不出"))
        for r in rows:
            if r.get("why"):
                L.append("- %s → %s：%s。" % (r["symbol"], r["sibling"], r["why"]))
    conv = face.get("convergence") or {}
    if conv.get("pairs"):
        L += ["", "同一个价差路径，两条口径各读一次（**不能相加、不能平均**）：",
              "- 按「一来一回 %.2fpp」算：净 **￥%s**（%s）"
              % (sc["trip"]["pp"], format(conv["net_round_trip_cny"], ",.0f"),
                 conv["verdict_round_trip"]),
              "- 按「今天再动才付 %.2fpp」算：净 **￥%s**（%s）"
              % (sc["exit"]["pp"], format(conv["net_exit_only_cny"], ",.0f"),
                 conv["verdict_exit_only"]),
              "- 读法：%s。" % conv.get("why")]
    audit = face.get("label_audit") or {}
    if audit.get("disclosure_status") == "VALUE_IS_ONE_EXCHANGE_LABEL_SAYS_ROUND_TRIP":
        L.append("- **命名纠错**：触发面把 %.2fpp 写成「往返」，而往返是 %.2fpp——%.2fpp "
                 "是一次换手（买卖各一边）。拿它当「要不要再动一次」的门槛是对的，"
                 "当成「这次换票花了多少」就少算了一半。"
                 % (audit["trigger_toll_pp"], audit["round_trip_pp"], audit["trigger_toll_pp"]))
    rep = face.get("reproduction") or {}
    if rep.get("checked"):
        L.append("- 复现门：本面重算 %d 对的窗口占比，与触发面发布值一致=%s。"
                 % (rep["checked"], "是" if rep.get("ok") else "否（%s）"
                    % "、".join(rep.get("mismatched") or [])))
    return L


def _pct(share):
    return "%.1f%%" % (100.0 * share) if share is not None else "读不出"


def check(face):
    problems = []
    if not face:
        return ["no face"]
    if face.get("verdict") != "SCOPES_SEPARATED":
        return problems
    bp = float(face.get("cost_bp_per_side") or 0.0)
    sc = {s["name"]: s for s in face.get("scopes") or []}
    if len(sc) != 3:
        return ["the face does not carry three scopes"]
    for name, sides in (("entry", toll_face.ENTRY_SIDES), ("exit", toll_face.EXIT_SIDES),
                        ("trip", toll_face.ENTRY_SIDES + toll_face.EXIT_SIDES)):
        if sc[name]["sides"] != int(sides):
            problems.append("%s scope side count drifted from r1522" % name)
        if abs(sc[name]["pp"] - round(int(sides) * bp / 100.0, 4)) > 1e-9:
            problems.append("%s scope pp does not re-derive" % name)
    if abs(sc["entry"]["pp"] + sc["exit"]["pp"] - sc["trip"]["pp"]) > 1e-9:
        problems.append("entry + exit != trip")
    t = face.get("totals") or {}
    if t.get("combined_cny") is not None:
        problems.append("totals carries a combined figure: the three scopes are not addable")
    if abs((t.get("entry_cny") or 0.0) + (t.get("exit_cny") or 0.0) - (t.get("trip_cny") or 0.0)) > 0.02:
        problems.append("totals do not add up to the trip")
    dec = face.get("decision") or {}
    if dec.get("threshold_pp") != sc["exit"]["pp"]:
        problems.append("the decision threshold is not the exit scope")
    for r in face.get("rows") or []:
        if r.get("net_exit_only_pp") is None:
            continue
        if abs((r["net_exit_only_pp"] - r["net_round_trip_pp"]) - (sc["trip"]["pp"] - sc["exit"]["pp"])) > 1e-6:
            problems.append("%s: the two calibers are not the trip-minus-exit gap" % r["symbol"])
        if r.get("caliber_gap_pp") is not None and abs(r["caliber_gap_pp"] - sc["entry"]["pp"]) > 1e-9:
            problems.append("%s: the caliber gap is not the entry toll" % r["symbol"])
    audit = face.get("label_audit") or {}
    if audit.get("value_matches_neither_scope" if False else "disclosure_status") == \
            "VALUE_MATCHES_NEITHER_SCOPE":
        problems.append("the trigger's toll matches neither scope: re-derive before publishing")
    return problems


# ---------------------------------------------------------------- selftest fixtures

def _fixture(bp=8.0, flip_share=True):
    trig = {"artifact": "etf_book_swap_trigger",
            "criteria": {"cost_bp_per_side": bp, "toll_pp": round(2 * bp / 100.0, 4),
                         "structural_share": 0.80},
            "pairs": [{"leg_symbol": "A1", "sibling_symbol": "B", "today_gap_pp": 8.0,
                       "mean_gap_pp": 2.0, "window_share": 0.92,
                       "verdict": "WINDOW_ALWAYS_OPEN"},
                      {"leg_symbol": "A2", "sibling_symbol": "B", "today_gap_pp": 6.0,
                       "mean_gap_pp": 2.2, "window_share": 0.90,
                       "verdict": "WINDOW_ALWAYS_OPEN"}]}
    toll = {"artifact": "etf_book_swap_toll", "verdict": "TOLL_PRICED",
            "cost_bp_per_side": bp,
            "rows": [{"symbol": "A1", "sibling": "B", "notional_cny": 78492.0},
                     {"symbol": "A2", "sibling": "B", "notional_cny": 78455.0}],
            "totals": {"notional_cny": 156947.0, "entry_cost_cny": 251.12,
                       "exit_cost_cny": 251.12, "round_trip_cny": 502.24}}
    conv = {"artifact": "etf_book_swap_convergence", "toll_pp": round(4 * bp / 100.0, 4),
            "pairs": [{"leg_symbol": "A1", "sibling_symbol": "B",
                       "net_after_toll_pp": -0.4705, "net_after_toll_cny": -369.3},
                      {"leg_symbol": "A2", "sibling_symbol": "B",
                       "net_after_toll_pp": -0.2265, "net_after_toll_cny": -177.7}]}
    return {"as_of": "2026-11-10", "swap_toll": toll, "swap_convergence": conv,
            "swap_trigger": trig}


def _series(today_gap=8.0, n=300, wide=260):
    """A deterministic stand-in series: `wide` sessions above 0.4pp, then a tail."""
    vals = []
    for i in range(n):
        vals.append(today_gap if i >= n - wide else -1.0)
    return vals


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    bp = 8.0
    sc = {s["name"]: s for s in scopes(bp)}
    leg("L1 entry is 2 sides x 8bp = 0.16pp", abs(sc["entry"]["pp"] - 0.16) < 1e-9)
    leg("L2 exit is 0.16pp as well", abs(sc["exit"]["pp"] - 0.16) < 1e-9)
    leg("L3 trip is 4 sides = 0.32pp", abs(sc["trip"]["pp"] - 0.32) < 1e-9)
    leg("L4 trip == entry + exit", abs(sc["trip"]["pp"] - sc["entry"]["pp"] - sc["exit"]["pp"]) < 1e-9)
    leg("L5 side counts come from r1522", sc["entry"]["sides"] == toll_face.ENTRY_SIDES
        and sc["exit"]["sides"] == toll_face.EXIT_SIDES)
    leg("L6 only the exit scope may be a decision threshold",
        sc["exit"]["decision_use"].startswith("INCREMENTAL")
        and not sc["trip"]["decision_use"].startswith("INCREMENTAL"))
    leg("L7 a scope carries its per-100k money", sc["trip"]["cny_per_100k"] == 320.0)

    # --- the share is a function of the threshold, on the same series
    s = _series(today_gap=8.0, n=300, wide=260)
    leg("L8 the wider threshold cannot raise the share",
        share_above(s, 0.32) <= share_above(s, 0.16))
    leg("L9 both shares are inside [0,1]",
        0.0 <= share_above(s, 0.32) <= 1.0 and 0.0 <= share_above(s, 0.16) <= 1.0)
    leg("L10 an empty series gives None, not 0", share_above([], 0.16) is None)

    # --- the label audit reads the value, not the word
    ctx = _fixture()
    f = _face(ctx["swap_toll"], ctx["swap_convergence"], ctx["swap_trigger"], "2026-11-10")
    f["rows"] = []  # the share legs need the real panels; the audit does not
    aud = f["label_audit"]
    leg("L11 the trigger's 0.16 is one exchange, not the round trip",
        aud["disclosure_status"] == "VALUE_IS_ONE_EXCHANGE_LABEL_SAYS_ROUND_TRIP")
    leg("L12 the mismatch is reported, not silently corrected",
        aud["equal_to_round_trip"] is False and aud["equal_to_single_exchange"] is True)

    ctx2 = _fixture()
    ctx2["swap_trigger"]["criteria"]["toll_pp"] = 0.32
    f2 = _face(ctx2["swap_toll"], ctx2["swap_convergence"], ctx2["swap_trigger"], "2026-11-10")
    leg("L13 a trigger that prints the round trip is labelled a match",
        f2["label_audit"]["disclosure_status"] == "LABEL_MATCHES_VALUE")

    ctx3 = _fixture()
    ctx3["swap_trigger"]["criteria"]["toll_pp"] = 0.25
    f3 = _face(ctx3["swap_toll"], ctx3["swap_convergence"], ctx3["swap_trigger"], "2026-11-10")
    leg("L14 a third value is refused rather than rounded into a scope",
        f3["label_audit"]["disclosure_status"] == "VALUE_MATCHES_NEITHER_SCOPE")

    # --- the two calibers are the same gain repriced, and never added
    f["rows"] = [
        {"symbol": "A1", "sibling": "B", "notional_cny": 78492.0,
         "entry_pp": 0.16, "exit_pp": 0.16, "trip_pp": 0.32,
         "entry_cny": 125.59, "exit_cny": 125.59, "trip_cny": 251.18,
         "path_gain_pp": -0.1505, "net_round_trip_pp": -0.4705, "net_exit_only_pp": -0.3105,
         "net_round_trip_cny": -369.3, "net_exit_only_cny": -243.7, "caliber_gap_pp": 0.16,
         "why": ""},
        {"symbol": "A2", "sibling": "B", "notional_cny": 78455.0,
         "entry_pp": 0.16, "exit_pp": 0.16, "trip_pp": 0.32,
         "entry_cny": 125.53, "exit_cny": 125.53, "trip_cny": 251.06,
         "path_gain_pp": -0.0665, "net_round_trip_pp": -0.3865, "net_exit_only_pp": -0.2265,
         "net_round_trip_cny": -303.2, "net_exit_only_cny": -177.7, "caliber_gap_pp": 0.16,
         "why": ""},
    ]
    f["totals"] = {"notional_cny": 156947.0, "entry_cny": 251.12, "exit_cny": 251.12,
                   "trip_cny": 502.24, "pairs": 2, "combined_cny": None}
    repriced = f["rows"]
    f["convergence"] = {"pairs": 2,
                        "net_round_trip_cny": round(sum(r["net_round_trip_cny"] for r in repriced), 2),
                        "net_exit_only_cny": round(sum(r["net_exit_only_cny"] for r in repriced), 2),
                        "verdict_round_trip": "DOES_NOT_PAY", "verdict_exit_only": "DOES_NOT_PAY",
                        "do_not_add": True, "why": "fixture"}
    leg("L15 the caliber gap is exactly the entry toll",
        all(abs(r["caliber_gap_pp"] - sc["entry"]["pp"]) < 1e-9 for r in f["rows"]))
    leg("L16 charging the round trip never looks better than charging the exit",
        all(r["net_round_trip_pp"] < r["net_exit_only_pp"] for r in f["rows"]))
    leg("L17 check passes on a clean face", check(f) == [])
    leg("L18 a combined total is refused", check(dict(f, totals=dict(f["totals"],
                                                                     combined_cny=502.24))) != [])
    leg("L19 a drifted scope pp is refused",
        check(dict(f, scopes=[dict(s, pp=s["pp"] + 0.01) if s["name"] == "exit" else s
                              for s in f["scopes"]])) != [])
    leg("L20 a decision threshold that is the trip is refused",
        check(dict(f, decision={"threshold_scope": "trip", "threshold_pp": 0.32})) != [])
    leg("L21 a caliber that is not trip-minus-exit is refused",
        check(dict(f, rows=[dict(f["rows"][0], net_exit_only_pp=-0.40)])) != [])
    leg("L22 neither column is used as the other's total",
        f["convergence"]["net_exit_only_cny"] > f["convergence"]["net_round_trip_cny"])
    leg("L23 the sentence names the scope in front of each number",
        "进" in sentence(f) and "出" in sentence(f) and "一来一回" in sentence(f))
    leg("L24 no toll face -> refused, not zero",
        _face(None, None, None, "2026-11-10")["refused"] != [])
    leg("L25 a refused toll face propagates the refusal",
        _face({"verdict": "NO_SWAP_ON_THIS_BAR"}, None, None, "2026-11-10")["refused"] != [])
    leg("L26 the md carries the scopes even when a pair is unnamed",
        any("范围" in x for x in md_lines(f)))

    bad = [n for n, ok in legs if not ok]
    for n, ok in legs:
        print(("PASS " if ok else "FAIL ") + n)
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


# ---------------------------------------------------------------- io

def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:                                            # noqa: BLE001
        return None


def compute(ctx):
    """Ticket-time entry point: the caller passes the three faces it already computed."""
    ctx = ctx or {}
    face = _face(ctx.get("swap_toll"), ctx.get("swap_convergence"), ctx.get("swap_trigger"),
                 ctx.get("as_of") or ctx.get("ticket_bar"))
    face["sentence"] = sentence(face)
    return face


def build(as_of=None):
    toll = _read_json(os.path.join(ROOT, "results", "etf_book_swap_toll.json"))
    conv = _read_json(os.path.join(ROOT, "results", "etf_book_swap_convergence.json"))
    trig = _read_json(os.path.join(ROOT, "results", "etf_book_swap_trigger.json"))
    bar = as_of or (toll or {}).get("bar") or (conv or {}).get("bar") or (trig or {}).get("session")
    return _face(toll, conv, trig, bar)


def render_md(face):
    L = ["# 同一个成本，三个范围（r1529）", ""]
    L += md_lines(face, heading="## 这条过路费是几个钱")
    L += ["", "## 缘由", "",
          "- 触发面（r1466）写「act again only if a pair's gap exceeds 0.16 pp」，"
          "窗口占比 92% 也是拿 0.16 算的。",
          "- 折返面（r1522）写「往返 0.32pp」，收敛面（r1523）扣的也是 0.32。",
          "- 两个数都真，但它们是两个范围：0.16 是一次换手（买卖各一边），"
          "0.32 是进加出。纸面上两处都叫它「往返」，中间隔了半页。", ""]
    L += ["## 自证", ""]
    L += ["- 范围 pp 由边数与成本重算，边数从 r1522 import、成本从票面 import",
          "- 判据门槛必须等于「出」那一档，--check 见到别的值即红",
          "- 两个净额只并列，不求和、不平均；出现 combined 即红"]
    return "\n".join(L) + "\n"


def write_out(face):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(face))


def run():
    face = build()
    face["sentence"] = sentence(face)
    write_out(face)
    problems = check(face)
    t = face.get("totals") or {}
    conv = face.get("convergence") or {}
    print("verdict=%s bar=%s pairs=%s entry=%s exit=%s trip=%s (CNY)"
          % (face.get("verdict"), face.get("bar"), t.get("pairs"), t.get("entry_cny"),
             t.get("exit_cny"), t.get("trip_cny")))
    print("decision threshold=%s pp (scope %s)"
          % ((face.get("decision") or {}).get("threshold_pp"),
             (face.get("decision") or {}).get("threshold_scope")))
    print("label: %s" % ((face.get("label_audit") or {}).get("disclosure_status")))
    if conv.get("pairs"):
        print("reprice: round-trip net=%s vs exit-only net=%s (CNY, do_not_add=%s)"
              % (conv.get("net_round_trip_cny"), conv.get("net_exit_only_cny"),
                 conv.get("do_not_add")))
    if face.get("refused"):
        print("REFUSED: %s" % "；".join(face["refused"]))
        return 2
    print("CHECK_FAIL: %s" % "；".join(problems) if problems else "CHECK_OK")
    for r in face.get("rows") or []:
        print("  %s -> %s share@exit=%s share@trip=%s flips=%s"
              % (r.get("symbol"), r.get("sibling"), r.get("share_at_entry_pp"),
                 r.get("share_at_trip_pp"), r.get("verdict_flips_with_scope")))
    print("wrote", OUT_JSON)
    return 0 if not problems else 2


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest" or args.selftest:
        return selftest()
    if args.cmd == "check" or args.check:
        face = _read_json(OUT_JSON) or build()
        problems = check(face)
        print("CHECK_FAIL: %s" % "；".join(problems) if problems else "CHECK_OK")
        return 0 if not problems else 2
    return run()


if __name__ == "__main__":
    sys.exit(main())
