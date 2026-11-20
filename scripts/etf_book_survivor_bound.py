"""ETF book -- can survivorship be blamed for the 2015 refusal?

r1871 measured a capacity line in every year; r1872 re-priced it on the whole roster and
found the market got WIDER as well as deeper. Both faces read a panel swept from the ETF
list that exists TODAY, so a reader is entitled to one question before quoting either
number: **is the early "not enough depth" verdict an artifact of names that died?**

This face answers it in CNY of turnover, using the book's own capacity algebra
(`cap = line * slots * adv_worst`), with the criterion frozen in `CRITERIA` below:

  * `census`  -- how many panel files actually have a dead tail. A panel with ~0 deaths is
    a survivors sweep, and its early roster is an undercount; this prints that number
    instead of asserting it.
  * `anchor`  -- for each r1871 anchor: names readable, total ADV, the fifth-deepest ADV
    (the one that binds), the capital the visible roster supports, and the ADV a name
    needs to carry one slot of the gate's own lens at the line.
  * the criterion -- when the visible roster cannot fill five slots at the line, the
    missing depth has to come from names that are NOT in the panel at all. A single fund
    can be at most as large as the turnover of everything else we see, so:
      need <= visible total  -> SURVIVORSHIP_COULD_SAVE_IT   (do not quote the refusal)
      need >  visible total  -> SURVIVORSHIP_CANNOT_SAVE_IT  (refusal survives any roster)

Usage:
    python scripts/etf_book_survivor_bound.py run
    python scripts/etf_book_survivor_bound.py check
    python scripts/etf_book_survivor_bound.py selftest
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import etf_book_era_capacity as EC  # noqa: E402
import etf_book_era_grid as EG  # noqa: E402
import etf_book_era_roster as ER  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_survivor_bound.json")
DATA_DIR = os.path.join(ROOT, "data", "daily")

SLOTS = 5
ALIVE_CUT = "2026-10-01"     # a tail before this is a dead name


# ------------------------------------------------------------------ panel census

def panel_census(data_dir=None, alive_cut=ALIVE_CUT):
    """Head and tail of every panel csv: which names died, and when they were born."""
    data_dir = data_dir or DATA_DIR
    rows = []
    for p in sorted(glob.glob(os.path.join(data_dir, "*.csv"))):
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.read().strip().splitlines()
        except OSError:
            continue
        if len(lines) < 2:
            continue
        rows.append((os.path.basename(p)[:-4], lines[1].split(",")[0][:10],
                     lines[-1].split(",")[0][:10]))
    dead = [r for r in rows if r[2] < alive_cut]
    return {"files": len(rows), "rows": rows, "dead": dead,
            "dead_share": (len(dead) / len(rows)) if rows else None,
            "alive_cut": alive_cut}


def census_at(rows, anchor, alive_cut=ALIVE_CUT):
    """Names born by `anchor` and, of those, how many are still trading today."""
    born = [r for r in rows if r[1] <= anchor]
    alive = [r for r in born if r[2] >= alive_cut]
    return {"anchor": anchor, "born_by_anchor": len(born),
            "of_those_still_alive": len(alive),
            "of_those_dead_since": len(born) - len(alive),
            "dead_names": [r[0] for r in born if r[2] < alive_cut]}


# ------------------------------------------------------------------ arithmetic

def anchor_bound(roster, line, per_name_cny, slots=SLOTS):
    """Depth arithmetic for one anchor, in the book's own capacity algebra."""
    advs = sorted(roster.values(), reverse=True)
    need = (float(per_name_cny) / float(line)) if (line and per_name_cny is not None) else None
    lens = (float(per_name_cny) * slots) if per_name_cny is not None else None
    adv5 = advs[slots - 1] if len(advs) >= slots else None
    total = float(sum(advs)) if advs else 0.0
    cap_visible = (float(line) * slots * adv5) if (adv5 is not None and line) else None
    clearing = [a for a in advs if need is not None and a >= need]
    return {
        "n_names": len(advs),
        "adv_total_cny": total,
        "lens_cny": lens,
        "need_adv_per_name_cny": need,
        "n_names_clearing": len(clearing),
        "adv5_cny": adv5,
        "deepest_adv_cny": advs[0] if advs else None,
        "cap_visible_cny": cap_visible,
        "shortfall_cny": ((max(0.0, lens - cap_visible)
                           if (cap_visible is not None and lens is not None) else None)),
        "need_multiple_of_adv5": ((need / adv5) if (need and adv5) else None),
        "need_over_visible_total": ((need / total) if (need and total > 0) else None),
        "top5_sum_cny": float(sum(advs[:slots])),
        "top5_share_of_total": ((float(sum(advs[:slots])) / total) if total > 0 else None),
    }


