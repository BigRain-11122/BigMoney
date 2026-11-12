"""Is the money actually deployed inside the cap the same page prints above it?

Today the market clock turned RED for the first time since the guard was switched to
`enforce` on 2026-10-01 (results/market_clock/call_latest.json, days_in_state=1). Every
face that quotes a cap agrees it is 20%: the engine's own `risk_regime.position_cap`
(0.2, asof 2026-10-30, major_bear=True), the clock's `position_cap_ladder` (0.2), and the
position ladder the CEO page renders (`ceo_live_usage.LADDER`, RED -> 0.20). And yet the
six paper traders hold 4.6%..76.8% of equity.

Both statements can be true at once: the cap gates *new entries*, and the accounts were
opened before the state flipped. Nothing in the repo says so next to the numbers, so a
reader who sees "RED, cap 20%" above a 76.8% book has to guess whether the guard is
broken or the cap means something narrower. This face asks the question mechanically and
answers it in one sentence, with the gap in pp and CNY and with the sources it compared.

Rules:
  * the ladder is IMPORTED from `scripts.ceo_live_usage` (frozen v2), never re-typed;
  * a cap source that disagrees is reported as DISAGREE, never averaged;
  * an account with no equity reads as absent, never as 0% deployed;
  * the ETF book is listed in the same table but is NOT judged against this ladder --
    its own rule is a beta target x vol target (ticket caveat, r1167/r1169), and mixing
    the two would manufacture a breach.

  python scripts/regime_cap_vs_book.py run
  python scripts/regime_cap_vs_book.py --selftest

Outputs results/regime_cap_vs_book.json.
Exploratory: reads published faces, books nothing, changes no rule.
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS                                        # noqa: E402
from scripts.ceo_live_usage import LADDER                       # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PATHS.results_dir, "regime_cap_vs_book.json")
CLOCK_PTR = os.path.join(PATHS.results_dir, "market_clock", "call_latest.json")
EXPORT_PTR = os.path.join(PATHS.results_dir, "paper_export", "latest.json")
TICKET_PTR = os.path.join(PATHS.results_dir, "etf_book_order", "latest.json")
PAPER_GLOB = os.path.join(PATHS.results_dir, "paper", "*_paper.json")

# Published weights are rounded to 4dp and caps to 2dp; 20bp of slack keeps rounding
# from being read as a breach while a real 1pp overrun still fires.
CAP_TOL = 0.002


# ---------------------------------------------------------------- pure helpers
def rung_cap(state, ladder=None):
    """The cap a ladder rung carries, or None for a state the ladder does not name."""
    ladder = LADDER if ladder is None else ladder
    for name, cap, _note in ladder:
        if name == state:
            return float(cap)
    return None


def deployed_weight(positions_value, equity):
    """Share of equity that is in the market. Absent equity is None, never a 0% book."""
    try:
        eq = float(equity)
        pv = float(positions_value)
    except (TypeError, ValueError):
        return None
    if eq <= 0:
        return None
    return pv / eq


LADDER_RULE = "REGIME_GUARD v3 政体阶梯（RED 20%/ORANGE 50%/YELLOW 65%/GREEN 80%/GREEN×HOT 95%）"
ENGINE_RULE = "风配3 R-配3（跌破 MA250 且自 250 日高点回撤≥20% 才压到 20%）"


def cap_agreement(sources, ladder_cap=None, tol=CAP_TOL, ladder_rule=None):
    """Compare every cap source against the ladder. Disagreement is never averaged.

    `sources` maps a source name to a cap (float) or None when that source is missing,
    or to {"cap": float, "rule": str} when the source states which rule it encodes.
    r1583: two faces can print "position cap" and mean two *different laws* -- the
    ladder prices the market state, the paper engine prices its own dual condition
    (below MA250 AND >=20% off the 250d high).  Reading that difference as "the same
    cap counts differently" put a permanent, unactionable 矛盾 on the CEO page; a
    source that names a different rule is reported as `other_rule` and is never graded
    against this ladder, while two sources on the *same* rule that differ still are.
    """
    rows = []
    for name, val in sorted(sources.items()):
        rule = None
        cap = val
        if isinstance(val, dict):
            cap, rule = val.get("cap"), val.get("rule")
        if cap is None:
            rows.append({"source": name, "cap": None, "rule": rule, "status": "absent"})
            continue
        differs_rule = bool(rule) and bool(ladder_rule) and rule != ladder_rule
        if differs_rule:
            rows.append({"source": name, "cap": float(cap), "rule": rule,
                         "status": "other_rule"})
            continue
        ref = ladder_cap if ladder_cap is not None else cap
        status = "agrees" if abs(float(cap) - float(ref)) <= tol else "disagrees"
        rows.append({"source": name, "cap": float(cap), "rule": rule, "status": status})
    graded = [r for r in rows if r["status"] in ("agrees", "disagrees")]
    others = [r for r in rows if r["status"] == "other_rule"]
    if ladder_cap is None and not graded and not others:
        verdict = "NO_CAP_SOURCE"
    elif ladder_cap is None:
        verdict = "LADDER_SILENT_ON_THIS_STATE"
    elif any(r["status"] == "disagrees" for r in graded):
        verdict = "CAP_SOURCES_DISAGREE"
    elif not graded:
        verdict = "NO_SAME_RULE_SOURCE"
    else:
        verdict = "CAP_SOURCES_AGREE"
    return {"verdict": verdict, "ladder_cap": ladder_cap, "ladder_rule": ladder_rule,
            "n_agree": sum(1 for r in graded if r["status"] == "agrees"),
            "n_disagree": sum(1 for r in graded if r["status"] == "disagrees"),
            "n_other_rule": len(others),
            "other_rules": [{"source": r["source"], "cap": r["cap"], "rule": r["rule"]}
                            for r in others],
            "rows": rows}


def judge(rows, cap, tol=CAP_TOL):
    """Compare each account's deployed weight with the cap.

    `rows` = [{"name", "kind", "deployed_weight", "deployed_cny"}] where kind is
    "ladder" (governed by this cap) or "own_rule" (published here, judged elsewhere).
    """
    if cap is None:
        return {"verdict": "NO_CAP", "cap": None, "n_compared": 0, "n_above": 0,
                "worst": None, "rows": rows}
    judged = [r for r in rows if r.get("kind") == "ladder" and r.get("deployed_weight") is not None]
    for r in rows:
        w = r.get("deployed_weight")
        if w is None:
            r["status"] = "absent"
        elif r.get("kind") != "ladder":
            r["status"] = "own_rule"
        elif float(w) > float(cap) + tol:
            r["status"] = "above_cap"
        elif float(w) >= float(cap) - tol:
            r["status"] = "at_cap"
        else:
            r["status"] = "inside_cap"
        r["gap_pp"] = (None if w is None else round((float(w) - float(cap)) * 100.0, 2))
        r["headroom_pp"] = (None if w is None else round((float(cap) - float(w)) * 100.0, 2))
        r["multiple_of_cap"] = (None if (w is None or cap in (None, 0))
                                else round(float(w) / float(cap), 2))
    above = [r for r in judged if r["status"] == "above_cap"]
    worst = max(judged, key=lambda r: r["deployed_weight"]) if judged else None
    if not judged:
        verdict = "NOTHING_TO_COMPARE"
    elif above:
        verdict = "ABOVE_CAP"
    else:
        verdict = "INSIDE_CAP"
    return {"verdict": verdict, "cap": float(cap), "n_compared": len(judged),
            "n_above": len(above), "worst": worst, "rows": rows}


def sentence(state, cap, judged, capcheck, under_engine=None, moves=None):
    """One plain-language line: what the cap is, who is over it, and by how much.

    r1582: this sentence is printed inside two Chinese pages (CEO 一页纸 §② and
    the daily report §一), so it speaks Chinese. Numbers, account names and the
    verdict are unchanged -- only the prose language moved. The smoke leg that
    quotes the widest account recomputes them from the face, so it stays valid.
    r1583: when a second cap source encodes a *different* rule, the line says so
    instead of calling it a contradiction, and it also reports how many accounts
    sit above that looser ceiling -- a number no page printed before."""
    if cap is None:
        return ("市场状态为 %s，阶梯没有给出对应的帽子——这里没有任何读数可以当作超帽。"
                % (state or "未知"))
    head = "市场状态 %s 把新增风险的股票敞口压在上限 %.0f%%。" % (state or "未知", cap * 100)
    if capcheck.get("verdict") == "CAP_SOURCES_DISAGREE":
        bad = [r["source"] for r in capcheck["rows"] if r["status"] == "disagrees"]
        head += "（帽子来源互相矛盾：%s——这处差额按未解决读。）" % "、".join(bad)
    elif capcheck.get("other_rules"):
        seen = "、".join("%.0f%%（%s）" % (r["cap"] * 100, r["source"])
                         for r in capcheck["other_rules"])
        head += ("（账户文件里另写着 %s，那是另一条规则——%s——不是同一顶帽子的矛盾读数。）"
                 % (seen, capcheck["other_rules"][0]["rule"]))
    if judged.get("verdict") == "NOTHING_TO_COMPARE":
        return head + " 没有阶梯管辖的账户发布仓位。"
    w = judged.get("worst")
    tail = ("%d/%d 个阶梯管辖账户站在帽子上方；最高的是 %s，仓位 %.1f%%"
            "（超 %.1fpp，是帽子的 %.2f 倍）。" % (
                judged["n_above"], judged["n_compared"], w["name"],
                w["deployed_weight"] * 100.0, w["gap_pp"], w["multiple_of_cap"]))
    if judged["n_above"] == 0:
        tail = ("全部 %d 个阶梯管辖账户都在帽子以内（最宽的 %s 仓位 %.1f%%，还有 %.1fpp 空间）。" % (
            judged["n_compared"], w["name"], w["deployed_weight"] * 100.0, w["headroom_pp"]))
    out = head + " " + tail
    mv = ((moves or {}).get("accounts") or {}).get(w["name"]) if moves else None
    if mv and (mv.get("entries") or mv.get("prev_weight") is not None):
        bits = []
        if mv.get("prev_weight") is not None:
            bits.append("该户上一交易日 %.1f%%" % (mv["prev_weight"] * 100.0))
        if mv.get("entries"):
            bits.append("当日有 %d 笔新开仓（%s）"
                        % (len(mv["entries"]), "、".join(mv["entries"])))
        out += "；".join(bits) + "。"
    if judged["n_above"]:
        out += "帽子只挡新开仓，并不强制卖出。"
    if under_engine and under_engine.get("cap") is not None:
        n, tot = under_engine.get("n_above") or 0, under_engine.get("n_compared") or 0
        if n:
            w2 = under_engine.get("worst_above") or {}
            out += ("按铁律 2 的 %.0f%% 单户总仓位帽重判：还有 %d/%d 户在上方（最高 %s 仓位 %.1f%%，"
                    "超 %.1fpp）。" % (under_engine["cap"] * 100, n, tot,
                                      w2.get("name"), (w2.get("deployed_weight") or 0) * 100.0,
                                      w2.get("gap_pp") or 0))
        else:
            out += ("按铁律 2 的 %.0f%% 单户总仓位帽重判：%d 户全部在帽子以内。" % (
                under_engine["cap"] * 100, tot))
    return out


# ---------------------------------------------------------------- live wiring
def _read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def last_day_moves(day, export_dir=None):
    """What each account did on the export day, and where it stood the day before.

    r1583: the page used to explain every over-cap book with "these positions were
    built before the regime flipped" -- a cause nobody measured, and for the widest
    account it is false (it opened a NEW position on 2026-11-11). The export lane
    already carries `operations_today` and a file per trading day, so the sentence
    can quote the previous weight and that day's entries instead of asserting a
    reason. Nothing is inferred: an account with no prior export gets
    `prev_weight: None` and the words are simply left out.
    """
    export_dir = export_dir or os.path.join(PATHS.results_dir, "paper_export")
    files = sorted(glob.glob(os.path.join(export_dir, "export-*.json")))
    prev_day, prev_doc = None, None
    for f in files:
        d = os.path.basename(f)[len("export-"):-len(".json")]
        if day and d < day:
            prev_day, prev_doc = d, f
    cur = _read_json(os.path.join(export_dir, "latest.json")) or {}
    if cur.get("export_date") != day:
        cur = _read_json(os.path.join(export_dir, "export-%s.json" % day)) if day else {}
    cur = cur or {}
    prev = _read_json(prev_doc) if prev_doc else None
    prev_w = {}
    for t in (prev or {}).get("traders") or []:
        c = t.get("capital_cny") or {}
        w = deployed_weight(c.get("positions_value"), c.get("equity"))
        prev_w[t.get("trader")] = (None if w is None else round(w, 4))
    out = {}
    for t in cur.get("traders") or []:
        name = t.get("trader")
        entries = [o.get("symbol") for o in (t.get("operations_today") or [])
                   if (o.get("action") or "").lower() in ("entry", "buy", "entry_buy")]
        out[name] = {"prev_weight": prev_w.get(name), "entries": [e for e in entries if e]}
    return {"date": day, "prev_date": prev_day, "accounts": out}


def collect():
    clock = _read_json(CLOCK_PTR) or {}
    state = ((clock.get("regime_v3") or {}).get("state")) or None
    clock_asof = clock.get("asof")
    engine_asof = (clock.get("regime_v3") or {}).get("asof")
    ladder_cap = rung_cap(state)
    clock_cap = clock.get("position_cap_ladder")
    clock_cap = float(clock_cap) if isinstance(clock_cap, (int, float)) else None

    engine_caps = {}
    for f in sorted(glob.glob(PAPER_GLOB)):
        d = _read_json(f) or {}
        rr = d.get("risk_regime") or {}
        if isinstance(rr.get("position_cap"), (int, float)):
            engine_caps[os.path.basename(f)] = float(rr["position_cap"])
    engine_cap = None
    if engine_caps:
        vals = sorted(set(round(v, 4) for v in engine_caps.values()))
        engine_cap = vals[0] if len(vals) == 1 else None

    try:
        from firm.risk.regime import regime_report
        _rep = regime_report() or {}
    except Exception:                                    # engine face unreadable
        _rep = {}
    engine_detail = {"rule": ENGINE_RULE,
                     "as_of": _rep.get("as_of"),
                     "close": _rep.get("close"),
                     "ma250": _rep.get("ma250"),
                     "dd_from_250d_high": _rep.get("dd_from_250d_high"),
                     "below_ma250": _rep.get("below_ma250"),
                     "is_major_bear": _rep.get("is_major_bear"),
                     "position_cap": _rep.get("position_cap")}

    capcheck = cap_agreement({"paper_engine": {"cap": engine_cap, "rule": ENGINE_RULE},
                              "market_clock": {"cap": clock_cap, "rule": LADDER_RULE}},
                             ladder_cap, ladder_rule=LADDER_RULE)

    rows = []
    export = _read_json(EXPORT_PTR) or {}
    for t in export.get("traders") or []:
        c = t.get("capital_cny") or {}
        w = deployed_weight(c.get("positions_value"), c.get("equity"))
        rows.append({"name": t.get("trader") or "?",
                     "kind": "ladder",
                     "deployed_weight": (None if w is None else round(w, 4)),
                     "deployed_cny": c.get("positions_value"),
                     "equity_cny": c.get("equity")})

    ticket_ptr = _read_json(TICKET_PTR) or {}
    ticket = _read_json(os.path.join(PATHS.results_dir, "etf_book_order",
                                     ticket_ptr.get("file") or "")) if ticket_ptr.get("file") else None
    if ticket:
        tk = ticket.get("ticket") or {}
        bw = tk.get("book_weight")
        if isinstance(bw, (int, float)):
            rows.append({"name": "ETF-BOOK (beta x vol target, own rule)",
                         "kind": "own_rule",
                         "deployed_weight": round(float(bw), 4),
                         "deployed_cny": tk.get("book_amount"),
                         "equity_cny": tk.get("nav")})

    judged = judge(rows, ladder_cap)
    # r1583: the same accounts, judged against the ceiling their own engine enforces.
    # A copy -- judge() writes status/gap_pp onto the rows it is handed, and the ladder
    # verdict above must keep the statuses the smoke leg recomputes.
    eng_rows = [dict(r) for r in rows]
    judged_engine = judge(eng_rows, engine_cap)
    above_engine = [r for r in eng_rows
                    if r.get("kind") == "ladder" and r.get("status") == "above_cap"]
    worst_engine = (max(above_engine, key=lambda r: r["deployed_weight"])
                    if above_engine else None)
    day = export.get("export_date")
    moves = last_day_moves(day)
    under_engine = {"cap": engine_cap,
                    "n_compared": judged_engine.get("n_compared"),
                    "n_above": judged_engine.get("n_above"),
                    "worst_above": (None if worst_engine is None else {
                        "name": worst_engine["name"],
                        "deployed_weight": worst_engine["deployed_weight"],
                        "gap_pp": worst_engine["gap_pp"]})}
    return {
        "evidence_cutoff": clock.get("asof") or export.get("export_date"),
        "clock": {"cell": clock.get("clock_cell"), "asof": clock_asof,
                  "regime_state": state, "regime_asof": engine_asof,
                  "days_in_state": (clock.get("regime_v3") or {}).get("days_in_state")},
        "ladder_cap": ladder_cap,
        "ladder_rule": LADDER_RULE,
        "engine": engine_detail,
        "cap_sources": capcheck,
        "accounts": sorted(judged["rows"], key=lambda r: -(r.get("deployed_weight") or -1)),
        "under_engine": dict(under_engine, rule=ENGINE_RULE,
                             verdict=judged_engine.get("verdict")),
        "last_day_moves": moves,
        "verdict": {"cap": capcheck["verdict"], "book": judged["verdict"],
                    "n_compared": judged["n_compared"], "n_above": judged["n_above"]},
        "sentence": sentence(state, ladder_cap, judged, capcheck,
                             under_engine=under_engine, moves=moves),
        "engine_caps_seen": engine_caps,
    }


def run():
    face = collect()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    print(face["sentence"])
    print("cap=%s | book=%s | wrote %s" % (face["verdict"]["cap"], face["verdict"]["book"], OUT))
    return 0


def read_published(path=None):
    """The verdict as published, for pages that must quote it rather than re-read it.

    Single implementation (r1290): the CEO one-pager (sec.2 prints the cap) and the
    daily report (sec.1 prints the cap) both call this, so the number they print and
    the number the artifact judges can never drift apart.  A missing or unreadable
    artifact reads as absent -- never as "inside the cap", which is the failure the
    whole face exists to prevent.  `widest_above` only ever names a ladder-governed
    account: an own-rule book (the ETF beta x vol target) is never a breach number.
    """
    face = _read_json(OUT if path is None else path)
    if not isinstance(face, dict) or not face.get("sentence"):
        return {"status": "absent"}
    verdict = face.get("verdict") or {}
    ladder_rows = [r for r in (face.get("accounts") or [])
                   if r.get("kind") == "ladder" and r.get("deployed_weight") is not None]
    above = [r for r in ladder_rows if r.get("status") == "above_cap"]
    widest = max(above, key=lambda r: r["deployed_weight"]) if above else None
    clock = face.get("clock") or {}
    return {
        "status": "ok",
        "source": "results/regime_cap_vs_book.json",
        "sentence": face["sentence"],
        "cap": face.get("ladder_cap"),
        "cap_verdict": verdict.get("cap"),
        "book_verdict": verdict.get("book"),
        "n_compared": verdict.get("n_compared"),
        "n_above": verdict.get("n_above"),
        "widest_above": (None if widest is None else {
            "name": widest.get("name"),
            "deployed_weight": widest.get("deployed_weight"),
            "gap_pp": widest.get("gap_pp"),
            "multiple_of_cap": widest.get("multiple_of_cap")}),
        "state": clock.get("regime_state"),
        "priced_on": clock.get("regime_asof"),
    }


# ---------------------------------------------------------------- selftest
def _selftest():
    ok = 0

    def chk(name, cond):
        nonlocal ok
        if not cond:
            raise AssertionError("FAIL: " + name)
        ok += 1
        print("[%2d] %s" % (ok, name))

    ladder = [("RED", 0.20, "red"), ("GREEN", 0.80, "green")]
    chk("ladder is the frozen v2 table, not a local copy (RED 20% / GREEN 80%)",
        rung_cap("RED", ladder) == 0.20 and rung_cap("GREEN", ladder) == 0.80)
    chk("a state the ladder does not name has no cap", rung_cap("PURPLE", ladder) is None)
    chk("the shipped ladder agrees with this file's RED reading",
        rung_cap("RED") == 0.20 and rung_cap("ORANGE") == 0.50)

    chk("deployed weight is positions/equity",
        abs(deployed_weight(758482.35, 987555.99) - 0.76803985) < 1e-7)
    chk("zero or absent equity reads as None, not a 0% book",
        deployed_weight(10, 0) is None and deployed_weight(None, 100) is None)

    src = {"a": 0.20, "b": 0.20, "c": None}
    r = cap_agreement(src, 0.20)
    chk("three sources, two equal -> AGREE and the missing one is marked absent",
        r["verdict"] == "CAP_SOURCES_AGREE" and r["n_agree"] == 2
        and [x["status"] for x in r["rows"] if x["source"] == "c"] == ["absent"])
    r = cap_agreement({"a": 0.20, "b": 0.50}, 0.20)
    chk("a disagreeing source is named, never averaged", r["verdict"] == "CAP_SOURCES_DISAGREE"
        and [x["source"] for x in r["rows"] if x["status"] == "disagrees"] == ["b"])
    chk("no ladder cap for this state -> LADDER_SILENT, not agreement",
        cap_agreement({"a": 0.20}, None)["verdict"] == "LADDER_SILENT_ON_THIS_STATE")

    # r1583: two caps, two laws. A source that names a different rule is not a
    # contradiction of this one; a source on the SAME rule that differs still is.
    r = cap_agreement({"ladder": {"cap": 0.20, "rule": LADDER_RULE},
                       "engine": {"cap": 0.80, "rule": ENGINE_RULE}},
                      0.20, ladder_rule=LADDER_RULE)
    chk("a source on another rule is named as other_rule, not as a contradiction",
        r["verdict"] == "CAP_SOURCES_AGREE" and r["n_other_rule"] == 1
        and r["n_disagree"] == 0
        and [x["status"] for x in r["rows"] if x["source"] == "engine"] == ["other_rule"]
        and r["other_rules"][0]["cap"] == 0.80)
    r = cap_agreement({"ladder": {"cap": 0.50, "rule": LADDER_RULE},
                       "engine": {"cap": 0.80, "rule": ENGINE_RULE}},
                      0.20, ladder_rule=LADDER_RULE)
    chk("a real disagreement on the same rule still wins over an other-rule source",
        r["verdict"] == "CAP_SOURCES_DISAGREE" and r["n_other_rule"] == 1)
    chk("nothing on this ladder's own rule -> NO_SAME_RULE_SOURCE, never 'agrees'",
        cap_agreement({"engine": {"cap": 0.80, "rule": ENGINE_RULE}},
                      0.20, ladder_rule=LADDER_RULE)["verdict"] == "NO_SAME_RULE_SOURCE")

    rows = [{"name": "WIDE", "kind": "ladder", "deployed_weight": 0.862},
            {"name": "OK", "kind": "ladder", "deployed_weight": 0.50}]
    j_lad = judge([dict(x) for x in rows], 0.20)
    j_eng = judge([dict(x) for x in rows], 0.80)
    chk("the same book judged on two ceilings: 2/2 over the ladder, 1/2 over the engine's",
        j_lad["n_above"] == 2 and j_eng["n_above"] == 1
        and j_eng["worst"]["name"] == "WIDE" and j_eng["worst"]["gap_pp"] == 6.2)
    chk("the second judgment does not overwrite the first (rows are copied)",
        j_lad["rows"][0]["status"] == "above_cap"
        and j_lad["rows"][0]["gap_pp"] == 66.2)

    rows = [{"name": "A", "kind": "ladder", "deployed_weight": 0.10},
            {"name": "B", "kind": "ladder", "deployed_weight": 0.201}]
    j = judge(rows, 0.20)
    chk("everyone inside -> INSIDE_CAP with headroom in pp",
        j["verdict"] == "INSIDE_CAP" and j["rows"][0]["headroom_pp"] == 10.0)
    chk("rounding slack (20.1% vs 20%) is at_cap, not a breach",
        j["rows"][1]["status"] == "at_cap")

    rows = [{"name": "WIDE", "kind": "ladder", "deployed_weight": 0.7682},
            {"name": "ETF", "kind": "own_rule", "deployed_weight": 0.4715}]
    j = judge(rows, 0.20)
    chk("a book above the cap names the widest account and the multiple",
        j["verdict"] == "ABOVE_CAP" and j["worst"]["name"] == "WIDE"
        and j["rows"][0]["multiple_of_cap"] == 3.84 and j["rows"][0]["gap_pp"] == 56.82)
    chk("an account governed by its own rule is never counted as a breach",
        j["n_above"] == 1 and j["rows"][1]["status"] == "own_rule")
    chk("no ladder-governed account -> NOTHING_TO_COMPARE, never 'inside'",
        judge([{"name": "ETF", "kind": "own_rule", "deployed_weight": 0.5}], 0.2)["verdict"]
        == "NOTHING_TO_COMPARE")
    chk("no cap -> NO_CAP and nothing is graded",
        judge([{"name": "A", "kind": "ladder", "deployed_weight": 0.3}], None)["verdict"] == "NO_CAP")

    s = sentence("RED", 0.20, j, cap_agreement({"a": 0.2}, 0.2))
    chk("the sentence carries the state, the cap, the widest account and the multiple",
        "RED" in s and "20%" in s and "WIDE" in s and "3.84 倍" in s)
    chk("a disagreeing cap source is stated in the sentence",
        "矛盾" in sentence("RED", 0.2, j, cap_agreement({"a": 0.5}, 0.2)))
    chk("another rule is explained, not called a contradiction (r1583)",
        "帽子来源互相矛盾" not in sentence("RED", 0.2, j,
                                     cap_agreement({"e": {"cap": 0.8, "rule": ENGINE_RULE}},
                                                   0.2, ladder_rule=LADDER_RULE))
        and "另一条规则" in sentence("RED", 0.2, j,
                                 cap_agreement({"e": {"cap": 0.8, "rule": ENGINE_RULE}},
                                               0.2, ladder_rule=LADDER_RULE)))
    s2 = sentence("RED", 0.2, j, cap_agreement({"a": 0.2}, 0.2),
                  under_engine={"cap": 0.80, "n_compared": 2, "n_above": 1,
                                "worst_above": {"name": "WIDE", "deployed_weight": 0.862,
                                                "gap_pp": 6.2}})
    chk("the second ceiling is reported in the same sentence with its own count",
        "80%" in s2 and "1/2 户在上方" in s2 and "6.2pp" in s2)
    chk("everyone inside the second ceiling says so instead of printing 0/2",
        "全部在帽子以内" in sentence("RED", 0.2, j, cap_agreement({"a": 0.2}, 0.2),
                                 under_engine={"cap": 0.80, "n_compared": 2, "n_above": 0}))
    chk("no ladder cap -> the sentence refuses to read a breach",
        "没有任何读数可以当作超帽" in sentence("PURPLE", None, j, {"verdict": "NO_CAP_SOURCE"}))
    chk("the sentence speaks Chinese, not English, on the two Chinese pages (r1582)",
        all(ord(ch) < 128 or ch in "，。（）：；、" or "\u4e00" <= ch <= "\u9fff"
            for ch in sentence("RED", 0.2, j, cap_agreement({"a": 0.2}, 0.2)))
        and "the widest is" not in sentence("RED", 0.2, j, cap_agreement({"a": 0.2}, 0.2)))

    # --- the over-cap book's own history, read not assumed (r1583)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        def _exp(day, w, ops):
            doc = {"export_date": day, "traders": [
                {"trader": "A", "capital_cny": {"positions_value": w, "equity": 1.0},
                 "operations_today": ops}]}
            with open(os.path.join(td, "export-%s.json" % day), "w", encoding="utf-8") as fh:
                json.dump(doc, fh)
        _exp("2026-11-10", 0.6691, [])
        _exp("2026-11-11", 0.8616, [{"action": "entry", "symbol": "513500"},
                                    {"action": "exit", "symbol": "511010"}])
        mv = last_day_moves("2026-11-11", td)
        chk("the previous export gives the weight, and only ENTRYs are quoted",
            mv["prev_date"] == "2026-11-10"
            and mv["accounts"]["A"]["prev_weight"] == 0.6691
            and mv["accounts"]["A"]["entries"] == ["513500"])
        chk("no prior export -> prev_weight None, nothing invented",
            last_day_moves("2026-11-10", td)["accounts"]["A"]["prev_weight"] is None)
    s3 = sentence("RED", 0.20, j, cap_agreement({"a": 0.2}, 0.2), moves={
        "accounts": {"WIDE": {"prev_weight": 0.6691, "entries": ["513500"]}}})
    chk("the sentence quotes the measured move instead of asserting a cause",
        "上一交易日 66.9%" in s3 and "513500" in s3
        and "政体翻转之前建的" not in s3)

    # --- reader face: pages quote the published verdict, they do not re-read it
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "face.json")
        chk("a missing artifact reads absent, never 'inside the cap'",
            read_published(p)["status"] == "absent")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"verdict": {"cap": "CAP_SOURCES_AGREE", "book": "ABOVE_CAP",
                                   "n_compared": 6, "n_above": 2},
                       "clock": {"regime_state": "RED", "regime_asof": "2026-10-30"},
                       "ladder_cap": 0.20,
                       "accounts": [
                           {"name": "SMALL", "kind": "ladder", "status": "above_cap",
                            "deployed_weight": 0.25, "gap_pp": 5.0, "multiple_of_cap": 1.25},
                           {"name": "WIDE", "kind": "ladder", "status": "above_cap",
                            "deployed_weight": 0.60, "gap_pp": 40.0, "multiple_of_cap": 3.0},
                           {"name": "BOOK", "kind": "own_rule", "status": "own_rule",
                            "deployed_weight": 0.90, "gap_pp": 70.0, "multiple_of_cap": 4.5},
                           {"name": "FLAT", "kind": "ladder", "status": "inside_cap",
                            "deployed_weight": 0.04, "gap_pp": -16.0, "multiple_of_cap": 0.2}],
                       "sentence": "quoted verbatim"}, fh)
        rp = read_published(p)
        chk("the reader quotes the sentence and the verdict verbatim",
            rp["status"] == "ok" and rp["sentence"] == "quoted verbatim"
            and rp["book_verdict"] == "ABOVE_CAP" and rp["n_above"] == 2
            and rp["cap"] == 0.20)
        chk("widest_above is the widest LADDER account over the cap, never an own-rule book",
            rp["widest_above"]["name"] == "WIDE"
            and rp["widest_above"]["deployed_weight"] == 0.60)

    print("selftest %d/%d PASS" % (ok, ok))
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv[1:])
    if a.selftest or a.cmd == "selftest":
        return _selftest()
    if a.cmd in ("run", ""):
        return run()
    ap.error("unknown command: %s" % a.cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv))