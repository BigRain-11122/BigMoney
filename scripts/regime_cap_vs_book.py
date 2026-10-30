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


def cap_agreement(sources, ladder_cap=None, tol=CAP_TOL):
    """Compare every cap source against the ladder. Disagreement is never averaged.

    `sources` maps a source name to a cap (float) or None when that source is missing.
    """
    rows = []
    for name, cap in sorted(sources.items()):
        if cap is None:
            rows.append({"source": name, "cap": None, "status": "absent"})
            continue
        ref = ladder_cap if ladder_cap is not None else cap
        status = "agrees" if abs(float(cap) - float(ref)) <= tol else "disagrees"
        rows.append({"source": name, "cap": float(cap), "status": status})
    graded = [r for r in rows if r["status"] != "absent"]
    if ladder_cap is None and not graded:
        verdict = "NO_CAP_SOURCE"
    elif ladder_cap is None:
        verdict = "LADDER_SILENT_ON_THIS_STATE"
    elif any(r["status"] == "disagrees" for r in graded):
        verdict = "CAP_SOURCES_DISAGREE"
    elif not graded:
        verdict = "NO_CAP_SOURCE"
    else:
        verdict = "CAP_SOURCES_AGREE"
    return {"verdict": verdict, "ladder_cap": ladder_cap,
            "n_agree": sum(1 for r in graded if r["status"] == "agrees"),
            "n_disagree": sum(1 for r in graded if r["status"] == "disagrees"),
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


def sentence(state, cap, judged, capcheck):
    """One plain-language line: what the cap is, who is over it, and by how much."""
    if cap is None:
        return ("The market state is %s and the ladder names no cap for it -- nothing here "
                "can be read as a breach." % (state or "unknown"))
    head = "Market state %s caps new risk at %.0f%% of equity." % (state or "unknown", cap * 100)
    if capcheck.get("verdict") == "CAP_SOURCES_DISAGREE":
        bad = [r["source"] for r in capcheck["rows"] if r["status"] == "disagrees"]
        head += " The cap sources disagree (%s) -- read the gap as unresolved." % ", ".join(bad)
    if judged.get("verdict") == "NOTHING_TO_COMPARE":
        return head + " No ladder-governed account published a weight."
    w = judged.get("worst")
    tail = "%d of %d ladder-governed accounts sit above it; the widest is %s at %.1f%% (%.1fpp over, %.2fx the cap)." % (
        judged["n_above"], judged["n_compared"], w["name"],
        w["deployed_weight"] * 100.0, w["gap_pp"], w["multiple_of_cap"])
    if judged["n_above"] == 0:
        tail = "all %d ladder-governed accounts sit inside it (widest %s at %.1f%%, %.1fpp of room)." % (
            judged["n_compared"], w["name"], w["deployed_weight"] * 100.0, w["headroom_pp"])
    return head + " " + tail + (" Those positions predate the state flip, so the cap gates "
                                "new entries rather than forcing a sale." if judged["n_above"] else "")


# ---------------------------------------------------------------- live wiring
def _read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


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

    capcheck = cap_agreement({"paper_engine": engine_cap, "market_clock": clock_cap}, ladder_cap)

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
    return {
        "evidence_cutoff": clock.get("asof") or export.get("export_date"),
        "clock": {"cell": clock.get("clock_cell"), "asof": clock_asof,
                  "regime_state": state, "regime_asof": engine_asof,
                  "days_in_state": (clock.get("regime_v3") or {}).get("days_in_state")},
        "ladder_cap": ladder_cap,
        "cap_sources": capcheck,
        "accounts": sorted(judged["rows"], key=lambda r: -(r.get("deployed_weight") or -1)),
        "verdict": {"cap": capcheck["verdict"], "book": judged["verdict"],
                    "n_compared": judged["n_compared"], "n_above": judged["n_above"]},
        "sentence": sentence(state, ladder_cap, judged, capcheck),
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
        "RED" in s and "20%" in s and "WIDE" in s and "3.84x" in s)
    chk("a disagreeing cap source is stated in the sentence",
        "disagree" in sentence("RED", 0.2, j, cap_agreement({"a": 0.5}, 0.2)))
    chk("no ladder cap -> the sentence refuses to read a breach",
        "nothing here can be read as a breach" in sentence("PURPLE", None, j, {"verdict": "NO_CAP_SOURCE"}))

    # --- reader face: pages quote the published verdict, they do not re-read it
    import tempfile
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