def bound_verdict(row):
    """One anchor -> which way survivorship can move it (criterion frozen above)."""
    if row.get("need_adv_per_name_cny") is None:
        return "NO_RULER"
    if row.get("n_names_clearing", 0) >= SLOTS:
        return "ENOUGH_DEPTH_VISIBLE"
    if not row.get("adv_total_cny"):
        return "NO_ROSTER"
    if row["need_adv_per_name_cny"] <= row["adv_total_cny"]:
        return "SURVIVORSHIP_COULD_SAVE_IT"
    return "SURVIVORSHIP_CANNOT_SAVE_IT"


WHY = {
    "ENOUGH_DEPTH_VISIBLE":
        "five readable names already carry a slot at the line -- the dead cannot change it",
    "SURVIVORSHIP_CANNOT_SAVE_IT":
        "the depth one slot needs exceeds every visible name's turnover combined, so no "
        "plausible vanished roster supplies it",
    "SURVIVORSHIP_COULD_SAVE_IT":
        "a vanished fund no bigger than the visible market could supply the depth -- the "
        "refusal is NOT robust and must not be quoted as a fact about that year",
    "NO_ROSTER": "no readable roster at that anchor",
    "NO_RULER": "the gate face carries no line or lens",
}


def verdict_payload(rows):
    first = rows[0] if rows else None
    if first is None:
        return {"verdict": "NO_ANCHORS"}
    v = bound_verdict(first)
    cap = first.get("score_k5_cap_cny")
    lens = first.get("lens_cny")
    if v == "ENOUGH_DEPTH_VISIBLE" and cap is not None and lens is not None:
        if cap < lens:
            reading = ("the market's depth was never the constraint at %s (%d names clear "
                       "one slot at the line); the score's own five only carried %.0f of "
                       "the %.0f the book wanted -- that is a RANKING problem, and no dead "
                       "name can fix a ranking" % (first["anchor"],
                                                   first["n_names_clearing"], cap, lens))
        else:
            reading = ("at %s both the market and the score's picks supported the lens"
                       % first["anchor"])
    else:
        reading = WHY.get(v, "")
    return {"verdict": v, "anchor": first["anchor"], "reading": reading,
            "need_adv_per_name_cny": first["need_adv_per_name_cny"],
            "visible_total_cny": first["adv_total_cny"],
            "n_names_clearing": first["n_names_clearing"],
            "score_k5_cap_cny": cap, "lens_cny": lens,
            "need_multiple_of_adv5": first["need_multiple_of_adv5"],
            "shortfall_cny": first["shortfall_cny"], "why": WHY.get(v, "")}


# ------------------------------------------------------------------ run

def measure(amt, sc, anchor, line, per_name_cny):
    adv_panel = ER.adv_at_anchors(amt, [anchor])
    last_pos = ER.last_valid_positions(amt)
    pos = {str(pd.Timestamp(d).date()): i for i, d in enumerate(amt.index)}
    roster = ER.roster_at(adv_panel, anchor, pos, last_pos)
    row = anchor_bound(roster, line, per_name_cny)
    row["anchor"] = anchor
    row["verdict"] = bound_verdict(row)
    row["deepest5"] = [[s, round(v, 2)] for s, v in ER.depth_picks(roster, SLOTS)]
    # the same anchor through r1871/r1872's own lens, so the reader can see whether the
    # constraint was the market's depth or the score's picks
    try:
        import statistics  # noqa: F401  (ER keeps the baseline in its own module)
        prior = ER.measure_anchor(adv_panel, last_pos, pos, sc, anchor, line, per_name_cny)
        row["score_k5_cap_cny"] = prior.get("cap_score_k5_cny")
        row["score_picks"] = prior.get("score_picks") or []
        row["n_slots_at_budget"] = prior.get("n_slots_at_budget")
    except Exception as exc:                      # never let the cross-check eat the face
        row["score_k5_cap_cny"] = None
        row["cross_check_error"] = "%s: %s" % (type(exc).__name__, exc)
    return row


def run() -> int:
    t0 = time.time()
    face = EC.load_gate()
    rituals = EC.rulers(face)
    if rituals["line_frac"] is None or rituals["lens_cny"] is None:
        print("gate face carries no usable ruler: line=%r lens=%r"
              % (rituals["line_pct"], rituals["lens_cny"]), flush=True)
        return 2
    line = rituals["line_frac"]
    per_name = float(rituals["lens_cny"]) / SLOTS

    _close, _openp, amt, sc, _n = S.nobond_universe()
    census = panel_census()
    anchors = [str(pd.Timestamp(a["first_bar"]).date()) for a in EG.year_anchors(sc.index)]
    anchors.append(str(pd.Timestamp(sc.index[-1]).date()))

    rows = []
    for a in anchors:
        r = measure(amt, sc, a, line, per_name)
        r["census"] = census_at(census["rows"], a)
        rows.append(r)
        print("  %s  names=%d adv_total=%s adv5=%s need=%s clearing=%d score_k5=%s -> %s"
              % (a, r["n_names"], _money(r["adv_total_cny"]), _money(r["adv5_cny"]),
                 _money(r["need_adv_per_name_cny"]), r["n_names_clearing"],
                 _money(r.get("score_k5_cap_cny")), r["verdict"]),
              flush=True)

    payload = {
        "face": "etf_book_survivor_bound",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": anchors[-1],
        "criteria": {"line_pct": rituals["line_pct"], "line_frac": line,
                     "lens_cny": rituals["lens_cny"], "lens_label": rituals["lens"],
                     "slots": SLOTS, "per_name_cny": per_name,
                     "alive_cut": census["alive_cut"],
                     "criterion": "need <= visible total ADV => the dead could have "
                                  "supplied the depth; else they could not"},
        "panel_census": {"files": census["files"],
                         "dead_files": [list(d) for d in census["dead"]],
                         "dead_share": census["dead_share"]},
        "anchors": rows,
        "verdict": verdict_payload(rows),
        "honest": [
            "the panel is a survivors sweep: %.2f%% of its files have a dead tail, so the "
            "roster at every early anchor is an UNDERCOUNT and its breadth is a floor"
            % (100.0 * (census["dead_share"] or 0.0)),
            "a name absent from the panel could never be ranked by the score, so "
            "survivorship can move the ceiling (depth), never the picks",
            "the criterion is sufficiency, not evidence: it says whether a vanished name "
            "COULD have supplied the depth, never that one existed",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("wrote %s  verdict=%s" % (os.path.relpath(OUT_JSON, ROOT),
                                    payload["verdict"]["verdict"]), flush=True)
    return 0


def _money(v):
    if v is None:
        return "-"
    if abs(v) >= 1e8:
        return "%.2f亿" % (v / 1e8)
    if abs(v) >= 1e4:
        return "%.1f万" % (v / 1e4)
    return "%.0f" % v


# ------------------------------------------------------------------ check

def check(payload=None):
    """Re-derive every anchor's verdict and arithmetic from its own published numbers."""
    problems = []
    if payload is None:
        with open(OUT_JSON, "r", encoding="utf-8") as f:
            payload = json.load(f)
    rows = payload.get("anchors") or []
    if not rows:
        problems.append("no anchors")
    for r in rows:
        again = bound_verdict(r)
        if again != r.get("verdict"):
            problems.append("%s: verdict %r re-derives as %r"
                            % (r.get("anchor"), r.get("verdict"), again))
        cap, lens = r.get("cap_visible_cny"), r.get("lens_cny")
        if cap is not None and lens is not None and r.get("shortfall_cny") is not None:
            want = max(0.0, lens - cap)
            if abs(want - r["shortfall_cny"]) > max(1.0, 1e-9 * max(1.0, lens)):
                problems.append("%s: shortfall %.4f != re-derived %.4f"
                                % (r.get("anchor"), r["shortfall_cny"], want))
        need, total = r.get("need_adv_per_name_cny"), r.get("adv_total_cny")
        if need and total and r.get("need_over_visible_total") is not None:
            if abs(need / total - r["need_over_visible_total"]) > 1e-9:
                problems.append("%s: need/total mismatch" % r.get("anchor"))
    vp = payload.get("verdict") or {}
    if rows and bound_verdict(rows[0]) != vp.get("verdict"):
        problems.append("headline verdict disagrees with the first anchor")
    if rows and vp.get("anchor") != rows[0].get("anchor"):
        problems.append("headline names a different anchor")
    ok = not problems
    print(json.dumps({"ok": ok, "problems": problems, "verdict": vp.get("verdict")},
                     ensure_ascii=False))
    return 0 if ok else 3


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    checks = []

    def leg(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    line, per = 0.01, 200_000.0
    need = per / line                                     # 20,000,000
    lens = per * SLOTS                                    # 1,000,000

    leg("L1 need = per_name/line", abs(need - 20_000_000.0) < 1e-9, "%.0f" % need)

    # L2 five names clear -> the dead cannot matter
    r = anchor_bound({"a": 30e6, "b": 25e6, "c": 22e6, "d": 21e6, "e": 20.5e6}, line, per)
    leg("L2 five clearing -> ENOUGH_DEPTH_VISIBLE",
        r["n_names_clearing"] == 5 and bound_verdict(r) == "ENOUGH_DEPTH_VISIBLE",
        bound_verdict(r))

    # L3 four clear inside a market far bigger than one slot -> the dead could supply it
    r = anchor_bound({"a": 30e6, "b": 25e6, "c": 22e6, "d": 21e6, "e": 9e6}, line, per)
    leg("L3 adv5 = 9M, need multiple 2.22x",
        abs(r["adv5_cny"] - 9e6) < 1e-6 and abs(r["need_multiple_of_adv5"] - need / 9e6) < 1e-9,
        "%.4f" % r["need_multiple_of_adv5"])
    leg("L3b need 20M <= visible 107M -> COULD",
        bound_verdict(r) == "SURVIVORSHIP_COULD_SAVE_IT", bound_verdict(r))
    leg("L3c shortfall = lens - line*5*adv5",
        abs(r["shortfall_cny"] - (lens - line * 5 * 9e6)) < 1e-6,
        "%.2f" % r["shortfall_cny"])

    # L4 a market where one slot is bigger than the whole visible roster -> cannot
    r = anchor_bound({"a": 2e6, "b": 1.5e6, "c": 1e6, "d": 0.8e6, "e": 0.7e6}, line, per)
    leg("L4 need 20M > visible 6M -> CANNOT",
        bound_verdict(r) == "SURVIVORSHIP_CANNOT_SAVE_IT", bound_verdict(r))
    leg("L4b cap_visible uses the fifth name, not the deepest",
        abs(r["cap_visible_cny"] - line * 5 * 0.7e6) < 1e-6, "%.0f" % r["cap_visible_cny"])

    # L5 empty roster never divides by zero and never claims a verdict
    r = anchor_bound({}, line, per)
    leg("L5 empty roster -> NO_ROSTER", bound_verdict(r) == "NO_ROSTER", bound_verdict(r))

    # L6 no ruler -> no verdict
    leg("L6 no line -> NO_RULER",
        bound_verdict(anchor_bound({"a": 1e6}, None, None)) == "NO_RULER")

    # L7 census counts a dead name by its tail, and by birth at the anchors
    rows = [("x", "2012-01-04", "2019-06-30"), ("y", "2010-01-04", "2026-11-19")]
    c = census_at(rows, "2015-01-05", alive_cut=ALIVE_CUT)
    leg("L7 dead name born before the anchor is counted dead",
        c["born_by_anchor"] == 2 and c["of_those_still_alive"] == 1
        and c["dead_names"] == ["x"], json.dumps(c, ensure_ascii=False))
    leg("L7b a name born after the anchor is not in the born set",
        census_at(rows, "2009-01-05")["born_by_anchor"] == 0)

    # L8 the verdict is read from the FIRST anchor, not from whichever looks best
    good = {"anchor": "2025-01-02", "n_names_clearing": 9, "need_adv_per_name_cny": need,
            "adv_total_cny": 1e9, "adv5_cny": 90e6, "lens_cny": lens,
            "cap_visible_cny": line * 5 * 90e6, "shortfall_cny": 0.0,
            "need_multiple_of_adv5": need / 90e6, "need_over_visible_total": need / 1e9}
    bad = {"anchor": "2015-01-05", "n_names_clearing": 0, "need_adv_per_name_cny": need,
           "adv_total_cny": 6e6, "adv5_cny": 0.7e6, "lens_cny": lens,
           "cap_visible_cny": line * 5 * 0.7e6,
           "shortfall_cny": lens - line * 5 * 0.7e6,
           "need_multiple_of_adv5": need / 0.7e6, "need_over_visible_total": need / 6e6}
    vp = verdict_payload([bad, good])
    leg("L8 headline reads the first anchor", vp["anchor"] == "2015-01-05"
        and vp["verdict"] == "SURVIVORSHIP_CANNOT_SAVE_IT", vp["verdict"])

    # L9 check() catches a tampered shortfall
    import contextlib
    import io as _io
    payload = {"anchors": [dict(bad)], "verdict": vp}
    payload["anchors"][0]["shortfall_cny"] = 1.0
    buf = _io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check(payload)
    leg("L9 check() rejects a tampered shortfall", rc == 3 and "shortfall" in buf.getvalue(),
        buf.getvalue()[:90])

    bad_n = sum(1 for _n, ok, _d in checks if not ok)
    for n, ok, d in checks:
        print(("  ok   " if ok else "  FAIL ") + n + (("  [" + d + "]") if d and not ok else ""))
    print("survivor_bound selftest %d/%d PASS" % (len(checks) - bad_n, len(checks)))
    return 0 if bad_n == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest"))
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
